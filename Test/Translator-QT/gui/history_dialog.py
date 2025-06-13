import os
import json
import requests
import threading
from datetime import datetime

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QTextEdit, QPushButton, QMessageBox, QAbstractItemView, QLabel,
    QSizePolicy, QProgressDialog
)
from PySide6.QtCore import Qt, QThread, Signal, QObject

from settings_manager import SettingsManager

try:
    from bs4 import BeautifulSoup
except ImportError:
    raise ImportError("You need to install BeautifulSoup: pip install beautifulsoup4")


class SummarizeWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, text, model, api_url, api_token):
        super().__init__()
        self.text = text
        self.model = model
        self.api_url = api_url
        self.api_token = api_token
        self._cancel_requested = threading.Event()

    def cancel(self):
        self._cancel_requested.set()

    def run(self):
        thread = threading.Thread(target=self._do_request)
        thread.start()

    def _do_request(self):
        if not self.api_url.startswith("http"):
            self.error.emit("Invalid API URL in settings. Please update it in Settings.")
            return

        prompt = (
            "Hãy đọc và tóm tắt nội dung chính của cuộc hội thoại giữa hai người dưới đây. "
            "Tóm tắt nên ngắn gọn, rõ ràng, nêu bật các ý chính đã được trao đổi, "
            "mục đích của cuộc trò chuyện và kết luận (nếu có). Vui lòng giữ văn phong trung lập và khách quan.\n\n"
            + self.text.strip()
        )

        headers = {
            "Authorization": f"Bearer {self.api_token}" if self.api_token else "",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False
        }

        try:
            with requests.Session() as session:
                response = session.post(self.api_url, headers=headers, json=payload, timeout=60)

                if self._cancel_requested.is_set():
                    return

                if response.status_code != 200:
                    self.error.emit(f"Request failed: {response.status_code} - {response.text}")
                    return

                result = response.json()
                self.finished.emit(result.get("message", result.get("response", response.text)))

        except requests.exceptions.Timeout:
            if not self._cancel_requested.is_set():
                self.error.emit("Request timed out.")
        except Exception as e:
            if not self._cancel_requested.is_set():
                self.error.emit(f"Unexpected error: {str(e)}")


class HistoryDialog(QDialog):
    def __init__(self, history_dir="history", parent=None):
        super().__init__(parent)
        self.setWindowTitle("🕘 Chat History")
        self.resize(800, 600)

        self.settings_manager = SettingsManager()
        self.history_dir = history_dir
        self.selected_file = None

        self.thread = None
        self.worker = None
        self.progress_dialog = None

        self.init_ui()
        self.load_files()

    def init_ui(self):
        self.table = QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(["Filename"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.table.setMinimumWidth(300)
        self.table.cellClicked.connect(self.load_content)
        self.table.horizontalHeader().setStretchLastSection(True)

        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)

        self.summary_view = QTextEdit()
        self.summary_view.setReadOnly(True)
        self.summary_view.setPlaceholderText("Summary will appear here...")

        self.button_delete = QPushButton("🗑 Delete")
        self.button_delete.clicked.connect(self.delete_selected)

        self.button_summary = QPushButton("🧠 Summarize")
        self.button_summary.clicked.connect(self.summarize_selected)

        layout_main = QVBoxLayout()
        layout_top = QHBoxLayout()
        layout_right = QVBoxLayout()
        layout_buttons = QHBoxLayout()

        layout_buttons.addWidget(self.button_delete)
        layout_buttons.addWidget(self.button_summary)

        layout_right.addWidget(QLabel("Chat Content:"))
        layout_right.addWidget(self.text_view)
        layout_right.addWidget(QLabel("Summary:"))
        layout_right.addWidget(self.summary_view)
        layout_right.addLayout(layout_buttons)

        layout_top.addWidget(self.table)
        layout_top.addLayout(layout_right)
        layout_main.addLayout(layout_top)
        self.setLayout(layout_main)

    def load_files(self):
        self.table.setRowCount(0)
        if not os.path.exists(self.history_dir):
            return

        files = sorted(os.listdir(self.history_dir), reverse=True)
        for i, file in enumerate(files):
            if not file.endswith(".html"):
                continue
            timestamp = file.replace("chat_", "").replace(".html", "")
            try:
                dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
                formatted = dt.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                formatted = timestamp
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(file))

    def load_content(self, row, column):
        file = self.table.item(row, 0).text()
        self.selected_file = os.path.join(self.history_dir, file)
        try:
            with open(self.selected_file, "r", encoding="utf-8") as f:
                html = f.read()
                self.text_view.setHtml(html)
                self.summary_view.clear()
        except Exception as e:
            self.text_view.setPlainText(f"Error loading file: {e}")

    def delete_selected(self):
        if not self.selected_file or not os.path.exists(self.selected_file):
            QMessageBox.warning(self, "No Selection", "Please select a history entry first.")
            return

        confirm = QMessageBox.question(
            self, "Delete Confirmation",
            f"Do you really want to delete:\n{os.path.basename(self.selected_file)}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                os.remove(self.selected_file)
                self.text_view.clear()
                self.summary_view.clear()
                self.load_files()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete: {e}")

    def summarize_selected(self):
        if not self.selected_file or not os.path.exists(self.selected_file):
            QMessageBox.warning(self, "No Selection", "Please select a history entry first.")
            return

        if self.worker:
            QMessageBox.information(self, "Please Wait", "Summarization is already in progress.")
            return

        try:
            with open(self.selected_file, "r", encoding="utf-8") as f:
                html_content = f.read()
                plain_text = self.html_to_text(html_content)

            model = self.settings_manager.get("llm_model")
            api_url = self.settings_manager.get("api_url").strip()
            api_token = self.settings_manager.get("api_token").strip()

            self.worker = SummarizeWorker(plain_text, model, api_url, api_token)
            self.worker.finished.connect(self.on_summary_finished)
            self.worker.error.connect(self.on_summary_error)

            self.progress_dialog = QProgressDialog("Summarizing chat, please wait...", "Cancel", 0, 0, self)
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.setMinimumDuration(0)
            self.progress_dialog.setCancelButtonText("Cancel")
            self.progress_dialog.setWindowTitle("Working...")
            self.progress_dialog.canceled.connect(self.cancel_summary)
            self.progress_dialog.show()

            self.worker.run()

        except Exception as e:
            self.summary_view.setPlainText(f"Error summarizing: {e}")

    def cancel_summary(self):
        if self.worker:
            self.worker.cancel()
        if self.progress_dialog:
            self.progress_dialog.close()
        self.cleanup_summary()

    def on_summary_finished(self, result):
        if self.progress_dialog:
            self.progress_dialog.close()
        self.summary_view.setPlainText(result)
        self.cleanup_summary()

    def on_summary_error(self, message):
        if self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.critical(self, "Error", message)
        self.cleanup_summary()

    def cleanup_summary(self):
        self.worker = None
        self.progress_dialog = None

    def closeEvent(self, event):
        if self.worker:
            self.worker.cancel()
        event.accept()

    def html_to_text(self, html):
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text()
