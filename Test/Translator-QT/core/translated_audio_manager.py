import threading
import numpy as np
from pydub import AudioSegment
import io
import queue


class TranslatedAudioManager:
    def __init__(self, chunk_size: int = 1024, sample_rate: int = 48000):
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.file_queue = queue.Queue()
        self.current_chunks = []
        self.chunk_index = 0
        self.lock = threading.Lock()

    def add_wav(self, wav_bytes: bytes):
        """
        Parse a WAV file and split it into fixed-size stereo chunks (int16).
        """
        try:
            audio = AudioSegment.from_file(io.BytesIO(wav_bytes), format="wav")
            audio = audio.set_channels(2).set_sample_width(2).set_frame_rate(self.sample_rate)
            samples = np.frombuffer(audio.raw_data, dtype=np.int16).reshape(-1, 2)

            chunks = [samples[i:i + self.chunk_size]
                      for i in range(0, len(samples), self.chunk_size)]

            with self.lock:
                self.file_queue.put(chunks)
        except Exception as e:
            print(f"[TranslatedAudioManager] Failed to decode WAV: {e}")

    def get_next_chunk(self) -> np.ndarray:
        """
        Return the next chunk of translated audio, or silence if none.
        """
        with self.lock:
            if not self.current_chunks or self.chunk_index >= len(self.current_chunks):
                if self.file_queue.empty():
                    return np.zeros((self.chunk_size, 2), dtype=np.int16)
                self.current_chunks = self.file_queue.get()
                self.chunk_index = 0

            chunk = self.current_chunks[self.chunk_index]
            self.chunk_index += 1

            if chunk.shape[0] < self.chunk_size:
                pad = np.zeros((self.chunk_size - chunk.shape[0], 2), dtype=np.int16)
                chunk = np.vstack((chunk, pad))

            return chunk