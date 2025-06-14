from PySide6.QtCore import QThread, Signal
import numpy as np
import sounddevice as sd
import math
import json
import struct
import threading
import queue
import time
import win32file
import win32con
import pywintypes
from core.audio_mixer import AudioMixer
from settings_manager import SettingsManager
from stts.stream_sender import WebSocketPCMClient
from pydub import AudioSegment
import io
from core.translated_audio_manager import TranslatedAudioManager

class MicMonitorThread(QThread):
    volume_signal = Signal(int)
    def __init__(self, input_device_name=None, writer: "VirtualMicWriter" = None, push_to_virtual=False, lang_combo=None, parent=None):
        super().__init__(parent)
        self.input_device_name = input_device_name
        self.writer = writer
        self.push_to_virtual = push_to_virtual
        self.running = True
        self.stream = None
        self.translated_audio_queue = queue.Queue()
        self.current_translated_chunk = None
        self.translated_offset = 0
        self.translated_audio_lock = threading.Lock()
        self.buffer_lock = threading.Lock()
        self.ws_client = WebSocketPCMClient(role="user")
        self.lang_combo = lang_combo
        self.translated_audio_manager = TranslatedAudioManager(sample_rate=48000)

    def set_translation_enabled(self, enabled: bool):
        if enabled:
            self.ws_client.connect()

            def on_translated_audio(wav_bytes):
                print("[MicMonitorThread] Received audio from server.")
                self.translated_audio_manager.add_wav(wav_bytes)

            self.ws_client.register_audio_callback(on_translated_audio)
            if self.lang_combo:
                text = self.lang_combo.currentText()
                lang = self.get_lang_code(text)
                self.update_language(src_lang=lang)
        else:
            self.ws_client.disconnect()
            with self.buffer_lock:
                self.translated_audio_buffer = np.empty((0, 2), dtype=np.int16)

    def find_input_device(self, name):
        for i, dev in enumerate(sd.query_devices()):
            if name.lower() in dev['name'].lower() and dev['max_input_channels'] > 0:
                return i
        return None

    def run(self):
        SAMPLE_RATE = 48000
        CHANNELS = 1

        device_index = self.find_input_device(self.input_device_name)
        if device_index is None:
            print(f"[ERROR] Input device '{self.input_device_name}' not found.")
            return

        try:
            with sd.InputStream(device=device_index,
                                channels=CHANNELS,
                                samplerate=SAMPLE_RATE,
                                dtype='int16',
                                blocksize=1024,
                                callback=self.audio_callback):
                while self.running:
                    sd.sleep(100)
        except Exception as e:
            print("[ERROR] Failed to start mic stream:", e)

    def audio_callback(self, indata, frames, time_info, status):
        raw_mono = indata[:, 0].copy()

        # 1. Gửi raw stereo lên server
        raw_stereo = np.repeat(raw_mono[:, np.newaxis], 2, axis=1)
        if self.ws_client.connected:
            self.ws_client.send_pcm_chunk(raw_stereo.astype(np.int16).tobytes())

        # 2. Mic gain
        mic_level = SettingsManager().get("microphone_level", 100)
        mic_gain = mic_level / 100.0
        mono = raw_mono.astype(np.float32) * mic_gain
        mono = np.clip(mono, -32768, 32767).astype(np.int16)
        mic_stereo = np.repeat(mono[:, np.newaxis], 2, axis=1)

        # 3. Lấy translated audio chunk khớp độ dài
        chunk_size = indata.shape[0]  # thường là 1024
        translated = self.translated_audio_manager.get_chunk_by_samples(chunk_size)         

        if translated is None:
            translated = np.zeros((chunk_size, 2), dtype=np.int16)

        # 4. Mix
        direct_volume = SettingsManager().get("direct_volume", 100)
        translated_volume = SettingsManager().get("translated_volume", 100)
        mixer = AudioMixer(direct_volume=direct_volume, translated_volume=translated_volume)
        mixed = mixer.mix(mic_stereo, translated)

        # 5. Gửi ra virtual mic
        mixed_int32 = mixed.astype(np.int32) << 16
        self.writer.feed_audio(mixed_int32.tobytes())

        # 6. Volume RMS
        rms = np.sqrt(np.mean(raw_mono.astype(np.float64) ** 2))
        volume_threshold = 300
        MAX_RMS = 9000
        adjusted_rms = max(0, rms - volume_threshold)
        volume = int(min(100, math.log1p(adjusted_rms) / math.log1p(MAX_RMS) * 100))
        self.volume_signal.emit(volume)

    def stop(self):
        self.running = False
        self.ws_client.disconnect()

