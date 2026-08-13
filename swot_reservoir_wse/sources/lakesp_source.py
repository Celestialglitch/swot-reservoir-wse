from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from tqdm import tqdm

from swot_reservoir_wse.config import load_config
from swot_reservoir_wse.filtering.lakesp.stages import filter_timeseries
from swot_reservoir_wse.lakesp.discovery import discover_granules
from swot_reservoir_wse.lakesp.extract import process_granule
from swot_reservoir_wse.lakesp.search import search_lakesp_granules


def _remove_temporary_granules(
    verified_granules,
):
    """
    Remove LakeSP granules created during
    a non-cached run.
    """

    for granule in verified_granules:
        if not granule.get(
            "temporary",
            False,
        ):
            continue

        granule["zip"].unlink(
            missing_ok=True
        )


def run_lakesp_pipeline(
    polygon,
    start_date: str,
    end_date: str,
):
    """
    Execute the complete LakeSP processing workflow.
    """

    config = load_config()
    max_workers = config["max_workers"]

    candidate_granules = (
        search_lakesp_granules(
            polygon,
            start_date,
            end_date,
        )
    )

    if not candidate_granules:
        print(
            "\nNo LakeSP granules found."
        )
        return None

    verified_granules = discover_granules(
        candidate_granules,
        polygon,
        max_workers=max_workers,
    )

    if not verified_granules:
        print(
            "\nNo LakeSP intersections found."
        )
        return None

    jobs = [
        (
            granule["zip"],
            granule["lake_ids"],
        )
        for granule in verified_granules
    ]

    extracted = []

    try:
        with ThreadPoolExecutor(
            max_workers=max_workers,
        ) as executor:
            for observations in tqdm(
                executor.map(
                    process_granule,
                    jobs,
                ),
                total=len(jobs),
                desc="Extracting WSE",
            ):
                if observations is not None:
                    extracted.append(
                        observations
                    )

    finally:
        _remove_temporary_granules(
            verified_granules
        )

    if not extracted:
        print(
            "\nNo usable LakeSP observations found."
        )
        return None

    raw_df = (
        pd.concat(
            extracted,
            ignore_index=True,
        )
        .drop_duplicates(
            subset=[
                "lake_id",
                "time_str",
                "wse",
            ]
        )
        .sort_values("time_str")
        .reset_index(drop=True)
    )

    raw_observation_count = len(
        raw_df
    )

    clean_df = filter_timeseries(
        raw_df
    )

    if clean_df is None or clean_df.empty:
        print(
            "\nNo observations remained "
            "after filtering."
        )
        return None

    return {
        "source": "LakeSP",
        "timeseries": clean_df,
        "summary": {
            "verified_granules": len(
                verified_granules
            ),
            "raw_observations": (
                raw_observation_count
            ),
            "final_observations": len(
                clean_df
            ),
        },
        "metadata": {
            "verified_granules": (
                verified_granules
            ),
        },
    }