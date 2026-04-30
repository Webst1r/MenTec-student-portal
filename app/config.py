import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "portal.db"

DATA_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)

SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me-in-production-please")
SESSION_COOKIE = "mentec_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

MAX_UPLOAD_BYTES = 25 * 1024 * 1024  # 25 MB

DATABASE_URL = f"sqlite:///{DB_PATH}"
