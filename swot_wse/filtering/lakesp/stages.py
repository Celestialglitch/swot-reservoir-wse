import numpy as np
import pandas as pd

from swot_wse.config import load_config


QUALITY_NAME_TO_VALUE = {
    "good": 0,
    "suspect": 1,
    "degraded": 2,
    "bad": 3,
}

QUALITY_VALUE_TO_NAME = {
    0: "GOOD",
    1: "SUSPECT",
    2: "DEGRADED",
    3: "BAD",
}


def _get_lakesp_config():
    """
    Return the active LakeSP configuration.
    """

    return load_config()["sources"]["lakesp"]


def _get_accepted_quality_values():
    """
    Convert configured LakeSP quality names
    to their numeric values.
    """

    configured_flags = (
        _get_lakesp_config()[
            "accepted_quality_flags"
        ]
    )

    accepted_values = set()

    for flag in configured_flags:
        normalized = (
            str(flag)
            .strip()
            .lower()
        )

        if normalized not in QUALITY_NAME_TO_VALUE:
            raise RuntimeError(
                "Invalid LakeSP quality class "
                f"in configuration: {flag}"
            )

        accepted_values.add(
            QUALITY_NAME_TO_VALUE[
                normalized
            ]
        )

    if not accepted_values:
        raise RuntimeError(
            "At least one LakeSP quality "
            "class must be enabled."
        )

    return accepted_values


def stage1_quality_filter(
    df: pd.DataFrame,
):
    """
    Remove partial observations and retain
    only the configured LakeSP quality classes.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    required_columns = {
        "partial_f",
        "quality_f",
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "LakeSP quality filtering requires "
            "the following column(s): "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    accepted_quality_values = (
        _get_accepted_quality_values()
    )

    return (
        df[
            (df["partial_f"] == 0)
            & df["quality_f"].isin(
                accepted_quality_values
            )
        ]
        .copy()
        .reset_index(drop=True)
    )


def _daily_quality_status(
    quality_values,
):
    """
    Determine the representative quality
    class for one acquisition date.

    The most frequent class is selected.
    If multiple classes are equally frequent,
    the poorer quality class is used.
    """

    counts = (
        quality_values
        .value_counts()
    )

    if counts.empty:
        return None

    maximum_count = counts.max()

    tied_values = (
        counts[
            counts == maximum_count
        ]
        .index
    )

    selected_value = max(
        int(value)
        for value in tied_values
    )

    if selected_value not in QUALITY_VALUE_TO_NAME:
        raise ValueError(
            "Unknown LakeSP quality flag "
            f"value: {selected_value}"
        )

    return QUALITY_VALUE_TO_NAME[
        selected_value
    ]


def stage2_daily_aggregation(
    df: pd.DataFrame,
):
    """
    Aggregate LakeSP observations by
    acquisition date.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    required_columns = {
        "time_str",
        "wse",
        "quality_f",
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "LakeSP daily aggregation requires "
            "the following column(s): "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    df = df.copy()

    df["time_str"] = pd.to_datetime(
        df["time_str"],
        utc=True,
        errors="coerce",
    )

    df["wse"] = pd.to_numeric(
        df["wse"],
        errors="coerce",
    )

    df["quality_f"] = pd.to_numeric(
        df["quality_f"],
        errors="coerce",
    )

    df = df.dropna(
        subset=[
            "time_str",
            "wse",
            "quality_f",
        ]
    )

    if df.empty:
        return pd.DataFrame()

    df["date"] = (
        df["time_str"]
        .dt.floor("D")
    )

    daily = (
        df.groupby(
            "date",
            as_index=False,
        )
        .agg(
            wse_median=(
                "wse",
                "median",
            ),
            n_good=(
                "quality_f",
                lambda values: (
                    values == 0
                ).sum(),
            ),
            n_suspect=(
                "quality_f",
                lambda values: (
                    values == 1
                ).sum(),
            ),
            n_degraded=(
                "quality_f",
                lambda values: (
                    values == 2
                ).sum(),
            ),
            n_bad=(
                "quality_f",
                lambda values: (
                    values == 3
                ).sum(),
            ),
            quality_status=(
                "quality_f",
                _daily_quality_status,
            ),
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    return daily


def stage3_mad_filter(
    df: pd.DataFrame,
):
    """
    Remove temporal WSE outliers using
    the Median Absolute Deviation.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    if "wse_median" not in df.columns:
        raise ValueError(
            "LakeSP MAD filtering requires "
            "the 'wse_median' column."
        )

    mad_threshold = float(
        _get_lakesp_config()[
            "mad_threshold"
        ]
    )

    df = df.copy()

    median = (
        df["wse_median"]
        .median()
    )

    mad = np.median(
        np.abs(
            df["wse_median"]
            - median
        )
    )

    if not np.isfinite(mad):
        return pd.DataFrame()

    if mad < 1e-6:
        return (
            df
            .reset_index(drop=True)
        )

    df["modified_z"] = (
        0.6745
        * np.abs(
            df["wse_median"]
            - median
        )
        / mad
    )

    return (
        df[
            df["modified_z"]
            <= mad_threshold
        ]
        .copy()
        .reset_index(drop=True)
    )


def filter_timeseries(
    df: pd.DataFrame,
):
    """
    Run the LakeSP quality filtering,
    daily aggregation, and MAD filtering
    workflow.
    """

    if df is None or df.empty:
        return None

    accepted_quality_values = (
        _get_accepted_quality_values()
    )

    accepted_quality_names = [
        QUALITY_VALUE_TO_NAME[value]
        for value in sorted(
            accepted_quality_values
        )
    ]

    print(
        "\nFiltering LakeSP observations..."
    )

    print(
        "Accepted quality classes : "
        + ", ".join(
            accepted_quality_names
        )
    )

    print(
        f"Raw observations         : "
        f"{len(df)}"
    )

    df = stage1_quality_filter(df)

    print(
        f"After quality filter     : "
        f"{len(df)}"
    )

    if df.empty:
        return None

    df = stage2_daily_aggregation(df)

    print(
        f"Acquisition dates        : "
        f"{len(df)}"
    )

    if df.empty:
        return None

    df = stage3_mad_filter(df)

    print(
        f"After MAD filter         : "
        f"{len(df)}"
    )

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