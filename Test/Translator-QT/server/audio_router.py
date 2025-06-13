import webrtcvad  # type: ignore
import numpy as np
import os
import time
import threading
import queue
import json
import struct
import resampy  # type: ignore
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter
import asyncio
from pydub import AudioSegment  # type: ignore
from pydub.effects import low_pass_filter  # type: ignore
import whisper
from starlette.websockets import WebSocketState
import base64
# from modules.synthesizer import tts # Uncomment for deploy
# from modules.translator.core.orchestrator import Orchestrator as Translator  # Uncomment for deploy


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
    "Hẹn gặp lại ở video tiếp theo",
    "Chào mừng quý vị đến với bộ phim",
    "Chúc các bạn đừng quên đăng ký",
    "ご視聴ありがとうございました",
    "Cảm ơn các bạn đã xem video hấp dẫn",
    "ご視聴ありがとうございました",
]

whisper_model = whisper.load_model("medium").to("cuda")

#translator = Translator()  # Uncomment for deploy


class AudioBuffer:
    def __init__(self, role, vad, message_queue, loop):
        self.role = role
        self.vad = vad
        self.loop = loop
        self.message_queue = message_queue
        self.frames = []
        self.raw_frames = []
        self.speaking = False
        self.last_voice_time = time.time()
        self.src_lang = "vi"
        self.tgt_lang = "jp"
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
                self.audio_process_pipeline(raw_pcm)
            self.queue.task_done()

    def audio_process_pipeline(self, raw_pcm):
        samples = np.frombuffer(raw_pcm, dtype=np.int16).reshape(-1, CHANNELS)
        mono = samples.mean(axis=1).astype(np.float32) / 32768.0
        audio_16k = resampy.resample(mono, WS_SAMPLE_RATE, 16000)

        if len(audio_16k) < 16000:
            return

        try:
            # 1. Transribe audio -> text
            result = whisper_model.transcribe(audio_16k, language=self.src_lang)
            text = result['text'].strip()

            if any(keyword.lower() in text.lower() for keyword in BLOCKED_KEYWORDS) or not text:
                return

            print(f"[WHISPER] Role: {self.role} | Language: {self.tgt_lang} | Text: {text}")

            # DUMMY
            with open("sample.wav", "rb") as f:
                wav_bytes = f.read()

            # ================   Uncomment for deploy ================
            # 2. Translate text to self.tgt_lang -> output <translated text>
            # texts_translated = translator.translate(texts=[text], src=self.src_lang, tgt=self.tgt_lang) 
            # text_translated = ' '.join(texts_translated) 

            # if self.tgt_lang == "ja":
            #     audio_hex = tts.tts_japanese(text_translated) # TODO: translated_text
            # else:
            #     audio_hex = tts.tts_vietnamese(text_translated) # TODO: translated_text
             # ================   Uncomment for deploy ================

            # 3. TTS <translated text> -> output audio (WAV byte)
            package = {
                "type": "translate_with_audio",
                "data": {
                    "text": text, # -> replace <translated text>
                    "role": self.role, # user or other
                    "audio_bytes": wav_bytes.hex()
                }
            }
            
            # Push message to main loop's queue
            print(f"[QUEUE PUSH] Role: {self.role} | Pushing message: {text}")
            self.loop.call_soon_threadsafe(self.message_queue.put_nowait, package)

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

    prev_langs = {
        "user": {"src": "vi", "tgt": "transcript"},
        "other": {"src": "ja", "tgt": "transcript"}
    }

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

                    if role not in ["user", "other"]:
                        recv_buffer = recv_buffer[4 + header_len:]
                        continue

                    new_src = header.get("src_lang", prev_langs[role]["src"])
                    new_tgt = header.get("tgt_lang", prev_langs[role]["tgt"])
                    if new_src != prev_langs[role]["src"] or new_tgt != prev_langs[role]["tgt"]:
                        print(f"[LANGUAGE CHANGE] Role: {role} Source: {new_src}, Target: {new_tgt}")
                        prev_langs[role]["src"] = new_src
                        prev_langs[role]["tgt"] = new_tgt

                        if role == "user":
                            buffer_user.src_lang = new_src
                            buffer_user.tgt_lang = new_tgt
                        elif role == "other":
                            buffer_other.src_lang = new_src
                            buffer_other.tgt_lang = new_tgt

                except Exception as e:
                    print(f"[HEADER ERROR]: {e}")
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

    loop = asyncio.get_running_loop()
    message_queue = asyncio.Queue()

    buffer_user = AudioBuffer("user", vad_user, message_queue, loop)
    buffer_user.src_lang = "vi"
    buffer_user.tgt_lang = "ja"
    buffer_other = AudioBuffer("other", vad_other, message_queue, loop)
    buffer_other.src_lang = "ja"
    buffer_other.tgt_lang = "vi"

    async def heartbeat():
        while True:
            await asyncio.sleep(PING_INTERVAL)
            try:
                await websocket.send_text("ping")
            except Exception as e:
                print(f"[HEARTBEAT ERROR] WebSocket closed: {e}")
                break

    async def message_sender():
        while True:
            package = await message_queue.get()
            try:
                await websocket.send_json(package)
                print(f"[SEND SUCCESS] Sent package to client")
            except Exception as e:
                print(f"[SEND ERROR] {e}")
                break


    heartbeat_task = asyncio.create_task(heartbeat())
    sender_task = asyncio.create_task(message_sender())

    try:
        await process_audio_stream(websocket, buffer_user, buffer_other)
    except WebSocketDisconnect:
        pass
    finally:
        heartbeat_task.cancel()
        sender_task.cancel()


app.include_router(router)