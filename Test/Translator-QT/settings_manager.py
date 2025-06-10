import json
import os

SETTINGS_PATH = "config/settings.json"

DEFAULT_SETTINGS = {
    "microphone": "",
    "speaker": "",
    "microphone_level": 100,
    "speaker_level": 100,
    "direct_volume": 70,
    "translated_volume": 70,
    "llm_model": "Gemma",
    "api_url": "",
    "api_token": ""
}

class SettingsManager:
    def __init__(self):
        os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
        self.settings = DEFAULT_SETTINGS.copy()
        self.load_settings()

    def load_settings(self):
        try:
            if os.path.exists(SETTINGS_PATH):
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    self.settings.update(json.load(f))
        except Exception as e:
            print("Failed to load settings:", e)

    def save_settings(self):
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print("Failed to save settings:", e)

    def get(self, key):
        return self.settings.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        self.settings[key] = value
