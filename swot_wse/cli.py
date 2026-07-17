import argparse
from datetime import datetime
from swot_wse.cache.polygon_cache import initialize_cache
from swot_wse.earth_engine import initialize_earth_engine
from swot_wse.pipeline import get_wse
from swot_wse.config import initialize_directories



def main():
  
    initialize_directories()
    initialize_earth_engine()

    parser = argparse.ArgumentParser(
        prog="swot-wse",
        description="Extract reservoir Water Surface Elevation (WSE) for a given dam location."
    )

    subparsers = parser.add_subparsers(dest="command")

    # -------------------------
    # get command
    # -------------------------

    polygon_parser = subparsers.add_parser(
    "polygon",
    help="Generate or load a reservoir polygon."
    )

    polygon_parser.add_argument(
        "--lat",
        type=float,
        required=True,
        help="Latitude of the reservoir."
    )

    polygon_parser.add_argument(
        "--lon",
        type=float,
        required=True,
        help="Longitude of the reservoir."
    )
    polygon_parser.add_argument(
    "--start-date",
    required=True,
    help="Start date (YYYY-MM-DD)"
    )

    polygon_parser.add_argument(
    "--end-date",
    required=True,
    help="End date (YYYY-MM-DD)"
    )

    args = parser.parse_args()
   
    if args.command == "polygon":
         try:
            datetime.strptime(args.start_date, "%Y-%m-%d")
            datetime.strptime(args.end_date, "%Y-%m-%d")
         except ValueError:
            parser.error("Dates must be in YYYY-MM-DD format.")

         get_wse(
    args.lat,
    args.lon,
    args.start_date,
    args.end_date,
)