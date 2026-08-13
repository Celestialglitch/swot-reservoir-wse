import numpy as np
import pandas as pd

from swot_reservoir_wse.config import load_config


def build_daily_statistics(
    dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Aggregate accepted PIXC reservoir pixels
    into one WSE observation per acquisition date by using median.
    """

    if dataframe is None or dataframe.empty:
        return pd.DataFrame()

    required_columns = {
        "time_str",
        "wse",
        "water_frac",
        "phase_noise_std",
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "PIXC daily aggregation requires "
            "the following column(s): "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    dataframe = dataframe.copy()

    dataframe["time_str"] = pd.to_datetime(
        dataframe["time_str"],
        errors="coerce",
    )

    dataframe["wse"] = pd.to_numeric(
        dataframe["wse"],
        errors="coerce",
    )

    dataframe["water_frac"] = pd.to_numeric(
        dataframe["water_frac"],
        errors="coerce",
    )

    dataframe["phase_noise_std"] = pd.to_numeric(
        dataframe["phase_noise_std"],
        errors="coerce",
    )

    dataframe = dataframe.dropna(
        subset=[
            "time_str",
            "wse",
        ]
    )

    if dataframe.empty:
        return pd.DataFrame()

    daily = (
        dataframe
        .groupby(
            dataframe["time_str"].dt.normalize()
        )
        .agg(
            wse_median=(
                "wse",
                "median",
            ),
            wse_mean=(
                "wse",
                "mean",
            ),
            wse_std=(
                "wse",
                "std",
            ),
            wse_min=(
                "wse",
                "min",
            ),
            wse_max=(
                "wse",
                "max",
            ),
            pixel_count=(
                "wse",
                "count",
            ),
            mean_water_frac=(
                "water_frac",
                "mean",
            ),
            mean_phase_noise=(
                "phase_noise_std",
                "mean",
            ),
        )
        .reset_index()
        .rename(
            columns={
                "time_str": "date",
            }
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    return daily


def timeline_mad_filter(
    daily_dataframe: pd.DataFrame,
    threshold: float,
) -> pd.DataFrame:
    """
    Remove temporal WSE outliers using
    the Median Absolute Deviation.
    """

    if (
        daily_dataframe is None
        or daily_dataframe.empty
    ):
        return pd.DataFrame()

    if "wse_median" not in daily_dataframe.columns:
        raise ValueError(
            "PIXC MAD filtering requires "
            "the 'wse_median' column."
        )

    dataframe = daily_dataframe.copy()

    series = pd.to_numeric(
        dataframe["wse_median"],
        errors="coerce",
    )

    median = series.median()

    mad = np.median(
        np.abs(
            series - median
        )
    )

    if not np.isfinite(mad):
        return pd.DataFrame()

    # If all daily values are effectively identical,
    # there is no meaningful temporal deviation to filter.
    if mad < 1e-6:
        return dataframe.reset_index(
            drop=True
        )

    dataframe["modified_z"] = (
        0.6745
        * np.abs(
            series - median
        )
        / mad
    )

    return (
        dataframe[
            dataframe["modified_z"]
            <= threshold
        ]
        .copy()
        .reset_index(drop=True)
    )


def filter_timeseries(
    raw_dataframe: pd.DataFrame,
) -> pd.DataFrame:
    """
    Run the PIXC daily aggregation and
    temporal MAD filtering workflow.
    """

    if (
        raw_dataframe is None
        or raw_dataframe.empty
    ):
        return pd.DataFrame()

    mad_threshold = float(
        load_config()[
            "sources"
        ][
            "pixc"
        ][
            "mad_threshold"
        ]
    )

    print(
        "\nFiltering PIXC observations..."
    )
    print(
        f"Raw PIXC pixels       : "
        f"{len(raw_dataframe)}"
    )

    daily = build_daily_statistics(
        raw_dataframe
    )

    print(
        f"Daily observations    : "
        f"{len(daily)}"
    )

    if daily.empty:
        return pd.DataFrame()

    filtered = timeline_mad_filter(
        daily,
        threshold=mad_threshold,
    )

    print(
        f"Final observations    : "
        f"{len(filtered)}"
    )

    if filtered.empty:
        return pd.DataFrame()

    return (
        filtered[
            [
                "date",
                "wse_median",
                "wse_mean",
                "wse_std",
                "wse_min",
                "wse_max",
                "pixel_count",
                "mean_water_frac",
                "mean_phase_noise",
            ]
        ]
        .sort_values("date")
        .reset_index(drop=True)
    )