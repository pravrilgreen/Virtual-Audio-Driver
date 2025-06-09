import sys
from PySide6.QtWidgets import QApplication, QWidget, QGraphicsDropShadowEffect, QLabel
from PySide6.QtGui import QColor
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from ui_form import Ui_Widget
from speaker_monitor import SpeakerMonitorThread


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.setupUi()

        self.speaker_thread = SpeakerMonitorThread()
        self.speaker_thread.volume_signal.connect(
            lambda vol: self.update_sound_effect(self.ui.labelCustomerAvatar, vol)
        )
        self.speaker_thread.start()

    def setupUi(self):
        self.ui.setupUi(self)
        self.glow_effects = {}
        self.animations = {}

        self.add_sound_effect(self.ui.labelCustomerAvatar)
        self.add_sound_effect(self.ui.labelMeAvatar)

    def add_sound_effect(self, target_label: QLabel):
        effect = QGraphicsDropShadowEffect(self)
        effect.setColor(QColor(0, 255, 100))
        effect.setOffset(0, 0)
        effect.setBlurRadius(0)
        target_label.setGraphicsEffect(effect)
        self.glow_effects[target_label] = effect

        anim = QPropertyAnimation(effect, b"blurRadius")
        anim.setDuration(200)
        anim.setEasingCurve(QEasingCurve.InOutSine)
        self.animations[target_label] = anim

    def update_sound_effect(self, target_label: QLabel, volume: int):
        volume = max(0, min(volume, 10))
        effect = self.glow_effects.get(target_label)
        anim = self.animations.get(target_label)
        if not effect or not anim:
            return

        color = self.volume_to_color(volume)
        effect.setColor(color)

        # Nhân đôi độ blur
        target_radius = volume * 8

        anim.stop()
        if volume == 0:
            effect.setBlurRadius(0)
        else:
            anim.setStartValue(effect.blurRadius())
            anim.setEndValue(target_radius)
            anim.start()

    def volume_to_color(self, volume: int) -> QColor:
        if volume < 9:
            t = volume / 8.0 
            r = int(50 + t * 150)
            g = 255
            b = int(100 - t * 80)
        else:
            r = 255
            g = 50
            b = 20
        return QColor(r, g, b)

    def closeEvent(self, event):
        self.speaker_thread.stop()
        self.speaker_thread.wait()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
