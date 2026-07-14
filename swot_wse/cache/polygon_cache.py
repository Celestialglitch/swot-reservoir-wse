from pathlib import Path
import geopandas as gpd

CACHE_DIR = Path.home() / ".swot_wse" / "cache"
POLYGON_CACHE_DIR = CACHE_DIR / "polygons"


def initialize_cache():
    POLYGON_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_polygon_path(lat: float, lon: float):
    filename = f"{lat:.5f}_{lon:.5f}.geojson"
    return POLYGON_CACHE_DIR / filename


def polygon_exists(lat: float, lon: float):
    return get_polygon_path(lat, lon).exists()


def load_polygon(lat: float, lon: float):
    return gpd.read_file(get_polygon_path(lat, lon))


def save_polygon(lat: float, lon: float, polygon):
    polygon.to_file(get_polygon_path(lat, lon), driver="GeoJSON")