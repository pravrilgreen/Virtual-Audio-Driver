from modules.speech_to_text import speech_to_text
from modules.translate import translate_text
from modules.text_to_speech import text_to_speech

def process_audio_pipeline(pcm_bytes: bytes, header: dict) -> dict:
    role = header.get("sender", "unknown")
    src_lang = header.get("src_lang", "auto")
    tgt_lang = header.get("tgt_lang", "en")

    # 1. STT (dummy)
    text = speech_to_text(pcm_bytes, role)

    # 2. Translate (dummy)
    translated = translate_text(text, src_lang, tgt_lang)

    # 3. TTS (dummy)
    wav_b64 = text_to_speech(translated)

    return {
        "role": role,
        "text": translated,
        "tts_audio": wav_b64
    }
