from pathlib import Path

APP_DIR = Path.home() / ".swot_wse"

DATA_DIR = APP_DIR / "data"
CACHE_DIR = APP_DIR / "cache"
DOWNLOAD_DIR = APP_DIR / "downloads"


def initialize_directories():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)