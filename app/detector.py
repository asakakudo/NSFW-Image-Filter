# app/detector.py
from typing import Optional
import os

CLASSIFIER_AVAILABLE = False
try:
    from nudenet import NudeClassifier
    CLASSIFIER_AVAILABLE = True
except Exception:
    NudeClassifier = None


class NSFWDetector:
    """Wrapper for NSFW classification. Returns score in 0..1 (higher = more likely NSFW).

    If nudenet is not available, instantiation will raise RuntimeError.
    """

    def __init__(self):
        if not CLASSIFIER_AVAILABLE:
            raise RuntimeError("nudenet/NudeClassifier not available")
        self.clf = NudeClassifier()

    def classify_image(self, path: str) -> float:
        """Classify image file path. Returns float score 0..1.

        Uses the classifier output heuristics to derive a single NSFW score.
        """
        # nudenet.classify returns {path: {label: score}}
        res = self.clf.classify(path)
        entry = res.get(path) or next(iter(res.values()))
        # common labels include 'unsafe', 'porn', 'raw', 'safe'
        # prefer explicit unsafe/porn keys, else invert safe
        for key in ("unsafe", "porn", "nsfw", "raw"):
            if key in entry:
                try:
                    return float(entry[key])
                except Exception:
                    pass
        if "safe" in entry:
            try:
                return 1.0 - float(entry["safe"])
            except Exception:
                pass
        # fallback: max of all non-safe probabilities
        try:
            vals = [float(v) for k, v in entry.items() if k != "safe"]
            return max(vals) if vals else 0.0
        except Exception:
            return 0.0