from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSlider, QLineEdit,
    QFormLayout, QPushButton, QGroupBox, QMessageBox, QGridLayout
)
from PySide6.QtCore import Qt

from settings_manager import SettingsManager
from devices.audio_devices import list_input_devices, list_output_devices


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(500, 420)

        self.settings_manager = SettingsManager()

        self.setup_ui()
        self.load_settings()

        self.ok_btn.clicked.connect(self.validate_and_accept)
        self.cancel_btn.clicked.connect(self.reject)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # === Device Settings (mic, speaker, levels) ===
        device_group = QGroupBox("Device Settings")
        device_layout = QGridLayout()

        self.microphone_combo = QComboBox()
        self.microphone_combo.addItems(list_input_devices())

        self.microphone_level_slider = QSlider(Qt.Horizontal)
        self.microphone_level_slider.setRange(0, 100)

        self.speaker_combo = QComboBox()
        self.speaker_combo.addItems(list_output_devices())

        self.speaker_level_slider = QSlider(Qt.Horizontal)
        self.speaker_level_slider.setRange(0, 100)

        device_layout.addWidget(QLabel("Microphone:"), 0, 0)
        device_layout.addWidget(self.microphone_combo, 0, 1)

        device_layout.addWidget(QLabel("Mic Level:"), 1, 0)
        device_layout.addWidget(self.microphone_level_slider, 1, 1)

        device_layout.addWidget(QLabel("Speaker:"), 2, 0)
        device_layout.addWidget(self.speaker_combo, 2, 1)

        device_layout.addWidget(QLabel("Speaker Level:"), 3, 0)
        device_layout.addWidget(self.speaker_level_slider, 3, 1)

        device_group.setLayout(device_layout)

        # === Audio Mixer ===
        mixer_group = QGroupBox("Audio Mixer")
        mixer_layout = QGridLayout()

        self.direct_audio_slider = QSlider(Qt.Horizontal)
        self.direct_audio_slider.setRange(0, 100)

        self.translated_audio_slider = QSlider(Qt.Horizontal)
        self.translated_audio_slider.setRange(0, 100)

        mixer_layout.addWidget(QLabel("Direct Volume:"), 0, 0)
        mixer_layout.addWidget(self.direct_audio_slider, 0, 1)

        mixer_layout.addWidget(QLabel("Translated Volume:"), 1, 0)
        mixer_layout.addWidget(self.translated_audio_slider, 1, 1)

        mixer_group.setLayout(mixer_layout)

        # === LLM Settings ===
        llm_group = QGroupBox("LLM Model Settings")
        llm_layout = QFormLayout()

        self.model_combo = QComboBox()
        self.model_combo.addItems(["Gemma3:12b"])

        self.api_url_input = QLineEdit()
        self.api_token_input = QLineEdit()
        self.api_token_input.setEchoMode(QLineEdit.Password)

        llm_layout.addRow("Model:", self.model_combo)
        llm_layout.addRow("API URL:", self.api_url_input)
        llm_layout.addRow("API Token:", self.api_token_input)

        llm_group.setLayout(llm_layout)

        # === Buttons ===
        button_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.cancel_btn = QPushButton("Cancel")
        button_layout.addStretch()
        button_layout.addWidget(self.ok_btn)
        button_layout.addWidget(self.cancel_btn)

        # === Main Layout ===
        layout.addWidget(device_group)
        layout.addWidget(mixer_group)
        layout.addWidget(llm_group)
        layout.addLayout(button_layout)

    def load_settings(self):
        s = self.settings_manager
        self.microphone_combo.setCurrentText(s.get("microphone"))
        self.speaker_combo.setCurrentText(s.get("speaker"))
        self.direct_audio_slider.setValue(s.get("direct_volume"))
        self.translated_audio_slider.setValue(s.get("translated_volume"))
        self.microphone_level_slider.setValue(s.get("microphone_level"))
        self.speaker_level_slider.setValue(s.get("speaker_level"))
        self.model_combo.setCurrentText(s.get("llm_model"))
        self.api_url_input.setText(s.get("api_url"))
        self.api_token_input.setText(s.get("api_token"))

    def validate_and_accept(self):
        url = self.api_url_input.text().strip()
        token = self.api_token_input.text().strip()

        if not url.startswith("http"):
            QMessageBox.warning(self, "Validation Error", "API URL must start with http or https.")
            return
        if not token:
            QMessageBox.warning(self, "Validation Error", "API Token cannot be empty.")
            return

        s = self.settings_manager
        s.set("microphone", self.microphone_combo.currentText())
        s.set("speaker", self.speaker_combo.currentText())
        s.set("direct_volume", self.direct_audio_slider.value())
        s.set("translated_volume", self.translated_audio_slider.value())
        s.set("microphone_level", self.microphone_level_slider.value())
        s.set("speaker_level", self.speaker_level_slider.value())
        s.set("llm_model", self.model_combo.currentText())
        s.set("api_url", url)
        s.set("api_token", token)
        s.save_settings()

        self.accept()

    def get_selected_microphone(self):
        return self.microphone_combo.currentText()