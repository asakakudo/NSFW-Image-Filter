import sys
import os
from pathlib import Path
from PySide6 import QtCore, QtGui, QtWidgets

from .worker import Worker

I18N = {
    "en": {
        "title": "NSFW Separator",
        "select_folder": "Select Folder",
        "start": "Start Scan",
        "theme": "Theme",
        "language": "Language",
        "archive_zip": "Create ZIP after filter",
        "status_idle": "Idle",
        "scanning": "Scanning...",
        "done": "Done",
        "choose_folder": "Choose a folder to scan",
        "success_finished": "Filtering finished",
        "failed_finished": "Filtering finished with errors",
        "minimize_to_tray": "App minimized to tray.",
    },
    "id": {
        "title": "Pemilah NSFW",
        "select_folder": "Pilih Folder",
        "start": "Mulai Pindai",
        "theme": "Tema",
        "language": "Bahasa",
        "archive_zip": "Buat ZIP setelah filter",
        "status_idle": "Siap",
        "scanning": "Memindai...",
        "done": "Selesai",
        "choose_folder": "Pilih folder untuk dipindai",
        "success_finished": "Penyaringan selesai",
        "failed_finished": "Penyaringan selesai dengan error",
        "minimize_to_tray": "Aplikasi diminimized ke tray.",
    }
}

LIGHT_STYLE = """
QWidget { font-family: Arial; font-size: 12px; }
"""
DARK_STYLE = """
QWidget { background: #111; color: #eee; }
"""


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.lang = "en"
        self.trans = I18N[self.lang]
        self.setWindowTitle(self.trans["title"])
        self.resize(640, 300)
        self.folder = None
        self.worker = None
        self.setup_ui()
        self.setup_tray()

    def setup_ui(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        v = QtWidgets.QVBoxLayout(central)
        h = QtWidgets.QHBoxLayout()
        self.folder_edit = QtWidgets.QLineEdit()
        btn = QtWidgets.QPushButton(self.trans["select_folder"])
        btn.clicked.connect(self.on_browse)
        h.addWidget(self.folder_edit)
        h.addWidget(btn)
        v.addLayout(h)
        opts = QtWidgets.QHBoxLayout()
        self.zip_cb = QtWidgets.QCheckBox(self.trans["archive_zip"])
        opts.addWidget(self.zip_cb)
        opts.addStretch()
        v.addLayout(opts)
        c = QtWidgets.QHBoxLayout()
        self.start_btn = QtWidgets.QPushButton(self.trans["start"])
        self.start_btn.clicked.connect(self.on_start)
        self.theme_combo = QtWidgets.QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_change)
        self.lang_combo = QtWidgets.QComboBox()
        self.lang_combo.addItems(["English", "Bahasa Indonesia"])
        self.lang_combo.currentIndexChanged.connect(self.on_lang_change)
        c.addWidget(self.start_btn)
        c.addWidget(QtWidgets.QLabel(self.trans["theme"]))
        c.addWidget(self.theme_combo)
        c.addWidget(QtWidgets.QLabel(self.trans["language"]))
        c.addWidget(self.lang_combo)
        c.addStretch()
        v.addLayout(c)
        self.progress = QtWidgets.QProgressBar()
        self.status = QtWidgets.QLabel(self.trans["status_idle"])
        v.addWidget(self.progress)
        v.addWidget(self.status)

    def setup_tray(self):
        self.tray = QtWidgets.QSystemTrayIcon(self)
        icon = self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon)
        self.tray.setIcon(icon)
        menu = QtWidgets.QMenu()
        menu.addAction("Show", self.showNormal)
        menu.addAction("Quit", QtWidgets.QApplication.quit)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def on_browse(self):
        dlg = QtWidgets.QFileDialog(self, self.trans["select_folder"])
        dlg.setFileMode(QtWidgets.QFileDialog.Directory)
        if dlg.exec():
            sel = dlg.selectedFiles()
            if sel:
                self.folder_edit.setText(sel[0])

    def on_start(self):
        folder = self.folder_edit.text().strip()
        if not folder or not Path(folder).is_dir():
            QtWidgets.QMessageBox.warning(self, self.trans["title"], self.trans["choose_folder"])
            return
        self.start_btn.setEnabled(False)
        self.worker = Worker(folder, use_detector=True, zip_after=self.zip_cb.isChecked())
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.status.setText(self.trans["scanning"])
        self.progress.setValue(0)
        self.worker.start()

    def on_progress(self, done, total, fname):
        pct = int(done / total * 100) if total else 0
        self.progress.setValue(pct)
        self.status.setText(f"{self.trans['scanning']} ({done}/{total}) - {fname}")

    def on_finished(self, success, failed):
        self.start_btn.setEnabled(True)
        self.status.setText(self.trans["done"])
        if failed == 0:
            self.tray.showMessage(self.trans["success_finished"], f"{success} processed.")
        else:
            self.tray.showMessage(self.trans["failed_finished"], f"{success} success, {failed} failed.")
        # open results folder
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(Path(self.folder_edit.text() ))) )

    def on_error(self, msg):
        QtWidgets.QMessageBox.critical(self, self.trans["title"], msg)

    def on_theme_change(self, txt):
        if txt.lower() == "dark":
            self.setStyleSheet(DARK_STYLE)
        else:
            self.setStyleSheet(LIGHT_STYLE)

    def on_lang_change(self, idx):
        self.lang = "en" if idx == 0 else "id"
        self.trans = I18N[self.lang]
        # Minimal label updates
        self.setWindowTitle(self.trans["title"])
        self.start_btn.setText(self.trans["start"])
        self.zip_cb.setText(self.trans["archive_zip"])
        self.status.setText(self.trans["status_idle"])


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()