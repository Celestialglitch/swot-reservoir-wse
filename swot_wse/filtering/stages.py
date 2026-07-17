import numpy as np
import pandas as pd


MAD_THRESHOLD = 3.0


# -------------------------------------------------
# Stage 1
# Quality filtering
# -------------------------------------------------
def stage1_quality_filter(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only observations that are:
    - not partial water bodies
    - GOOD (0) or SUSPECT (1)
    """
    return df[
        (df["partial_f"] == 0) &
        (df["quality_f"].isin([0, 1]))
    ].copy()


# -------------------------------------------------
# Stage 2
# Daily median aggregation
# -------------------------------------------------
def stage2_daily_aggregation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Median aggregation of all observations acquired on the same day.
   
    """
    df = df.copy()
    df["time_str"] = pd.to_datetime(df["time_str"], utc=True)
    df["date_day"] = df["time_str"].dt.floor("D")

    stage2 = (
        df.groupby("date_day", as_index=False)
          .agg(
              wse_median=("wse", "median"),
              n_good=("quality_f", lambda x: (x == 0).sum()),
              n_suspect=("quality_f", lambda x: (x == 1).sum())
          )
          .sort_values("date_day")
          .reset_index(drop=True)
    )

    stage2["quality_status"] = np.where(
        stage2["n_good"] >= stage2["n_suspect"],
        "GOOD",
        "SUSPECT"
    )

    return stage2


# -------------------------------------------------
# Stage 3
# MAD outlier removal
# -------------------------------------------------
def stage3_mad_filter(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove abnormal daily elevations using Median Absolute Deviation (MAD).
    """
    df = df.copy()
    median = np.median(df["wse_median"])
    mad = np.median(np.abs(df["wse_median"] - median))

   
    if mad == 0:
        mad = 1e-6

    df["modified_z"] = (
        0.6745 * np.abs(df["wse_median"] - median) / mad
    )

    return df[df["modified_z"] <= MAD_THRESHOLD].copy()


# -------------------------------------------------
# Complete filtering pipeline
# -------------------------------------------------
def filter_timeseries(df: pd.DataFrame) -> pd.DataFrame | None:
    """
    Apply the full three-stage filtering pipeline:
    1. Quality filter
    2. Daily median aggregation
    3. MAD outlier removal

    Returns
    -------
    pd.DataFrame or None
        Filtered time series with columns:
        - date
        - wse_median
        - quality_status
    """
    print("\nFiltering observations...")
    print(f"Raw observations : {len(df)}")

    stage1 = stage1_quality_filter(df)
    print(f"After quality filter : {len(stage1)}")
    if stage1.empty:
        return None

    stage2 = stage2_daily_aggregation(stage1)
    print(f"Acquisition dates : {len(stage2)}")
    if stage2.empty:
        return None

    stage3 = stage3_mad_filter(stage2)
    print(f"After MAD filter : {len(stage3)}")
    if stage3.empty:
        return None

    return (
        stage3[["date_day", "wse_median", "quality_status"]]
        .rename(columns={"date_day": "date"})
        .sort_values("date")
        .reset_index(drop=True)
    )
