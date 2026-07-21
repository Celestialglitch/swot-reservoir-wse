from pathlib import Path
import json


APP_DIR = Path.home() / "Documents" / "swot_wse"

CACHE_DIR = APP_DIR / "cache"
POLYGON_CACHE_DIR = CACHE_DIR / "polygons"
LAKESP_CACHE_DIR = CACHE_DIR / "lakesp"

DATA_DIR = APP_DIR / "data"
OUTPUT_DIR = DATA_DIR / "outputs"

DOWNLOAD_DIR = APP_DIR / "downloads"
CONFIG_FILE = APP_DIR / "config.json"


def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}


def save_config(config: dict) -> None:
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)




def initialize_directories() -> None:
    """
    Ensure that all required application directories exist.
    Creates them if they do not already exist.
    """
    for directory in (
        APP_DIR,
        CACHE_DIR,
        POLYGON_CACHE_DIR,
        LAKESP_CACHE_DIR,
        DATA_DIR,
        OUTPUT_DIR,
        DOWNLOAD_DIR,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    if not CONFIG_FILE.exists():
        save_config({})
