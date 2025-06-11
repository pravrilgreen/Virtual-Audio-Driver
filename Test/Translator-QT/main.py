import sys
from PySide6.QtWidgets import QApplication
from gui.widget import Widget

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Widget()
    window.show()
    sys.exit(app.exec())