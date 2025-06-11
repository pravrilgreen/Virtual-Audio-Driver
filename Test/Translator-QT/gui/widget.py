import sys
import math
import numpy as np
import time
import threading
import librosa
import soundfile as sf

from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve

from gui.ui_form import Ui_Widget
import gui.rc_resources
from core.speaker_monitor import SpeakerMonitorThread
from core.mic_monitor import MicMonitorThread, VirtualMicWriter, PCMPlayerThread
from gui.settings_dialog import SettingsDialog
from settings_manager import SettingsManager
from core.virtual_audio import VirtualSpeakerKeepAlive, VirtualMicKeepAlive
from devices.audio_devices import find_output_device_index_by_name

def wav_to_pcm_bytes(wav_path: str) -> bytes:
    data, sr = sf.read(wav_path, always_2d=True)

    # Resample if needed
    if sr != 48000:
        data = librosa.resample(data.T, orig_sr=sr, target_sr=48000).T

    # Mono → stereo if needed
    if data.shape[1] == 1:
        data = np.repeat(data, 2, axis=1)

    # Normalize and convert to int32
    data = np.clip(data, -1.0, 1.0)
    pcm_data = (data * 2147483647).astype(np.int32)
    return pcm_data.tobytes()

class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mic_thread = None
        self.pcm_thread = None
        self.mic_on = False
        self.ui = Ui_Widget()
        self.setupUi()
        self.settings_manager = SettingsManager()

        # === Virtual Devices Keep Alive ===
        self.virtual_mic_keepalive = VirtualMicKeepAlive("Virtual Audio Device - NS Team")
        self.virtual_mic_keepalive.start()
        self.virtual_speaker_keepalive = VirtualSpeakerKeepAlive("Virtual Audio Device - NS Team")
        self.virtual_speaker_keepalive.start()

        # === Virtual Mic Writer ===
        self.virtual_writer = VirtualMicWriter()
        self.virtual_writer.start()

        # === Speaker Monitor Thread ===
        from devices.audio_devices import find_output_device_index_by_name
        speaker_device_name = self.settings_manager.get("speaker", "")
        speaker_device_index = find_output_device_index_by_name(speaker_device_name)

        self.speaker_thread = SpeakerMonitorThread()
        self.speaker_thread.output_device_index = speaker_device_index
        self.speaker_thread.volume_signal.connect(
            lambda vol: self.update_sound_effect(self.ui.labelCustomerAvatar, vol)
        )
        self.speaker_thread.start()

        # === Mic Monitor Thread ===
        self.start_initial_mic_thread()


    def setupUi(self):
        self.ui.setupUi(self)
        self.glow_effects = {}
        self.animations = {}

        self.add_sound_effect(self.ui.labelCustomerAvatar)
        self.add_sound_effect(self.ui.labelMeAvatar)

        self.avatar_size_animation = QPropertyAnimation(self.ui.labelCustomerAvatar, b"geometry")
        self.avatar_size_animation.setDuration(200)
        self.avatar_size_animation.setEasingCurve(QEasingCurve.InOutQuad)

        self.ui.buttonNewConversation.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
        self.ui.buttonMicToggle.setStyleSheet("background-color: gray; color: white; font-weight: bold;")
        self.ui.labelMic.setEnabled(False)

        self.ui.buttonMicToggle.clicked.connect(self.toggle_mic)
        self.ui.buttonNewConversation.clicked.connect(self.new_conversation)
        self.ui.buttonSettings.clicked.connect(self.settings_dialog)

    def start_initial_mic_thread(self):
        mic_device_name = self.settings_manager.get("microphone", "")
        print(f"[INIT] Starting mic thread with device: {mic_device_name}")
        self.mic_thread = MicMonitorThread(
            input_device_name=mic_device_name,
            writer=self.virtual_writer,
            push_to_virtual=True
        )
        self.mic_thread.volume_signal.connect(
            lambda vol: self.update_sound_effect(self.ui.labelMeAvatar, vol)
        )
        self.mic_thread.start()


    def toggle_mic(self):
        if self.mic_on:
            # === Disable live translation ===
            print("Live Translate: OFF")
            self.ui.buttonMicToggle.setText("Live Translate: OFF")
            self.ui.buttonMicToggle.setStyleSheet("background-color: gray; color: white; font-weight: bold;")
            self.ui.labelMic.setEnabled(False)

            # Stop translated audio playback (if any)
            if self.pcm_thread:
                self.pcm_thread.stop()
                self.pcm_thread.join()
                self.pcm_thread = None

            # Enable direct mic passthrough to virtual mic
            if self.mic_thread:
                self.mic_thread.set_virtual_output_enabled(True)

            # Disable translation (stop sending speaker audio to socket)
            self.speaker_thread.set_translation_enabled(False)

        else:
            # === Enable live translation ===
            print("Live Translate: ON")
            self.ui.buttonMicToggle.setText("Live Translate: ON")
            self.ui.buttonMicToggle.setStyleSheet("background-color: green; color: white; font-weight: bold;")
            self.ui.labelMic.setEnabled(True)

            if self.mic_thread:
                self.mic_thread.set_virtual_output_enabled(False)

                def on_translated_audio(data_bytes):
                    if self.mic_thread:
                        self.mic_thread.set_translated_audio(data_bytes)

                self.speaker_thread.ws_client.register_audio_callback(on_translated_audio)

            self.speaker_thread.set_translation_enabled(True)

        self.mic_on = not self.mic_on

    def restart_mic_thread(self):
        mic_device_name = self.settings_manager.get("microphone", "")
        print(f"[Mic] Restarting thread with: {mic_device_name}")

        if self.mic_thread:
            self.mic_thread.stop()
            self.mic_thread.wait()

        self.mic_thread = MicMonitorThread(
            input_device_name=mic_device_name,
            writer=self.virtual_writer,
            push_to_virtual=True
        )
        self.mic_thread.volume_signal.connect(
            lambda vol: self.update_sound_effect(self.ui.labelMeAvatar, vol)
        )
        self.mic_thread.start()


    def settings_dialog(self):
        dialog = SettingsDialog(self)
        old_mic_device = self.settings_manager.get("microphone", "")
        old_speaker_device = self.settings_manager.get("speaker", "")

        if dialog.exec():
            new_mic_device = dialog.get_selected_microphone()
            new_speaker_device = dialog.speaker_combo.currentText()

            # Mic changed
            if new_mic_device != old_mic_device:
                print("[SETTINGS] Mic device changed, restarting mic thread.")
                self.settings_manager.set("microphone", new_mic_device)
                self.restart_mic_thread()
            else:
                print("[SETTINGS] Mic device unchanged.")

            # Speaker changed
            if new_speaker_device != old_speaker_device:
                print("[SETTINGS] Speaker device changed, updating speaker thread.")
                self.settings_manager.set("speaker", new_speaker_device)
                self.restart_speaker_thread()
            else:
                print("[SETTINGS] Speaker device unchanged.")


    def restart_speaker_thread(self):
        speaker_device_name = self.settings_manager.get("speaker", "")
        from devices.audio_devices import find_output_device_index_by_name
        index = find_output_device_index_by_name(speaker_device_name)

        if self.speaker_thread:
            self.speaker_thread.stop()
            self.speaker_thread.wait()

        self.speaker_thread = SpeakerMonitorThread()
        self.speaker_thread.output_device_index = index
        self.speaker_thread.volume_signal.connect(
            lambda vol: self.update_sound_effect(self.ui.labelCustomerAvatar, vol)
        )
        self.speaker_thread.start()

    def new_conversation(self):
        print("New conversation started")
        self.ui.textChatBox.clear()
        self.ui.textSummaryBox.clear()

    def add_sound_effect(self, target_label: QLabel):
        target_label.setStyleSheet("""
            border: 3px solid white;
            border-radius: 25px;
        """)

        effect = QGraphicsDropShadowEffect(self)
        effect.setColor(QColor(0, 255, 255))
        effect.setOffset(0, 0)
        effect.setBlurRadius(0)
        target_label.setGraphicsEffect(effect)
        self.glow_effects[target_label] = effect

        anim = QPropertyAnimation(effect, b"blurRadius")
        anim.setDuration(300)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.setLoopCount(-1)
        self.animations[target_label] = anim

    def update_sound_effect(self, target_label: QLabel, volume: int):
        effect = self.glow_effects.get(target_label)
        anim = self.animations.get(target_label)
        if not effect or not anim:
            return

        effect.setColor(self.volume_to_color(volume))

        min_radius = volume * 0.5
        max_radius = volume * 1.0 + 10

        anim.stop()
        anim.setStartValue(min_radius)
        anim.setEndValue(max_radius)
        anim.start()

    def volume_to_color(self, volume: int) -> QColor:
        if volume < 20:
            return QColor(0, 255, 255)
        elif volume < 50:
            return QColor(0, 200, 150)
        elif volume < 70:
            return QColor(0, 255, 0)
        elif volume < 90:
            return QColor(255, 165, 0)
        else:
            return QColor(255, 0, 0)

    def closeEvent(self, event):
        self.speaker_thread.stop()
        self.speaker_thread.wait()

        if self.mic_thread:
            self.mic_thread.stop()
            self.mic_thread.wait()

        if self.virtual_mic_keepalive:
            self.virtual_mic_keepalive.stop()

        if self.virtual_speaker_keepalive:
            self.virtual_speaker_keepalive.stop()

        if self.pcm_thread:
            self.pcm_thread.stop()

        super().closeEvent(event)

