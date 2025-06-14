from PySide6.QtCore import QThread, Signal
import ctypes
import numpy as np
import time
import math
import sounddevice as sd
from stts.stream_sender import WebSocketPCMClient
import queue
import threading
import json
import struct
from scipy.signal import resample_poly
from core.audio_mixer import AudioMixer
from settings_manager import SettingsManager
from pydub import AudioSegment
import io
from core.translated_audio_manager import TranslatedAudioManager

class SpeakerMonitorThread(QThread):
    volume_signal = Signal(int)
    fft_signal = Signal(list)

    def __init__(self, parent=None, lang_combo=None):
        super().__init__(parent)
        self.running = True
        self.ws_client = WebSocketPCMClient(role="other")
        self.enable_translation = True
        self.output_stream = None
        self.output_device_index = None
        # self.playback_queue = queue.Queue()
        # self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.translated_audio_buffer = None
        self.translation_playing = False
        self.lang_combo = lang_combo
        self.translated_audio_manager = TranslatedAudioManager(sample_rate=48000)

    def set_translation_enabled(self, enabled: bool):
        self.enable_translation = enabled
        if enabled:
            self.ws_client.connect()

            def on_translated_audio(wav_bytes):
                print("[SpeakerMonitorThread] Received audio from server.")
                self.translated_audio_manager.add_wav(wav_bytes)

            self.ws_client.register_audio_callback(on_translated_audio)
            if self.lang_combo:
                text = self.lang_combo.currentText()
                lang = self.get_lang_code(text)
                self.update_language(src_lang=lang)
        else:
            self.ws_client.disconnect()
            self.translated_audio_buffer = None


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
        READ_SIZE = 8192  # Increased buffer size
        INPUT_SAMPLE_RATE = 48000
        CHANNELS = 2

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

        if handle in (0, -1):
            print("[ERROR] Failed to open device handle.")
            return

        print("[INFO] SpeakerMonitorThread started.")

        try:
            device_info = sd.query_devices(self.output_device_index or None)
            actual_sample_rate = int(device_info['default_samplerate'])

            self.output_stream = sd.RawOutputStream(
                samplerate=actual_sample_rate,
                channels=CHANNELS,
                dtype='int16',
                device=self.output_device_index or None,
                blocksize=READ_SIZE // (2 * CHANNELS),
                latency='low'
            )
            self.output_stream.start()
            #self.playback_thread.start()
        except Exception as e:
            print("[ERROR] Failed to open output stream:", e)
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

                if not result or bytes_returned.value == 0:
                    time.sleep(0.001)
                    continue

                raw = buffer.raw[:bytes_returned.value]
                if len(raw) % 2 != 0:
                    raw = raw[:-1]

                audio = np.frombuffer(raw, dtype=np.int16)
                if audio.size == 0 or len(audio) % CHANNELS != 0:
                    continue

                audio = audio.reshape(-1, CHANNELS)

                # Optional resample if needed
                if actual_sample_rate != INPUT_SAMPLE_RATE:
                    left = resample_poly(audio[:, 0], actual_sample_rate, INPUT_SAMPLE_RATE)
                    right = resample_poly(audio[:, 1], actual_sample_rate, INPUT_SAMPLE_RATE)
                    audio = np.stack([left, right], axis=1).astype(np.int16)

                # Volume RMS
                mono = audio.mean(axis=1)
                rms = np.sqrt(np.mean(mono.astype(np.float64) ** 2))
                volume_threshold = 300
                MAX_RMS = 9000
                adjusted_rms = max(0, rms - volume_threshold)
                volume = int(min(100, math.log1p(adjusted_rms) / math.log1p(MAX_RMS) * 100))
                self.volume_signal.emit(volume)

                # FFT Signal
                fft = np.fft.rfft(mono, n=128)
                fft_magnitude = np.abs(fft)
                fft_magnitude /= (np.max(fft_magnitude) + 1e-6)
                self.fft_signal.emit(fft_magnitude[:64].tolist())

                # Send to real speaker
                try:
                    audio_chunk = audio.astype(np.int16)
                    chunk_size = audio_chunk.shape[0]
                    translated = self.translated_audio_manager.get_chunk_by_samples(chunk_size)

                    if translated is None:
                        translated = np.zeros((chunk_size, 2), dtype=np.int16)

                    # Lấy cài đặt âm lượng
                    settings = SettingsManager()
                    direct_volume = settings.get("direct_volume", 100)
                    translated_volume = settings.get("translated_volume", 100)
                    speaker_level = settings.get("speaker_level", 100)

                    # Trộn 2 nguồn âm
                    mixer = AudioMixer(direct_volume=direct_volume, translated_volume=translated_volume)
                    mixed = mixer.mix(audio_chunk, translated)

                    # Điều chỉnh âm lượng tổng thể và phát ra loa
                    mixed = mixed.astype(np.float32) * (speaker_level / 100.0)
                    mixed = np.clip(mixed, -32768, 32767).astype(np.int16)
                    self.output_stream.write(mixed.tobytes())

                except queue.Full:
                    print("[WARN] playback_queue full, dropping chunk.")

                # Send to socket if enabled
                if self.enable_translation and self.ws_client.connected:
                    self.ws_client.send_pcm_chunk(raw)

        except Exception as e:
            print("[ERROR] SpeakerMonitorThread exception:", e)

        finally:
            if self.output_stream:
                try:
                    self.output_stream.stop()
                    self.output_stream.close()
                except Exception as e:
                    print("[WARN] Cleanup output stream failed:", e)
                self.output_stream = None

            self.ws_client.disconnect()
            CloseHandle(handle)
            print("[INFO] SpeakerMonitorThread stopped.")

    def stop(self):
        self.running = False