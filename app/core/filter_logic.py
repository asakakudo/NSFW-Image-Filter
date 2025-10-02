# File: app/core/filter_logic.py

import os
import shutil
from nsfw_detector import predict
from PIL import Image

# Muat model AI sekali saja saat modul diimpor untuk efisiensi
# Ini mungkin akan memakan waktu beberapa detik saat pertama kali aplikasi dijalankan
print("Memuat model AI untuk deteksi NSFW...")
model = predict.load_model('./nsfw_mobilenet_v2.224x224.h5')
print("Model AI berhasil dimuat.")

def classify_image(image_path):
    """
    Menganalisis satu gambar dan mengklasifikasikannya sebagai 'nsfw' atau 'sfw'.

    Args:
        image_path (str): Path lengkap ke file gambar.

    Returns:
        str: 'nsfw' atau 'sfw'. Mengembalikan 'error' jika file tidak dapat diproses.
    """
    try:
        # Pastikan file adalah gambar yang valid sebelum diproses
        Image.open(image_path).verify() 
        
        predictions = predict.classify(model, image_path)
        
        # 'predictions' adalah dictionary, contoh:
        # {'hentai': 0.9, 'porn': 0.05, 'sexy': 0.03, 'drawings': 0.01, 'neutral': 0.01}
        
        nsfw_score = predictions[image_path]['porn'] + predictions[image_path]['hentai']
        
        # Tentukan ambang batas (threshold). Jika skor 'porn' + 'hentai' > 50%, anggap NSFW.
        if nsfw_score > 0.5:
            return 'nsfw'
        else:
            return 'sfw'
            
    except Exception as e:
        print(f"Error saat memproses file {os.path.basename(image_path)}: {e}")
        return 'error'

def filter_folder_generator(folder_path):
    """
    Memindai folder, mengklasifikasi setiap gambar, dan memindahkannya.
    Fungsi ini adalah 'generator' yang akan 'yield' status progresnya.

    Args:
        folder_path (str): Path ke folder yang akan difilter.

    Yields:
        dict: Kamus berisi status progres (total file, file saat ini, nama file).
    """
    # Tentukan path untuk folder hasil
    base_folder = os.path.dirname(folder_path)
    nsfw_folder = os.path.join(base_folder, "NSFW_Results")
    sfw_folder = os.path.join(base_folder, "SFW_Results")

    # Buat folder jika belum ada
    os.makedirs(nsfw_folder, exist_ok=True)
    os.makedirs(sfw_folder, exist_ok=True)

    # Dapatkan daftar file gambar yang didukung
    supported_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp')
    files_to_process = [f for f in os.listdir(folder_path) if f.lower().endswith(supported_extensions)]
    
    total_files = len(files_to_process)
    
    # Mulai proses dan yield progresnya
    for i, filename in enumerate(files_to_process):
        current_file_path = os.path.join(folder_path, filename)
        
        # Kirim update progres ke UI sebelum memproses
        yield {
            'total': total_files,
            'current': i + 1,
            'filename': filename
        }

        # Klasifikasi gambar
        category = classify_image(current_file_path)

        # Pindahkan file berdasarkan kategori
        if category == 'nsfw':
            shutil.move(current_file_path, os.path.join(nsfw_folder, filename))
        elif category == 'sfw':
            shutil.move(current_file_path, os.path.join(sfw_folder, filename))
        # Jika 'error', biarkan file di folder aslinya

    # Kirim pesan selesai
    yield {'status': 'completed', 'total': total_files}