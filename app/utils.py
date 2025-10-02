import os
import zipfile
from pathlib import Path
import shutil
from typing import Iterable


def make_zip(output_path: Path, folders: Iterable[Path]):
    """Create a ZIP archive at output_path containing given folders (relative paths preserved).

    Overwrites existing archive.
    """
    output_path = Path(output_path)
    if output_path.exists():
        output_path.unlink()
    with zipfile.ZipFile(str(output_path), "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for fld in folders:
            fld = Path(fld)
            if not fld.exists():
                continue
            for root, _, files in os.walk(str(fld)):
                for f in files:
                    fp = Path(root) / f
                    arcname = fp.relative_to(fld.parent)
                    zf.write(str(fp), arcname= str(arcname) )


def safe_copy(src: Path, dest_dir: Path):
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(str(src), str(dest_dir / src.name))