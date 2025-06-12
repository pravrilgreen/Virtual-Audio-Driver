from fastapi import WebSocket, WebSocketDisconnect, APIRouter
import struct
import json
import asyncio
import numpy as np
import sounddevice as sd
from queue import Queue, Empty
import threading
import time

router = APIRouter()

PING_INTERVAL = 2
SAMPLE_RATE = 48000
CHANNELS = 2
BYTES_PER_SAMPLE = 2
FRAME_MS = 21 
FRAME_SIZE = int(SAMPLE_RATE * FRAME_MS / 1000)
FRAME_BYTES = FRAME_SIZE * CHANNELS * BYTES_PER_SAMPLE


playback_queue = Queue(maxsize=100)

def playback_loop():
    stream = sd.RawOutputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype='int16',
        blocksize=FRAME_SIZE,
        latency='low'
    )
    stream.start()
    print("[AUDIO] Output stream started.")

    last_chunk = b'\x00' * FRAME_BYTES

    try:
        while True:
            try:
                chunk = playback_queue.get(timeout=0.05)
                last_chunk = chunk
            except Empty:
                chunk = last_chunk 
            if len(chunk) < FRAME_BYTES:
                chunk += b'\x00' * (FRAME_BYTES - len(chunk))

            stream.write(chunk)
            time.sleep(FRAME_MS / 1000.0) 

    except Exception as e:
        print("[AUDIO ERROR]", e)
    finally:
        stream.stop()
        stream.close()


threading.Thread(target=playback_loop, daemon=True).start()

async def process_audio_stream(websocket: WebSocket):
    frame_accum = b""

    while True:
        try:
            data = await websocket.receive_bytes()
        except Exception:
            break

        if len(data) < 4:
            continue

        try:
            header_len = struct.unpack("!I", data[:4])[0]
            header_bytes = data[4:4 + header_len]
            pcm_bytes = data[4 + header_len:]
            header = json.loads(header_bytes.decode("utf-8"))
            sender = header.get("sender", "unknown")
        except Exception as e:
            print("[HEADER ERROR]", e)
            continue

        print(f"[RECV] {len(pcm_bytes)} bytes from role: {sender}")
        frame_accum += pcm_bytes

        while len(frame_accum) >= FRAME_BYTES:
            frame = frame_accum[:FRAME_BYTES]
            frame_accum = frame_accum[FRAME_BYTES:]

            try:
                if playback_queue.full():
                    _ = playback_queue.get_nowait()
                playback_queue.put_nowait(frame)
            except Exception as e:
                print("[QUEUE ERROR]", e)

@router.websocket("/ws/audio")
async def audio_socket(websocket: WebSocket):
    await websocket.accept()
    print("[WS] Client connected.")

    async def heartbeat():
        while True:
            await asyncio.sleep(PING_INTERVAL)
            try:
                await websocket.send_text(json.dumps({"type": "ping"}))
            except:
                break

    heartbeat_task = asyncio.create_task(heartbeat())

    try:
        await process_audio_stream(websocket)
    except WebSocketDisconnect:
        print("[WS] Disconnected.")
    except Exception as e:
        print("[WS ERROR]", e)
    finally:
        heartbeat_task.cancel()
