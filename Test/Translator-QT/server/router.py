from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from processor import process_audio_pipeline
import struct
import json
import asyncio

router = APIRouter()

@router.websocket("/ws/audio")
async def audio_socket(websocket: WebSocket):
    await websocket.accept()
    print("[WS] Client connected.")

    buffer = b""
    last_header = {}

    try:
        while True:
            data = await websocket.receive_bytes()
            if len(data) < 4:
                continue

            header_len = struct.unpack("!I", data[:4])[0]
            header_bytes = data[4:4 + header_len]
            pcm_bytes = data[4 + header_len:]

            header = json.loads(header_bytes.decode("utf-8"))
            buffer += pcm_bytes
            last_header = header

            #print(f"[RECEIVE] {len(pcm_bytes)} bytes from {header.get('sender')}")

            # Process every ~2s of audio (stereo, 16-bit, 48kHz)
            if len(buffer) > 48000 * 2 * 4:
                print(f"[PROCESS] {len(buffer)} bytes from {header.get('sender')}, starting dummy pipeline...")
                response = process_audio_pipeline(buffer, last_header)

                # Prevent blocking if client is not reading
                try:
                    await asyncio.wait_for(websocket.send_text(json.dumps(response)), timeout=1.0)
                except asyncio.TimeoutError:
                    print("[WARN] Client not reading response → dropped.")

                buffer = b""

    except WebSocketDisconnect:
        print("[WS] Disconnected.")
    except Exception as e:
        print("[WS] Error:", e)