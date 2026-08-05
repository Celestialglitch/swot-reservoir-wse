
import matplotlib.pyplot as plt
import pandas as pd

from swot_wse.config import (
    OUTPUT_DIR,
    load_config,
)


def save_outputs(
    df: pd.DataFrame,
    lat: float,
    lon: float,
):
    """
    Save the final filtered Water Surface Elevation time series.
    """

    if df is None or df.empty:
        raise ValueError(
            "No observations available to save."
        )

    config = load_config()

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    df = (
        df.copy()
        .sort_values("date")
        .reset_index(drop=True)
    )

    csv_path = (
        OUTPUT_DIR
        / f"{lat:.5f}_{lon:.5f}_wse.csv"
    )

    df.to_csv(
        csv_path,
        index=False,
    )

    plot_path = None

    if config["generate_plot"]:

        plot_path = (
            OUTPUT_DIR
            / f"{lat:.5f}_{lon:.5f}_wse.png"
        )

        fig, ax = plt.subplots(
            figsize=(10, 5)
        )

        ax.plot(
            df["date"],
            df["wse_median"],
            marker="o",
            markersize=4,
            linewidth=2,
        )

        ax.set_title(
            "SWOT LakeSP Water Surface Elevation"
        )

        ax.set_xlabel("Date")
        ax.set_ylabel(
            "Water Surface Elevation (m)"
        )

        ax.grid(True)

        fig.autofmt_xdate()
        fig.tight_layout()

        fig.savefig(
            plot_path,
            dpi=300,
        )

        plt.close(fig)

    print("\n===================================")
    print("Outputs successfully written")
    print("-----------------------------------")
    print(f"CSV  : {csv_path}")

    if plot_path is not None:
        print(f"Plot : {plot_path}")

    print("===================================\n")

    return (
        csv_path,
        plot_path,
    )
