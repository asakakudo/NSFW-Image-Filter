# File: app/ui/main_window.py

import customtkinter
import threading  # --- BARU ---: Impor untuk multithreading
from tkinter import filedialog
from app.core.filter_logic import filter_folder_generator # --- BARU ---

class MainWindow(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        # ... (kode __init__ yang sudah ada tidak perlu diubah) ...
        # --- Konfigurasi Jendela Utama ---
        self.title("Aplikasi Filter NSFW")
        self.geometry("700x500")
        self.minsize(500, 300)

        self.selected_folder_path = ""

        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")

        self.main_frame = customtkinter.CTkFrame(self)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.title_label = customtkinter.CTkLabel(
            self.main_frame, text="Selamat Datang di Aplikasi Filter NSFW",
            font=customtkinter.CTkFont(size=20, weight="bold"))
        self.title_label.pack(padx=20, pady=(20, 10))

        self.upload_button = customtkinter.CTkButton(
            self.main_frame, text="Pilih Folder untuk Difilter", command=self.select_folder_event)
        self.upload_button.pack(padx=20, pady=10)

        self.start_button = customtkinter.CTkButton(
            self.main_frame, text="Mulai Filter", command=self.start_filtering_event, state="disabled")
        self.start_button.pack(padx=20, pady=10)

        self.progress_bar = customtkinter.CTkProgressBar(self.main_frame)
        self.progress_bar.pack(padx=20, pady=10, fill="x", expand=False)
        self.progress_bar.set(0)

        self.status_label = customtkinter.CTkLabel(
            self.main_frame, text="Silakan pilih folder untuk memulai.")
        self.status_label.pack(padx=20, pady=(10, 20))

    def select_folder_event(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.selected_folder_path = folder_path
            display_path = folder_path if len(folder_path) < 50 else "..." + folder_path[-47:]
            self.status_label.configure(text=f"Folder dipilih: {display_path}")
            self.start_button.configure(state="normal")
        else:
            self.status_label.configure(text="Pemilihan folder dibatalkan.")
            self.start_button.configure(state="disabled")

    def start_filtering_event(self):
        """
        Memulai proses filter dengan membuat thread baru.
        """
        if not self.selected_folder_path:
            self.status_label.configure(text="Error: Tidak ada folder yang dipilih!")
            return

        self.status_label.configure(text="Memulai proses filter...")
        self.upload_button.configure(state="disabled")
        self.start_button.configure(state="disabled")
        self.progress_bar.set(0)

        # --- BARU ---: Buat dan jalankan thread untuk proses filter
        filter_thread = threading.Thread(
            target=self.run_filter_in_thread,
            args=(self.selected_folder_path,)
        )
        filter_thread.daemon = True  # Agar thread berhenti saat aplikasi ditutup
        filter_thread.start()

    # --- BARU ---
    def run_filter_in_thread(self, folder_path):
        """
        Fungsi ini berjalan di background thread dan memanggil generator filter.
        """
        try:
            for progress in filter_folder_generator(folder_path):
                # Kirim update ke main thread untuk memperbarui UI
                self.after(0, self.update_ui, progress)
        except Exception as e:
            # Menangani error yang mungkin terjadi di dalam thread
            self.after(0, self.update_ui, {'status': 'error', 'message': str(e)})

    # --- BARU ---
    def update_ui(self, progress_data):
        """
        Fungsi ini berjalan di main thread untuk memperbarui UI dengan aman.
        """
        if 'status' in progress_data:
            if progress_data['status'] == 'completed':
                self.status_label.configure(text=f"Selesai! {progress_data['total']} file berhasil diproses.")
                self.progress_bar.set(1) # Progress bar penuh
            elif progress_data['status'] == 'error':
                self.status_label.configure(text=f"Terjadi Error: {progress_data['message']}")
            
            # Aktifkan kembali tombol setelah selesai atau error
            self.upload_button.configure(state="normal")
            self.start_button.configure(state="normal")
        else:
            # Update progres selama proses berjalan
            current = progress_data['current']
            total = progress_data['total']
            filename = progress_data['filename']
            
            progress_value = current / total
            self.progress_bar.set(progress_value)
            
            self.status_label.configure(text=f"Memproses [{current}/{total}]: {filename}")