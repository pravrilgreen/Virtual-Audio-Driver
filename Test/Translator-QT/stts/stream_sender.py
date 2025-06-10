import asyncio
import json
import struct
import threading
import time
import websocket

class WebSocketPCMClient:
    def __init__(self, role="customer", url=None):
        self.role = role  # "customer" or "user"
        self.url = url or "ws://localhost:8000/ws/audio"
        self.ws = None
        self.connected = False
        self.lock = threading.Lock()

        self.src_lang = "ja"
        self.tgt_lang = "vi"
        self.rate = 48000
        self.channels = 2
        self.sample_width = 2  # 16-bit PCM = 2 bytes

    def connect(self):
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(self.url)
            self.connected = True
            print(f"[WebSocketPCMClient] Connected to {self.url}")
        except Exception as e:
            print(f"[WebSocketPCMClient] Connection failed: {e}")
            self.connected = False

    def disconnect(self):
        try:
            if self.ws:
                self.ws.close()
                print("[WebSocketPCMClient] Connection closed.")
        except Exception as e:
            print(f"[WebSocketPCMClient] Error on disconnect: {e}")
        finally:
            self.connected = False

    def send_pcm_chunk(self, pcm_bytes: bytes):
        if not self.connected:
            return

        try:
            header = {
                "sender": self.role,
                "src_lang": self.src_lang,
                "tgt_lang": self.tgt_lang,
                "format": "pcm_s16le",
                "rate": self.rate,
                "channels": self.channels,
                "sample_width": self.sample_width,
                "timestamp": time.time()
            }

            header_bytes = json.dumps(header).encode("utf-8")
            header_len = struct.pack("!I", len(header_bytes))  # 4-byte big-endian

            message = header_len + header_bytes + pcm_bytes

            with self.lock:  # ensure thread-safe write
                self.ws.send_binary(message)

        except Exception as e:
            print(f"[WebSocketPCMClient] Send failed: {e}")
            self.connected = False
