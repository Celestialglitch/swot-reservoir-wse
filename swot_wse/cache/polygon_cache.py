from pathlib import Path

CACHE_DIR = Path.home() / ".swot_wse" / "cache"
POLYGON_CACHE_DIR = CACHE_DIR / "polygons"


def initialize_cache():
    POLYGON_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_polygon_path(lat, lon):
    """
    Return the expected cache file path for a reservoir polygon.
    """

    filename = f"{lat:.5f}_{lon:.5f}.geojson"

    return POLYGON_CACHE_DIR / filename


def polygon_exists(lat, lon):
    """
    Check whether a cached polygon already exists.
    """

    return get_polygon_path(lat, lon).exists()