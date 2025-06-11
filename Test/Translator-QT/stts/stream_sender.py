import threading
import websocket
import json
import struct
import time
import queue


class WebSocketPCMClient:
    def __init__(self, role="customer", url=None):
        self.role = role
        self.url = url or "ws://localhost:8000/ws/audio"
        self.ws = None
        self.connected = False
        self.lock = threading.Lock()

        self.src_lang = "ja"
        self.tgt_lang = "vi"
        self.rate = 48000
        self.channels = 2
        self.sample_width = 2

        self.send_queue = queue.Queue()
        self.receiver_thread = None
        self.sender_thread = None
        self.running = False

    def connect(self):
        self.running = True
        try:
            self.ws = websocket.WebSocket()
            self.ws.connect(self.url)
            self.connected = True
            print(f"[WebSocketPCMClient] Connected to {self.url}")
        except Exception as e:
            print(f"[WebSocketPCMClient] Connection failed: {e}")
            self.connected = False
            return

        # Start sender and receiver threads
        self.sender_thread = threading.Thread(target=self._sender_loop, daemon=True)
        self.receiver_thread = threading.Thread(target=self._receiver_loop, daemon=True)
        self.sender_thread.start()
        self.receiver_thread.start()

    def disconnect(self):
        self.running = False
        try:
            if self.ws:
                self.ws.close()
                print("[WebSocketPCMClient] Connection closed.")
        except Exception as e:
            print(f"[WebSocketPCMClient] Error on disconnect: {e}")
        finally:
            self.connected = False

    def send_pcm_chunk(self, pcm_bytes: bytes):
        """
        Enqueue PCM chunk to be sent asynchronously.
        """
        if not self.connected or not self.running:
            return
        self.send_queue.put(pcm_bytes)

    def _sender_loop(self):
        while self.running and self.connected:
            try:
                pcm_bytes = self.send_queue.get(timeout=1)

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
                header_len = struct.pack("!I", len(header_bytes))
                message = header_len + header_bytes + pcm_bytes

                with self.lock:
                    self.ws.send_binary(message)

                print(f"[SEND] {len(pcm_bytes)} bytes sent for role: {self.role}")

            except queue.Empty:
                continue
            except Exception as e:
                print("[WebSocketPCMClient] Send failed:", e)
                self.connected = False
                self._attempt_reconnect()

    def _receiver_loop(self):
        while self.running and self.connected:
            try:
                msg = self.ws.recv()
                #print("[RECEIVE FROM SERVER]", msg)
            except Exception as e:
                print("[WS RECEIVER ERROR]", e)
                self.connected = False
                self._attempt_reconnect()

    def _attempt_reconnect(self):
        print("[WebSocketPCMClient] Attempting to reconnect...")
        self.disconnect()
        time.sleep(1.5)
        self.connect()
