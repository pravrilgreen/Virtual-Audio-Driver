import sys
import math
import numpy as np

from PySide6.QtWidgets import QApplication, QWidget, QLabel, QGraphicsDropShadowEffect
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve

from ui_form import Ui_Widget
from speaker_monitor import SpeakerMonitorThread
from mic_monitor import MicMonitorThread
from settings_dialog import SettingsDialog
from settings_manager import SettingsManager


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.mic_thread = None
        self.mic_on = False
        self.ui = Ui_Widget()
        self.setupUi()
        self.settings_manager = SettingsManager()

        # Start speaker monitor
        self.speaker_thread = SpeakerMonitorThread()
        self.speaker_thread.volume_signal.connect(
            lambda vol: self.update_sound_effect(self.ui.labelCustomerAvatar, vol)
        )
        self.speaker_thread.start()

        # Start mic monitor thread immediately with saved mic
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

        # UI Buttons
        self.ui.buttonNewConversation.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
        self.ui.buttonMicToggle.setStyleSheet("background-color: gray; color: white; font-weight: bold;")
        self.ui.labelMic.setEnabled(False)

        self.ui.buttonMicToggle.clicked.connect(self.toggle_mic)
        self.ui.buttonNewConversation.clicked.connect(self.new_conversation)
        self.ui.buttonSettings.clicked.connect(self.settings_dialog)

    def start_initial_mic_thread(self):
        mic_device_name = self.settings_manager.get("microphone", "")
        print(f"[INIT] Starting mic thread with device: {mic_device_name}")
        self.mic_thread = MicMonitorThread(input_device_name=mic_device_name)
        self.mic_thread.volume_signal.connect(
            lambda vol: self.update_sound_effect(self.ui.labelMeAvatar, vol)
        )
        self.mic_thread.start()

    def toggle_mic(self):
        if self.mic_on:
            print("Live Translate: OFF")
            self.ui.buttonMicToggle.setText("Live Translate: OFF")
            self.ui.buttonMicToggle.setStyleSheet("background-color: gray; color: white; font-weight: bold;")
            self.ui.labelMic.setEnabled(False)
        else:
            print("Live Translate: ON")
            self.ui.buttonMicToggle.setText("Live Translate: ON")
            self.ui.buttonMicToggle.setStyleSheet("background-color: green; color: white; font-weight: bold;")
            self.ui.labelMic.setEnabled(True)
        self.mic_on = not self.mic_on

    def restart_mic_thread(self):
        mic_device_name = self.settings_manager.get("microphone", "")
        print(f"[Mic] Restarting thread with: {mic_device_name}")

        if self.mic_thread:
            self.mic_thread.stop()
            self.mic_thread.wait()

        self.mic_thread = MicMonitorThread(input_device_name=mic_device_name)
        self.mic_thread.volume_signal.connect(
            lambda vol: self.update_sound_effect(self.ui.labelMeAvatar, vol)
        )
        self.mic_thread.start()

    def settings_dialog(self):
        dialog = SettingsDialog(self)
        old_mic_device = self.settings_manager.get("microphone", "")

        if dialog.exec():
            new_mic_device = dialog.get_selected_microphone()
            print(f"[SETTINGS] Selected mic: {new_mic_device}")

            if new_mic_device != old_mic_device:
                print("[SETTINGS] Mic device changed, restarting mic thread.")
                self.settings_manager.set("microphone", new_mic_device)
                self.restart_mic_thread()
            else:
                print("[SETTINGS] Mic device unchanged.")

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

        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
