from pathlib import Path
import geopandas as gpd
from swot_wse.config import POLYGON_CACHE_DIR






def initialize_cache() -> None:
    """
    Ensure that the polygon cache directory exists.
    Creates the directory if it does not already exist.
    """
    POLYGON_CACHE_DIR.mkdir(parents=True, exist_ok=True)



def get_polygon_path(lat: float, lon: float) -> Path:
    """
    Construct the cache file path for a reservoir polygon.

    Parameters
    ----------
    lat : float
        Latitude of reservoir.
    lon : float
        Longitude of reservoir.

    Returns
    -------
    Path
        Path to the GeoJSON file in the cache.
    """
    filename = f"{lat:.5f}_{lon:.5f}.geojson"
    return POLYGON_CACHE_DIR / filename


def polygon_exists(lat: float, lon: float) -> bool:
    """
    Check whether a cached polygon exists for the given coordinates.
    """
    return get_polygon_path(lat, lon).exists()



def load_polygon(lat: float, lon: float) -> gpd.GeoDataFrame:
    """
    Load a cached reservoir polygon from GeoJSON.

    Parameters
    ----------
    lat : float
    lon : float

    Returns
    -------
    GeoDataFrame
        Reservoir polygon geometry.
    """
    return gpd.read_file(get_polygon_path(lat, lon))


def save_polygon(lat: float, lon: float, polygon: gpd.GeoDataFrame) -> None:
    """
    Save a reservoir polygon to the cache as GeoJSON.

    Parameters
    ----------
    lat : float
    lon : float
    polygon : GeoDataFrame
        Reservoir polygon geometry to save.
    """
    polygon.to_file(get_polygon_path(lat, lon), driver="GeoJSON")
