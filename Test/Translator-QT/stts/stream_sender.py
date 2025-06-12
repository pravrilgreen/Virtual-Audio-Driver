import threading
import websocket
import json
import struct
import time
import queue


class WebSocketPCMClient:
    def __init__(self, role="other", url=None):  # role = other or user
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

        self.send_queue = queue.Queue(maxsize=500)
        self.receiver_thread = None
        self.sender_thread = None
        self.running = False
        self.reconnect_lock = threading.Lock()
        self.stop_event = threading.Event()
        self.audio_callback = None
        self.manual_stop = False  # New flag to distinguish manual vs. error stop

    def connect(self):
        if self.connected or self.running:
            return

        def _connect_thread():
            with self.reconnect_lock:
                try:
                    self.ws = websocket.WebSocket()
                    self.ws.connect(self.url, timeout=5)
                    self.connected = True
                    self.running = True
                    self.manual_stop = False
                    self.stop_event.clear()
                    print(f"[WebSocketPCMClient] Connected to {self.url}")

                    self.sender_thread = threading.Thread(target=self._sender_loop, daemon=True)
                    self.receiver_thread = threading.Thread(target=self._receiver_loop, daemon=True)
                    self.sender_thread.start()
                    self.receiver_thread.start()
                except Exception as e:
                    self.connected = False
                    self.running = False
                    print(f"[WebSocketPCMClient] Connection failed: {e}")
                    self._attempt_reconnect()

        threading.Thread(target=_connect_thread, daemon=True).start()

    def disconnect(self, auto_reconnect=False):
        self.manual_stop = not auto_reconnect  # Set manual_stop to True only if no reconnect is wanted
        self.running = False
        self.stop_event.set()

        with self.lock:
            try:
                if self.ws:
                    self.ws.close()
                    print("[WebSocketPCMClient] Connection closed.")
            except Exception as e:
                print(f"[WebSocketPCMClient] Error on disconnect: {e}")
            finally:
                self.ws = None
                self.connected = False

        if auto_reconnect:
            self._attempt_reconnect()

    def send_pcm_chunk(self, pcm_bytes: bytes):
        if not self.connected or not self.running or not self.ws:
            return
        try:
            # Block until space available (up to 1 sec), avoids dropping frames
            self.send_queue.put(pcm_bytes, timeout=1)
        except queue.Full:
            print("[WARN] Send queue full. Audio frame dropped.")


    def _sender_loop(self):
        while self.running and not self.stop_event.is_set():
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
                    if self.ws and self.connected:
                        self.ws.send_binary(message)
                        #print(f"[SEND] {len(pcm_bytes)} bytes sent for role: {self.role}")
                    else:
                        print("[WebSocketPCMClient] Cannot send: WebSocket is not connected.")

            except queue.Empty:
                continue
            except Exception as e:
                print("[WebSocketPCMClient] Send failed:", e)
                self.disconnect(auto_reconnect=True)

    def _receiver_loop(self):
        while self.running and not self.stop_event.is_set():
            try:
                msg = self.ws.recv()
                if isinstance(msg, str):
                    if msg.strip().lower() == "ping":
                        print("[server] ping pong")
                        continue
                elif isinstance(msg, bytes) and self.audio_callback:
                    self.audio_callback(msg)
            except Exception as e:
                print("[WS RECEIVER ERROR]", e)
                self.disconnect(auto_reconnect=True)


    def _attempt_reconnect(self):
        if self.manual_stop:
            print("[WebSocketPCMClient] Reconnect skipped (stopped manually).")
            return

        print("[WebSocketPCMClient] Attempting to reconnect...")
        time.sleep(1.5)
        self.connect()

    def register_audio_callback(self, callback_fn):
        self.audio_callback = callback_fn
