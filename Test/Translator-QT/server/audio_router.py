import webrtcvad
import numpy as np
import os
import time
import threading
import queue
import json
import struct
import resampy
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
import asyncio
from pydub import AudioSegment
from pydub.effects import low_pass_filter
import whisper

app = FastAPI()
router = APIRouter()

SAMPLE_RATE = 16000
WS_SAMPLE_RATE = 48000
CHANNELS = 2
BYTES_PER_SAMPLE = 2
FRAME_DURATION = 20
FRAME_BYTES = int(WS_SAMPLE_RATE * FRAME_DURATION / 1000) * CHANNELS * BYTES_PER_SAMPLE
PING_INTERVAL = 2
BLOCKED_KEYWORDS = [
        "Hãy subscribe cho kênh",
        "Ghiền Mì Gõ", 
        "Cảm ơn các bạn.",
    ]
        


whisper_model = whisper.load_model("medium").to("cuda")

class AudioBuffer:
    def __init__(self, role, vad):
        self.role = role
        self.vad = vad
        self.frames = []
        self.raw_frames = []
        self.speaking = False
        self.last_voice_time = time.time()
        self.queue = queue.Queue()
        threading.Thread(target=self.audio_worker, daemon=True).start()

    def add_frame(self, frame, raw_pcm):
        int16_frame = (frame * 32768).clip(-32768, 32767).astype(np.int16)
        pcm_bytes = int16_frame.tobytes()

        try:
            is_speech = self.vad.is_speech(pcm_bytes, SAMPLE_RATE)
        except Exception as e:
            print(f"[VAD ERROR] ({self.role}):", e)
            return

        now = time.time()
        if is_speech:
            self.frames.append(frame.copy())
            self.raw_frames.append(raw_pcm)
            self.speaking = True
            self.last_voice_time = now
        elif self.speaking and now - self.last_voice_time < 0.1:
            self.frames.append(frame.copy())
            self.raw_frames.append(raw_pcm)
        elif self.speaking and now - self.last_voice_time >= 0.1:
            self.speaking = False
            result = self.get_audio()
            if result:
                self.queue.put(result)

    def get_audio(self):
        if not self.frames or not self.raw_frames:
            return None
        audio = np.concatenate(self.frames, axis=0)
        raw_pcm = b"".join(self.raw_frames)
        self.frames = []
        self.raw_frames = []
        duration = len(audio) / SAMPLE_RATE
        energy = np.sqrt(np.mean(audio ** 2))
        if duration < 0.2 or energy < 0.01:
            return None
        return audio, raw_pcm

    def audio_worker(self):
        while True:
            result = self.queue.get()
            if result:
                audio, raw_pcm = result
                self.transcribe_with_whisper(raw_pcm)
            self.queue.task_done()

    def transcribe_with_whisper(self, raw_pcm):
        samples = np.frombuffer(raw_pcm, dtype=np.int16).reshape(-1, CHANNELS)
        mono = samples.mean(axis=1).astype(np.float32) / 32768.0
        audio_16k = resampy.resample(mono, WS_SAMPLE_RATE, 16000)

        if len(audio_16k) < 16000:
            print(f"[WHISPER] Skipped: too short ({len(audio_16k)} samples)")
            return

        try:
            result = whisper_model.transcribe(audio_16k, language="vi")
            text = result['text'].strip()

            if any(keyword.lower() in text.lower() for keyword in BLOCKED_KEYWORDS) o :
                return

            print(f"[WHISPER] Role: {self.role} | Text: {result['text']}")

        except Exception as e:
            print(f"[ERROR] Whisper failed: {e}")

def process_audio_frame(frame_bytes: bytes, role: str, buffer_user: AudioBuffer, buffer_other: AudioBuffer):
    samples = np.frombuffer(frame_bytes, dtype=np.int16).reshape(-1, CHANNELS)
    audio_segment = AudioSegment(
        samples.tobytes(),
        frame_rate=WS_SAMPLE_RATE,
        sample_width=2,
        channels=CHANNELS
    )
    filtered_segment = low_pass_filter(audio_segment, cutoff=3000)
    filtered_samples = np.frombuffer(filtered_segment.raw_data, dtype=np.int16).reshape(-1, CHANNELS)
    float_samples = filtered_samples.astype(np.float32) / 32768.0
    mono = float_samples.mean(axis=1)
    resampled = resampy.resample(mono, WS_SAMPLE_RATE, SAMPLE_RATE)
    frame_reshaped = resampled.reshape(-1, 1).astype(np.float32)
    raw_pcm = filtered_samples.astype(np.int16).tobytes()

    if role == "user":
        buffer_user.add_frame(frame_reshaped, raw_pcm)
    elif role == "other":
        buffer_other.add_frame(frame_reshaped, raw_pcm)


async def process_audio_stream(websocket: WebSocket, buffer_user: AudioBuffer, buffer_other: AudioBuffer):
    frame_accum_user = b""
    frame_accum_other = b""
    recv_buffer = b""

    while True:
        try:
            chunk = await websocket.receive_bytes()
            recv_buffer += chunk

            while len(recv_buffer) >= 4:
                header_len = struct.unpack("!I", recv_buffer[:4])[0]
                if len(recv_buffer) < 4 + header_len:
                    break

                header_bytes = recv_buffer[4:4 + header_len]
                try:
                    header = json.loads(header_bytes.decode("utf-8"))
                    role = header.get("sender", "unknown")
                except:
                    recv_buffer = recv_buffer[4 + header_len:]
                    continue

                full_len = 4 + header_len
                remaining = recv_buffer[full_len:]
                recv_buffer = b""

                sample_align = CHANNELS * BYTES_PER_SAMPLE
                valid_len = len(remaining) - (len(remaining) % sample_align)
                pcm_bytes = remaining[:valid_len]

                if role == "user":
                    frame_accum_user += pcm_bytes
                    while len(frame_accum_user) >= FRAME_BYTES:
                        frame = frame_accum_user[:FRAME_BYTES]
                        frame_accum_user = frame_accum_user[FRAME_BYTES:]
                        process_audio_frame(frame, "user", buffer_user, buffer_other)

                elif role == "other":
                    frame_accum_other += pcm_bytes
                    while len(frame_accum_other) >= FRAME_BYTES:
                        frame = frame_accum_other[:FRAME_BYTES]
                        frame_accum_other = frame_accum_other[FRAME_BYTES:]
                        process_audio_frame(frame, "other", buffer_user, buffer_other)

            await asyncio.sleep(0.01)

        except Exception as e:
            print("[WebSocket Error]:", e)
            break


@router.websocket("/ws/audio")
async def audio_socket(websocket: WebSocket):
    await websocket.accept()

    vad_user = webrtcvad.Vad(1)
    vad_other = webrtcvad.Vad(1)

    buffer_user = AudioBuffer("user", vad_user)
    buffer_other = AudioBuffer("other", vad_other)

    async def heartbeat():
        while True:
            await asyncio.sleep(PING_INTERVAL)
            try:
                await websocket.send_text("ping")
            except:
                break

    heartbeat_task = asyncio.create_task(heartbeat())

    try:
        await process_audio_stream(websocket, buffer_user, buffer_other)
    except WebSocketDisconnect:
        pass
    finally:
        heartbeat_task.cancel()


app.include_router(router)
