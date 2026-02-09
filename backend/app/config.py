from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_PETS = BASE_DIR / "uploads" / "pets"
UPLOAD_LOST = BASE_DIR / "uploads" / "lost"
UPLOAD_STRAY = BASE_DIR / "uploads" / "stray"
UPLOAD_PETS.mkdir(parents=True, exist_ok=True)
UPLOAD_LOST.mkdir(parents=True, exist_ok=True)
UPLOAD_STRAY.mkdir(parents=True, exist_ok=True)
