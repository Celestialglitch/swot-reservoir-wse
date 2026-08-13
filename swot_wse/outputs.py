from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

from swot_wse.config import load_config


QUALITY_COLORS = {
    "GOOD": "green",
    "SUSPECT": "orange",
    "DEGRADED": "red",
    "BAD": "black",
}


def _resolve_output_directory(path):
    """
    Resolve the configured output directory.

    Relative paths are resolved from the directory
    in which the swot-wse command is executed.
    """

    path = Path(path).expanduser()

    if not path.is_absolute():
        path = Path.cwd() / path

    return path.resolve()


def _validate_timeseries(dataframe, source):
    """
    Validate the columns required for output generation.
    """

    required_columns = {
        "date",
        "wse_median",
    }

    if source == "lakesp":
        required_columns.add(
            "quality_status"
        )

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        missing = ", ".join(
            sorted(missing_columns)
        )

        raise ValueError(
            "Cannot generate WSE outputs. "
            "Missing required column(s): "
            f"{missing}"
        )


def _source_information(source):
    """
    Return the normalized source name and display label.
    """

    source_name = str(source).strip().lower()

    if source_name == "lakesp":
        return "lakesp", "SWOT LakeSP"

    if source_name == "pixc":
        return "pixc", "SWOT PIXC"

    raise ValueError(
        f"Unsupported output source: {source}"
    )


def _prepare_timeseries(dataframe):
    """
    Prepare a time series for writing and plotting.
    """

    dataframe = dataframe.copy()

    dataframe["date"] = pd.to_datetime(
        dataframe["date"],
        errors="coerce",
    )

    dataframe["wse_median"] = pd.to_numeric(
        dataframe["wse_median"],
        errors="coerce",
    )

    dataframe = (
        dataframe
        .dropna(
            subset=[
                "date",
                "wse_median",
            ]
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    if dataframe.empty:
        raise ValueError(
            "No valid observations remained "
            "for output generation."
        )

    return dataframe


def _plot_lakesp(fig, ax, dataframe):
    """
    Plot LakeSP WSE observations with quality-aware markers.
    """

    dataframe = dataframe.copy()

    dataframe["quality_status"] = (
        dataframe["quality_status"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    unknown_quality = (
        set(dataframe["quality_status"].unique())
        - set(QUALITY_COLORS)
    )

    if unknown_quality:
        raise ValueError(
            "Unknown LakeSP quality status encountered: "
            + ", ".join(
                sorted(unknown_quality)
            )
        )

    ax.plot(
        dataframe["date"],
        dataframe["wse_median"],
        color="grey",
        linewidth=1.6,
        zorder=1,
    )

    point_colors = dataframe[
        "quality_status"
    ].map(
        QUALITY_COLORS
    )

    ax.scatter(
        dataframe["date"],
        dataframe["wse_median"],
        c=point_colors,
        marker="o",
        s=85,
        edgecolors="black",
        linewidths=0.8,
        zorder=3,
    )

    legend_items = [
        Line2D(
            [0],
            [0],
            marker="o",
            linestyle="None",
            markerfacecolor=color,
            markeredgecolor="black",
            markersize=9,
            label=quality,
        )
        for quality, color
        in QUALITY_COLORS.items()
    ]

    ax.legend(
        handles=legend_items,
        title="LakeSP Quality Status",
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        borderaxespad=0,
        frameon=True,
    )

    fig.subplots_adjust(
        right=0.78
    )


def _plot_pixc(ax, dataframe):
    """
    Plot the PIXC reservoir WSE time series.
    """

    ax.plot(
        dataframe["date"],
        dataframe["wse_median"],
        marker="o",
        markersize=5,
        linewidth=1.8,
    )


def save_outputs(
    df: pd.DataFrame,
    lat: float,
    lon: float,
    source: str,
):
    """
    Save the reservoir WSE time series and optional plot.

    Returns
    -------
    tuple
        Paths to the CSV file and PNG file. The PNG path is
        None when plot generation is disabled.
    """

    if df is None or df.empty:
        raise ValueError(
            "No observations available to save."
        )

    source_name, source_label = (
        _source_information(source)
    )

    _validate_timeseries(
        df,
        source_name,
    )

    dataframe = _prepare_timeseries(
        df
    )

    if source_name == "lakesp":
        dataframe["quality_status"] = (
            dataframe["quality_status"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        invalid_quality = (
            set(
                dataframe[
                    "quality_status"
                ].unique()
            )
            - set(QUALITY_COLORS)
        )

        if invalid_quality:
            raise ValueError(
                "Unknown LakeSP quality status encountered: "
                + ", ".join(
                    sorted(invalid_quality)
                )
            )

    config = load_config()

    output_directory = (
        _resolve_output_directory(
            config["output_dir"]
        )
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename_prefix = (
        f"{lat:.5f}_"
        f"{lon:.5f}_"
        f"{source_name}_wse"
    )

    csv_path = (
        output_directory
        / f"{filename_prefix}.csv"
    )

    dataframe.to_csv(
        csv_path,
        index=False,
    )

    plot_path = None

    if config["generate_plot"]:
        plot_path = (
            output_directory
            / f"{filename_prefix}.png"
        )

        fig, ax = plt.subplots(
            figsize=(12, 6)
        )

        if source_name == "lakesp":
            _plot_lakesp(
                fig,
                ax,
                dataframe,
            )
        else:
            _plot_pixc(
                ax,
                dataframe,
            )

        ax.set_title(
            f"{source_label} "
            "Water Surface Elevation"
        )

        ax.set_xlabel("Date")

        ax.set_ylabel(
            "Water Surface Elevation (m)"
        )

        ax.grid(
            True,
            alpha=0.3,
            zorder=0,
        )

        fig.autofmt_xdate()

        if source_name == "pixc":
            fig.tight_layout()

        save_options = {
            "dpi": 300,
        }

        if source_name == "lakesp":
            save_options[
                "bbox_inches"
            ] = "tight"

        fig.savefig(
            plot_path,
            **save_options,
        )

        plt.close(fig)

    print(
        "\n==================================="
    )
    print(
        "Outputs successfully written"
    )
    print(
    "-----------------------------------"
    )

    print(
    f"CSV  : "
    f"{csv_path}"
    )

    if plot_path is not None:

        print(
        f"Plot : "
        f"{plot_path}"
        )

    print(
        "===================================\n"
    )

    return (
        csv_path,
        plot_path,
    )