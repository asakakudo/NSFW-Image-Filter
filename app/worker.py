from PySide6 import QtCore
from pathlib import Path
import shutil
import os
from .utils import safe_copy, make_zip

# optional: import cv2 if available
try:
    import cv2
    OPENCV_AVAILABLE = True
except Exception:
    cv2 = None
    OPENCV_AVAILABLE = False

from .detector import NSFWDetector

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".webm", ".flv"}


class Worker(QtCore.QThread):
    progress = QtCore.Signal(int, int, str)
    finished = QtCore.Signal(int, int)
    error = QtCore.Signal(str)

    def __init__(self, folder: str, use_detector: bool = True, zip_after: bool = False, sample_frames: int = 3, nsfw_threshold: float = 0.6):
        super().__init__()
        self.folder = Path(folder)
        self.use_detector = use_detector
        self.zip_after = zip_after
        self.sample_frames = sample_frames
        self.nsfw_threshold = nsfw_threshold
        self._stop = False
        self.detector = None
        if use_detector:
            try:
                self.detector = NSFWDetector()
            except Exception as e:
                self.detector = None

    def run(self):
        try:
            files = [p for p in self.folder.rglob("*") if p.is_file() and p.suffix.lower() in (IMAGE_EXTS | VIDEO_EXTS)]
            total = len(files)
            if total == 0:
                self.finished.emit(0, 0)
                return
            safe_dir = self.folder / "safe"
            nsfw_dir = self.folder / "nsfw"
            safe_dir.mkdir(exist_ok=True)
            nsfw_dir.mkdir(exist_ok=True)
            done = 0
            failed = 0
            for p in files:
                if self._stop:
                    break
                done += 1
                try:
                    score = 0.0
                    if p.suffix.lower() in IMAGE_EXTS:
                        if self.detector:
                            score = self.detector.classify_image(str(p))
                    else:
                        # video
                        if OPENCV_AVAILABLE and self.detector:
                            score = self._classify_video(str(p))
                    target = nsfw_dir if score >= self.nsfw_threshold else safe_dir
                    safe_copy(p, target)
                except Exception as e:
                    failed += 1
                self.progress.emit(done, total, p.name)
            if self.zip_after:
                try:
                    make_zip(self.folder / "results.zip", [safe_dir, nsfw_dir])
                except Exception:
                    pass
            self.finished.emit(max(0, total - failed), failed)
        except Exception as e:
            self.error.emit(str(e))
            self.finished.emit(0, 1)

    def stop(self):
        self._stop = True

    def _classify_video(self, path: str) -> float:
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            return 0.0
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        if total <= 0:
            cap.release()
            return 0.0
        step = max(1, total // (self.sample_frames + 1))
        idxs = [min(total-1, i*step) for i in range(1, self.sample_frames+1)]
        max_score = 0.0
        for idx in idxs:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                continue
            tmp = Path.cwd() / f".tmp_frame_{os.getpid()}_{idx}.jpg"
            try:
                cv2.imencode('.jpg', frame)[1].tofile(str(tmp))
                if self.detector:
                    s = self.detector.classify_image(str(tmp))
                    if s > max_score:
                        max_score = s
                    if max_score >= self.nsfw_threshold:
                        break
            finally:
                try:
                    tmp.unlink(missing_ok=True)
                except Exception:
                    pass
        cap.release()
        return max_score