from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from swot_wse.config import OUTPUT_DIR





def save_outputs(df: pd.DataFrame, lat: float, lon: float) -> tuple[Path, Path]:
    
    if df is None or df.empty:
        raise ValueError("No data available to save.")

    df = df.copy()

    
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)

   
    csv_path = OUTPUT_DIR / f"{lat:.5f}_{lon:.5f}_wse.csv"
    plot_path = OUTPUT_DIR / f"{lat:.5f}_{lon:.5f}_wse.png"

  
    df.to_csv(csv_path, index=False)

    # -------------------------------------------------
    # Plot
    # -------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["date"], df["wse_median"], linewidth=2, marker="o", markersize=4)

    ax.set_title("SWOT LakeSP Water Surface Elevation")
    ax.set_xlabel("Date")
    ax.set_ylabel("Water Surface Elevation (m)")
    ax.grid(True)

    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(plot_path, dpi=300)
    plt.close(fig)

    print("\n===================================")
    print("Outputs successfully written")
    print("-----------------------------------")
    print(f"CSV : {csv_path}")
    print(f"Plot: {plot_path}")
    print("===================================\n")

    return csv_path, plot_path
