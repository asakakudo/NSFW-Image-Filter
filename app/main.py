# File: app/main.py

from app.ui.main_window import MainWindow

if __name__ == "__main__":
    # Membuat instance dari jendela utama kita
    app = MainWindow()
    # Menjalankan event loop aplikasi (membuat jendela tetap terbuka)
    app.mainloop()