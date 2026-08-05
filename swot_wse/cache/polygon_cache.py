
import geopandas as gpd

from swot_wse.config import POLYGON_CACHE_DIR


def ensure_cache_exists():
    """
    Ensure that the polygon cache directory exists.
    """

    POLYGON_CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def get_polygon_path(lat, lon):
    """
    Construct the cache file path for a reservoir polygon.
    """

    return (
        POLYGON_CACHE_DIR
        / f"{lat:.5f}_{lon:.5f}.geojson"
    )


def polygon_exists(lat, lon):
    """
    Check whether a cached polygon exists.
    """

    return get_polygon_path(lat, lon).is_file()


def load_polygon(lat, lon):
    """
    Load a cached reservoir polygon.
    """

    path = get_polygon_path(lat, lon)

    if not path.exists():
        raise FileNotFoundError(path)

    polygon = gpd.read_file(path)

    if polygon.empty:
        raise RuntimeError(
            f"Cached reservoir polygon is empty: {path}"
        )

    return polygon


def save_polygon(lat, lon, polygon):
    """
    Save a reservoir polygon to cache.
    """

    if polygon is None or polygon.empty:
        raise ValueError(
            "Cannot cache an empty reservoir polygon."
        )

    ensure_cache_exists()

    polygon.to_file(
        get_polygon_path(lat, lon),
        driver="GeoJSON",
    )
