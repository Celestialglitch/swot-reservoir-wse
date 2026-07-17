import os
import pandas as pd
from concurrent.futures import ProcessPoolExecutor
from tqdm import tqdm

from swot_wse.cache.polygon_cache import (
    polygon_exists,
    load_polygon,
    save_polygon,
)
from swot_wse.geometry.reservoir_extractor import extract_reservoir_polygon
from swot_wse.lakesp.search import search_lakesp_granules
from swot_wse.lakesp.discovery import discover_granules
from swot_wse.lakesp.extract import process_granule
from swot_wse.filtering.stages import filter_timeseries
from swot_wse.outputs import save_outputs


MAX_WORKERS = max(1, os.cpu_count() - 1)


# -------------------------------------------------
# Main pipeline
# -------------------------------------------------
def get_wse(lat: float, lon: float, start_date: str, end_date: str):
    """
    Extract Water Surface Elevation (WSE) time series for a reservoir
    at the given coordinates and date range.
    """

    # -------------------------------------------------
    # Stage 1: Reservoir polygon extraction
    # -------------------------------------------------
    if polygon_exists(lat, lon):
        polygon = load_polygon(lat, lon)
        print("Loaded cached reservoir polygon.")
    else:
        try:
            polygon = extract_reservoir_polygon(lat, lon)
        except Exception:
            print(f"\nNo reservoir polygon could be extracted at lat={lat}, lon={lon}.")
            return None

        if polygon is None or polygon.empty:
            print(f"\nNo reservoir polygon footprint found at lat={lat}, lon={lon}.")
            return None

        save_polygon(lat, lon, polygon)


    # -------------------------------------------------
    # Stage 2: NASA CMR Search for candidate LakeSP granules within reservoir polygon
    # -------------------------------------------------
    candidate_granules = search_lakesp_granules(polygon, start_date, end_date)
    if not candidate_granules:
        print("No LakeSP granules found.")
        return None

    # -------------------------------------------------
    # Stage 3: Discover LakeSP granules that intersect with the reservoir polygon
    # -------------------------------------------------
    verified = discover_granules(candidate_granules, polygon)
    if not verified:
        print("\nNo LakeSP intersections found.")
        return None

    print(f"\nLakeSP intersections found : {len(verified)}")

    # -------------------------------------------------
    # Stage 4: WSE Extraction
    # -------------------------------------------------
    jobs = [(item["zip"], item["lake_ids"]) for item in verified]
    observations = []

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for result in tqdm(
            executor.map(process_granule, jobs),
            total=len(jobs),
            desc="Extracting WSE",
        ):
            if result is not None:
                observations.append(result)

    if not observations:
        print("\nNot enough observations (filtered by quality)")
        return None


    raw_df = pd.concat(observations, ignore_index=True)
    before = len(raw_df)

    raw_df = raw_df.sort_values("time_str").reset_index(drop=True)

    # -------------------------------------------------
    # Stage 4: Filtering
    # -------------------------------------------------
    clean_df = filter_timeseries(raw_df)
    if clean_df is None or clean_df.empty:
        print("\nNo observations remained after filtering.")
        return None

   
    save_outputs(clean_df, lat, lon)

    print("\n========== SUMMARY ==========")
    print(f"Verified Granules     : {len(verified)}")
    print(f"Raw Observations      : {before}")
    print(f"Final Observations    : {len(clean_df)}")
    print("=============================\n")

    print(clean_df)
    return clean_df
