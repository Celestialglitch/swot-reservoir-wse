import argparse
from swot_wse.geometry.reservoir_extractor import find_reservoir
from swot_wse.cache.polygon_cache import initialize_cache
from swot_wse.pipeline import get_wse


def main():
    initialize_cache()
    parser = argparse.ArgumentParser(
        prog="swot-wse",
        description="Extract reservoir WSE from SWOT."
    )

    subparsers = parser.add_subparsers(dest="command")

    get_parser = subparsers.add_parser(
        "get",
        help="Get reservoir WSE."
    )

    get_parser.add_argument("--lat", type=float)
    get_parser.add_argument("--lon", type=float)
    get_parser.add_argument("--reservoir-id", type=int)

    args = parser.parse_args()

    if args.command == "get":
        get_wse(args.lat, args.lon)
    
