import numpy as np

class AudioMixer:
    def __init__(self, direct_volume=100, translated_volume=100):
        self.set_volumes(direct_volume, translated_volume)

    def set_volumes(self, direct_volume, translated_volume):
        self.direct_vol = direct_volume / 100.0
        self.translated_vol = translated_volume / 100.0

    def mix(self, direct_audio: np.ndarray, translated_audio: np.ndarray) -> np.ndarray:
        if direct_audio.shape != translated_audio.shape:
            min_len = min(len(direct_audio), len(translated_audio))
            direct_audio = direct_audio[:min_len]
            translated_audio = translated_audio[:min_len]

        mixed = (
            direct_audio.astype(np.float32) * self.direct_vol +
            translated_audio.astype(np.float32) * self.translated_vol
        )
        mixed = np.clip(mixed, -32768, 32767).astype(np.int16)
        return mixed
