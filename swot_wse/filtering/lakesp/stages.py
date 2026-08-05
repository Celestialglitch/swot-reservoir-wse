import numpy as np
import pandas as pd

from swot_wse.config import load_config


CONFIG = load_config()

MAD_THRESHOLD = CONFIG["sources"]["lakesp"]["mad_threshold"]


def stage1_quality_filter(df: pd.DataFrame):
    """
    Remove partial lakes and poor-quality observations.
    """

    return df[
        (df["partial_f"] == 0)
        &
        (df["quality_f"].isin([0, 1]))
    ].copy()


def stage2_daily_aggregation(df: pd.DataFrame):
    """
    Aggregate observations by acquisition day.
    """

    df = df.copy()

    df["time_str"] = pd.to_datetime(
        df["time_str"],
        utc=True,
    )

    df["date"] = df["time_str"].dt.floor("D")

    daily = (
        df.groupby(
            "date",
            as_index=False,
        )
        .agg(
            wse_median=("wse", "median"),
            n_good=("quality_f", lambda x: (x == 0).sum()),
            n_suspect=("quality_f", lambda x: (x == 1).sum()),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    daily["quality_status"] = np.where(
        daily["n_good"] >= daily["n_suspect"],
        "GOOD",
        "SUSPECT",
    )

    return daily


def stage3_mad_filter(df: pd.DataFrame):
    """
    Remove elevation outliers using MAD.
    """

    df = df.copy()

    median = df["wse_median"].median()

    mad = np.median(
        np.abs(
            df["wse_median"] - median
        )
    )

    if mad == 0:
        mad = 1e-6

    df["modified_z"] = (
        0.6745
        * np.abs(df["wse_median"] - median)
        / mad
    )

    return df[
        df["modified_z"] <= MAD_THRESHOLD
    ].copy()


def filter_timeseries(df: pd.DataFrame):
    """
    Execute the complete LakeSP filtering pipeline.
    """

    print("\nFiltering observations...")
    print(f"Raw observations : {len(df)}")

    df = stage1_quality_filter(df)

    print(f"After quality filter : {len(df)}")

    if df.empty:
        return None

    df = stage2_daily_aggregation(df)

    print(f"Acquisition dates : {len(df)}")

    if df.empty:
        return None

    df = stage3_mad_filter(df)

    print(f"After MAD filter : {len(df)}")

    if df.empty:
        return None

    return (
        df[
            [
                "date",
                "wse_median",
                "quality_status",
            ]
        ]
        .sort_values("date")
        .reset_index(drop=True)
    )