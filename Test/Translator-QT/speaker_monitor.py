from PySide6.QtCore import QThread, Signal
import ctypes
import numpy as np
import time
import math
import sounddevice as sd
from stts.stream_sender import WebSocketPCMClient  # 💡 WebSocket client bạn cần tạo

class SpeakerMonitorThread(QThread):
    volume_signal = Signal(int)
    fft_signal = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.ws_client = WebSocketPCMClient(role="customer")  # "customer" hoặc "user"

    def find_output_device(self, name):
        for i, dev in enumerate(sd.query_devices()):
            if name.lower() in dev['name'].lower() and dev['max_output_channels'] > 0:
                return i
        return None

    def run(self):
        GENERIC_READ = 0x80000000
        GENERIC_WRITE = 0x40000000
        OPEN_EXISTING = 3
        FILE_ATTRIBUTE_NORMAL = 0x80
        FILE_DEVICE_UNKNOWN = 0x00000022
        METHOD_BUFFERED = 0
        FILE_WRITE_DATA = 0x0002

        def CTL_CODE(DeviceType, Function, Method, Access):
            return (DeviceType << 16) | (Access << 14) | (Function << 2) | Method

        IOCTL_READ_AUDIO = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x80A, METHOD_BUFFERED, FILE_WRITE_DATA)
        DEVICE_NAME = r"\\.\VirtualAudio"
        READ_SIZE = 4096
        CHANNELS = 2
        SAMPLE_RATE = 48000

        kernel32 = ctypes.windll.kernel32
        CreateFileW = kernel32.CreateFileW
        DeviceIoControl = kernel32.DeviceIoControl
        CloseHandle = kernel32.CloseHandle
        CreateFileW.restype = ctypes.c_void_p

        handle = CreateFileW(
            DEVICE_NAME,
            GENERIC_READ | GENERIC_WRITE,
            0, None,
            OPEN_EXISTING,
            FILE_ATTRIBUTE_NORMAL,
            None
        )

        if handle == 0 or handle == -1:
            print("[ERROR] Failed to open device handle.")
            return

        print("[INFO] SpeakerMonitorThread started.")

        # Connect WebSocket
        self.ws_client.connect()

        try:
            while self.running:
                buffer = ctypes.create_string_buffer(READ_SIZE)
                bytes_returned = ctypes.c_ulong(0)

                result = DeviceIoControl(
                    handle,
                    IOCTL_READ_AUDIO,
                    None, 0,
                    buffer, READ_SIZE,
                    ctypes.byref(bytes_returned),
                    None
                )

                if result and bytes_returned.value > 0:
                    raw = buffer.raw[:bytes_returned.value]
                    if len(raw) % 2 != 0:
                        raw = raw[:-1]

                    audio = np.frombuffer(raw, dtype=np.int16)

                    if len(audio) % CHANNELS != 0:
                        audio = audio[:len(audio) - (len(audio) % CHANNELS)]

                    try:
                        audio = audio.reshape(-1, CHANNELS)
                        mono = audio.mean(axis=1)
                    except Exception as e:
                        print("[WARN] Reshape error:", e)
                        mono = audio
                        audio = np.stack((mono, mono), axis=1)

                    rms = np.sqrt(np.mean(mono.astype(np.float64) ** 2))
                    volume_threshold = 300
                    MAX_RMS = 9000
                    adjusted_rms = max(0, rms - volume_threshold)
                    volume = int(min(100, math.log1p(adjusted_rms) / math.log1p(MAX_RMS) * 100))
                    self.volume_signal.emit(volume)

                    fft = np.fft.rfft(mono, n=128)
                    fft_magnitude = np.abs(fft)
                    fft_magnitude = fft_magnitude / (np.max(fft_magnitude) + 1e-6)
                    self.fft_signal.emit(fft_magnitude[:64].tolist())
                    self.ws_client.send_pcm_chunk(raw)

                else:
                    time.sleep(0.005)

        except Exception as e:
            print("[ERROR]", e)
        finally:
            CloseHandle(handle)
            self.ws_client.disconnect()
            print("[INFO] SpeakerMonitorThread stopped.")

    def stop(self):
        self.running = False
