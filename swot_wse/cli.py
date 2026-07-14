import argparse

from swot_wse.cache.polygon_cache import initialize_cache
from swot_wse.earth_engine import initialize_earth_engine
from swot_wse.pipeline import get_wse


def main():
    """
    Entry point for the swot-wse command line interface.
    """

    # Initialize application
    initialize_cache()
    initialize_earth_engine()

    parser = argparse.ArgumentParser(
        prog="swot-wse",
        description="Extract Water Surface Elevation (WSE) from SWOT."
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

    args = parser.parse_args()

    if args.command == "polygon":
        get_wse(args.lat, args.lon)