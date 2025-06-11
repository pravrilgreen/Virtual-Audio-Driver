from modules.utils import load_wav_base64

def text_to_speech(text: str) -> str:
    """Dummy TTS: giả lập TTS bằng cách load sample.wav"""
    return load_wav_base64("sample.wav")
