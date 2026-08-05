
from swot_wse.cache.polygon_cache import (
    polygon_exists,
    load_polygon,
    save_polygon,
)
from swot_wse.config import load_config
from swot_wse.earth_engine import initialize_earth_engine
from swot_wse.geometry.reservoir_extractor import extract_reservoir_polygon
from swot_wse.sources.manager import run_source
from swot_wse.outputs import save_outputs


def get_or_create_polygon(lat, lon):
    """
    Load the cached reservoir polygon or extract it.
    """

    config = load_config()

    polygon_cache_enabled = config[
        "polygon_cache_enabled"
    ]

    if (
        polygon_cache_enabled
        and polygon_exists(lat, lon)
    ):
        print("Loaded cached reservoir polygon.")

        return load_polygon(
            lat,
            lon,
        )

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
    source="auto",
):
    """
    Generate WSE time series for the given reservoir location and date range.
    """

    source = source.lower()

    if source == "auto":
        source = "lakesp"

    polygon = get_or_create_polygon(
        lat,
        lon,
    )

    if polygon is None:
        return None

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
        print("\nNo usable observations found.")

        return None

    save_outputs(
        result["timeseries"],
        lat,
        lon,
    )

    summary = result["summary"]

    print("\n========== SUMMARY ==========")
    print(f"Source              : {result['source']}")
    print(f"Verified Granules   : {summary['verified_granules']}")
    print(f"Raw Observations    : {summary['raw_observations']}")
    print(f"Final Observations  : {summary['final_observations']}")
    print("=============================\n")

    print(
        result["timeseries"].to_string(
            index=False,
        )
    )

    return result["timeseries"]
