from PySide6.QtCore import QThread, Signal
import ctypes
import numpy as np
import time
import math
import sounddevice as sd


class SpeakerMonitorThread(QThread):
    volume_signal = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running = True
        self.stream = None

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
        FILE_READ_DATA = 0x0001

        def CTL_CODE(DeviceType, Function, Method, Access):
            return (DeviceType << 16) | (Access << 14) | (Function << 2) | Method

        IOCTL_READ_AUDIO = CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_READ_DATA)
        DEVICE_NAME = r"\\.\HackAI_AudioCtrl"
        READ_SIZE = 4096
        CHANNELS = 2
        SAMPLE_RATE = 48000
        OUTPUT_DEVICE_NAME = "Scarlett 2i2 USB"

        # Khởi tạo handle cho thiết bị ảo
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

        # Tìm thiết bị đầu ra Scarlett
        output_device_index = self.find_output_device(OUTPUT_DEVICE_NAME)
        if output_device_index is None:
            print(f"[ERROR] Output device '{OUTPUT_DEVICE_NAME}' not found.")
            CloseHandle(handle)
            return

        # Khởi tạo audio stream
        try:
            self.stream = sd.OutputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype='int16',
                device=output_device_index,
                blocksize=READ_SIZE // (2 * CHANNELS),
            )
            self.stream.start()
        except Exception as e:
            print("[ERROR] Cannot start audio output stream:", e)
            CloseHandle(handle)
            return

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

                    # Đảm bảo chia hết cho số kênh
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
                    volume = int(min(10, math.log1p(adjusted_rms) / math.log1p(MAX_RMS) * 10))

                    print(f"[DEBUG] RMS: {rms:.2f} | Volume: {volume}")
                    self.volume_signal.emit(volume)

                    try:
                        self.stream.write(audio)
                    except Exception as e:
                        print("[WARN] Audio playback failed:", e)
                else:
                    time.sleep(0.005)

        except Exception as e:
            print("[ERROR]", e)
        finally:
            if self.stream:
                self.stream.stop()
                self.stream.close()
            CloseHandle(handle)
            print("[INFO] SpeakerMonitorThread stopped.")

    def stop(self):
        self.running = False
