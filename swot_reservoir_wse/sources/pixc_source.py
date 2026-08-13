from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)

import pandas as pd
from tqdm import tqdm

from swot_reservoir_wse.config import load_config
from swot_reservoir_wse.filtering.pixc.stages import filter_timeseries
from swot_reservoir_wse.pixc.discovery import discover_pixc_granules
from swot_reservoir_wse.pixc.extract import process_pixc_granule
from swot_reservoir_wse.pixc.search import search_pixc_granules


def run_pixc_pipeline(
    polygon,
    start_date,
    end_date,
):
    """
    Execute the complete PIXC processing workflow
    for one reservoir.
    """

    config = load_config()
    max_workers = int(
        config["max_workers"]
    )

    candidate_granules = (
        search_pixc_granules(
            reservoir_polygon=polygon,
            start_date=start_date,
            end_date=end_date,
        )
    )

    if not candidate_granules:
        print(
            "\nNo PIXC granules found."
        )
        return None

    verified_granules = (
        discover_pixc_granules(
            candidate_granules,
            polygon,
        )
    )

    if not verified_granules:
        print(
            "\nNo PIXC intersections found."
        )
        return None

    print(
        "\nProcessing verified PIXC granules..."
    )

    extracted_frames = []

    with ThreadPoolExecutor(
        max_workers=max_workers,
    ) as executor:
        futures = [
            executor.submit(
                process_pixc_granule,
                record["granule"],
                polygon,
            )
            for record in verified_granules
        ]

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Processing PIXC granules",
            leave=False,
        ):
            dataframe = future.result()

            if (
                dataframe is None
                or dataframe.empty
            ):
                continue

            extracted_frames.append(
                dataframe
            )

    if not extracted_frames:
        print(
            "\nNo usable PIXC pixels found."
        )
        return None

    raw_observations = pd.concat(
        extracted_frames,
        ignore_index=True,
    )

    if raw_observations.empty:
        print(
            "\nNo usable PIXC observations found."
        )
        return None

    print(
        f"\nAccepted PIXC pixels   : "
        f"{len(raw_observations)}"
    )

    timeseries = filter_timeseries(
        raw_observations
    )

    if (
        timeseries is None
        or timeseries.empty
    ):
        print(
            "\nNo PIXC observations "
            "remained after filtering."
        )
        return None

    return {
        "source": "PIXC",
        "timeseries": timeseries,
        "summary": {
            "verified_granules": len(
                verified_granules
            ),
            "raw_observations": len(
                raw_observations
            ),
            "final_observations": len(
                timeseries
            ),
        },
    }