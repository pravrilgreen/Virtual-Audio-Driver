import threading
import numpy as np
from pydub import AudioSegment
import io
import queue


class TranslatedAudioManager:
    def __init__(self, sample_rate=48000):
        self.sample_rate = sample_rate
        self.buffer = np.zeros((0, 2), dtype=np.int16)  # stereo buffer
        self.lock = threading.Lock()
        self.read_index = 0


    def add_wav(self, wav_bytes: bytes):
        """
        Nhận WAV mới từ server, chuyển về stereo int16 và nối vào buffer.
        """
        try:
            audio = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")
            print(f"[DEBUG] Translated audio duration: {audio.duration_seconds:.2f}s, length: {len(audio.raw_data)} bytes")
            audio = audio.set_channels(2).set_sample_width(2).set_frame_rate(self.sample_rate)
            samples = np.frombuffer(audio.raw_data, dtype=np.int16).reshape(-1, 2)

            with self.lock:
                self.buffer = np.vstack((self.buffer, samples))
        except Exception as e:
            print(f"[TranslatedAudioManager] Failed to decode WAV: {e}")


    def get_chunk_by_samples(self, n_samples: int) -> np.ndarray:
        with self.lock:
            end_index = self.read_index + n_samples
            available = len(self.buffer) - self.read_index

            if available <= 0:
                return np.zeros((n_samples, 2), dtype=np.int16)  # <-- zero padding toàn bộ

            chunk = self.buffer[self.read_index:end_index]
            self.read_index = min(end_index, len(self.buffer))

            if len(chunk) < n_samples:
                # Pad nếu thiếu
                padding = np.zeros((n_samples - len(chunk), 2), dtype=np.int16)
                chunk = np.vstack((chunk, padding))

            return chunk.copy()



    def reset(self):
        """Reset toàn bộ buffer, dùng khi đổi ngôn ngữ hoặc clear data."""
        with self.lock:
            self.buffer = np.zeros((0, 2), dtype=np.int16)
            self.read_index = 0
