from swot_wse.cache.polygon_cache import (
    load_polygon,
    polygon_exists,
    save_polygon,
)
from swot_wse.config import load_config
from swot_wse.earth_engine import initialize_earth_engine
from swot_wse.earthdata import initialize_earthdata
from swot_wse.geometry.reservoir_extractor import extract_reservoir_polygon
from swot_wse.outputs import save_outputs
from swot_wse.sources.manager import run_source


def get_or_create_polygon(lat, lon):
    """
    Load a cached reservoir footprint when available,
    otherwise generate one from the supplied dam location.
    """

    config = load_config()
    polygon_cache_enabled = config["polygon_cache_enabled"]

    if (
        polygon_cache_enabled
        and polygon_exists(lat, lon)
    ):
        print("Loaded cached reservoir polygon.")
        return load_polygon(lat, lon)

    initialize_earth_engine()

    polygon = extract_reservoir_polygon(
        lat,
        lon,
    )

    if polygon is None or polygon.empty:
        print(
            f"\nNo reservoir polygon found at "
            f"lat={lat}, lon={lon}."
        )
        return None

    if polygon_cache_enabled:
        save_polygon(
            lat,
            lon,
            polygon,
        )

    return polygon



def get_wse(
    lat,
    lon,
    start_date,
    end_date,
    source,
):
    """
    Generate a reservoir-specific WSE time series
    using the selected SWOT observation product.
    """

    source = str(source).strip().lower()

    polygon = get_or_create_polygon(
        lat,
        lon,
    )

    if polygon is None:
        return None

    initialize_earthdata()

    print(
        f"\nRunning {source.upper()} pipeline..."
    )

    result = run_source(
        source=source,
        polygon=polygon,
        start_date=start_date,
        end_date=end_date,
    )

    if result is None:
        print(
            f"\nNo usable {source.upper()} observations "
            "found for the requested reservoir and date range."
        )
        return None

    timeseries = result["timeseries"]

    save_outputs(
        timeseries,
        lat,
        lon,
        source=result["source"],
    )

    print(
        timeseries.to_string(
            index=False,
        )
    )

    return timeseries