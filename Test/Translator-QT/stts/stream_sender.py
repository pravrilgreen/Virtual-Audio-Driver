import threading
import websocket
import json
import struct
import time
import queue


class WebSocketPCMClient:
    def __init__(self, role="other", url=None):
        self.role = role
        self.url = url or "ws://localhost:8000/ws/audio"

        self.ws_app = None
        self.ws_thread = None
        self.sender_thread = None

        self.connected = False
        self.running = False
        self.manual_stop = False
        self.stop_event = threading.Event()
        self.lock = threading.Lock()

        self.send_queue = queue.Queue(maxsize=100)
        self.audio_callback = None

        self.src_lang = "ja"
        self.tgt_lang = "vi"
        self.rate = 48000
        self.channels = 2
        self.sample_width = 2

    # ===============================
    # WebSocketApp Callbacks
    # ===============================
    def _on_open(self, ws):
        print(f"[WebSocketPCMClient] Connected to {self.url} (role: {self.role})")
        self.connected = True
        self.running = True

    def _on_close(self, ws, code, msg):
        print(f"[WebSocketPCMClient] Disconnected (code={code}, msg={msg})")
        self.connected = False
        self.running = False
        if not self.manual_stop:
            self._schedule_reconnect()

    def _on_error(self, ws, error):
        print("[WebSocketPCMClient] Error:", error)

    def _on_message(self, ws, message):
        if isinstance(message, bytes) and self.audio_callback:
            self.audio_callback(message)

    # ===============================
    # Connection Management
    # ===============================
    def connect(self):
        if self.running:
            return

        self.manual_stop = False
        self.stop_event.clear()

        self.ws_app = websocket.WebSocketApp(
            self.url,
            on_open=self._on_open,
            on_close=self._on_close,
            on_error=self._on_error,
            on_message=self._on_message
        )

        def run_ws():
            while not self.manual_stop:
                self.ws_app.run_forever()
                if not self.manual_stop:
                    print("[WebSocketPCMClient] Reconnecting in 2 seconds...")
                    time.sleep(2)

        self.ws_thread = threading.Thread(target=run_ws, daemon=True)
        self.ws_thread.start()

        self.sender_thread = threading.Thread(target=self._sender_loop, daemon=True)
        self.sender_thread.start()

    def disconnect(self):
        self.manual_stop = True
        self.running = False
        self.stop_event.set()
        try:
            if self.ws_app:
                self.ws_app.close()
        except Exception as e:
            print("[WebSocketPCMClient] Error during disconnect:", e)

    def _schedule_reconnect(self):
        print("[WebSocketPCMClient] Scheduling reconnect...")
        time.sleep(2)
        self.connect()

    # ===============================
    # PCM Sending
    # ===============================
    def send_pcm_chunk(self, pcm_bytes: bytes):
        if not self.connected or not self.running or not self.ws_app:
            return
        try:
            self.send_queue.put_nowait(pcm_bytes)
        except queue.Full:
            print("[WebSocketPCMClient] Send queue full. Dropping chunk.")

    def _sender_loop(self):
        while not self.stop_event.is_set():
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

                if self.connected and self.ws_app:
                    self.ws_app.send(message, opcode=websocket.ABNF.OPCODE_BINARY)
                    #print(f"[SEND] {len(pcm_bytes)} bytes sent for role: {self.role}")
            except queue.Empty:
                continue
            except Exception as e:
                print("[WebSocketPCMClient] Send failed:", e)

    # ===============================
    # Callback Registration
    # ===============================
    def register_audio_callback(self, callback_fn):
        self.audio_callback = callback_fn