# ==== IOCTL DEFINITIONS ====
FILE_DEVICE_UNKNOWN = 0x00000022
METHOD_BUFFERED = 0
FILE_WRITE_DATA = 0x00000002
IOCTL_INDEX = 0x800
DEVICE_NAME = r"\\.\VirtualAudio"
CHUNK_SIZE = 4096
DESIRED_SAMPLE_RATE = 48000
DESIRED_CHANNELS = 2
DESIRED_BIT_DEPTH = 32

def ctl_code(device_type, function, method, access):
    return ((device_type << 16) | (access << 14) | (function << 2) | method)

IOCTL_VIRTUALAUDIO_WRITE = ctl_code(FILE_DEVICE_UNKNOWN, IOCTL_INDEX, METHOD_BUFFERED, FILE_WRITE_DATA)

# ==== VIRTUAL MIC WRITER ====
class VirtualMicWriter(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.audio_queue = queue.Queue()
        self.running = True
        self.handle = self.open_driver()

    def open_driver(self):
        try:
            handle = win32file.CreateFile(
                DEVICE_NAME,
                win32con.GENERIC_WRITE,
                0,
                None,
                win32con.OPEN_EXISTING,
                0,
                None
            )
            print("[+] Opened virtual mic driver.")
            return handle
        except Exception as e:
            print(f"[!] Failed to open driver: {e}")
            return None

    def feed_audio(self, pcm_bytes: bytes):
        """Feed raw PCM bytes to the driver. Will be split into chunks internally."""
        if not isinstance(pcm_bytes, bytes):
            raise ValueError("Audio data must be bytes.")
        self.audio_queue.put(pcm_bytes)

    def run(self):
        if not self.handle:
            return

        while self.running:
            try:
                data = self.audio_queue.get(timeout=0.1)
            except queue.Empty:
                continue

            offset = 0
            total = len(data)
            while offset < total:
                chunk = data[offset:offset + CHUNK_SIZE]
                try:
                    win32file.DeviceIoControl(
                        self.handle,
                        IOCTL_VIRTUALAUDIO_WRITE,
                        chunk,
                        None  # No output buffer
                    )
                except pywintypes.error as e:
                    print(f"[!] IOCTL error: {e}")
                    break
                offset += len(chunk)

        self.handle.close()

    def stop(self):
        self.running = False

class PCMPlayerThread(threading.Thread):
    def __init__(self, pcm_bytes: bytes, writer: VirtualMicWriter):
        super().__init__(daemon=True)
        self.pcm_bytes = pcm_bytes
        self.writer = writer
        self.running = True

    def run(self):
        if not isinstance(self.pcm_bytes, bytes):
            print("[PCM] Error: Input is not bytes.")
            return

        CHUNK_SIZE = 4096
        SAMPLE_RATE = 48000
        CHANNELS = 2
        BYTES_PER_SAMPLE = 4  # int32

        bytes_per_frame = CHANNELS * BYTES_PER_SAMPLE
        frames_per_chunk = CHUNK_SIZE // bytes_per_frame

        total_bytes = len(self.pcm_bytes)
        offset = 0
        chunk_index = 0
        start_time = time.time()

        print(f"[PCM] Playing {total_bytes} bytes into virtual mic...")

        while self.running and offset < total_bytes:
            chunk = self.pcm_bytes[offset:offset + CHUNK_SIZE]
            expected_time = start_time + (chunk_index * frames_per_chunk / SAMPLE_RATE)

            self.writer.feed_audio(chunk)

            offset += len(chunk)
            chunk_index += 1

            now = time.time()
            sleep_time = expected_time - now
            if sleep_time > 0:
                time.sleep(sleep_time)

        print("[PCM] Playback finished.")

    def stop(self):
        self.running = False