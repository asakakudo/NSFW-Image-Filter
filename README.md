## NSFW Image Folder Filter — Desktop app (Python)

A simple desktop utility that scans a folder of images and videos and separates NSFW content from normal media into separate folders. Features:

* Upload/select a folder to scan
* Classify images and videos (video frames sampled) as NSFW or Safe
* Create separate folders for each category inside the selected folder (e.g. `safe/`, `nsfw/`)
* Option to archive results to ZIP (RAR supported if WinRAR/unrar is installed)
* System tray notifications when filtering succeeds or fails
* Minimal responsive UI built with PySide6 (Qt)
* Theme (light/dark) and language switching (English default)
* Packaged into an executable using PyInstaller

### Quick start

1. Clone the repository

```bash
git clone <repo-url>
cd nsfw-separator
```

2. Create a virtual environment and install requirements

```bash
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Install an NSFW classifier backend. This README expects `nudenet` (recommended).

```bash
pip install nudenet
```

4. Run the app

```bash
python -m app.main
```

5. Build an executable (optional)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed app/main.py
```

### Notes

* `nudenet` requires TensorFlow; use the CPU or GPU variant according to your system.
* If packaging with PyInstaller, include model files or let the app download them on first run.
* For video classification the app samples frames (configurable) — adjust for speed vs accuracy.

### License

MIT

