from swot_wse.config import (
    CACHE_DIR,
    POLYGON_CACHE_DIR,
    LAKESP_CACHE_DIR,
)


def register_cache_command(subparsers):

    parser = subparsers.add_parser(
        "cache",
        help="Inspect or clear cached files.",
    )

    parser.add_argument(
        "--clear-polygons",
        action="store_true",
        help="Remove cached reservoir polygons.",
    )

    parser.add_argument(
        "--clear-lakesp",
        action="store_true",
        default=False,
        help="Remove cached LakeSP granules.",
    )

    parser.add_argument(
        "--clear-all",
        action="store_true",
        default=False,
        help="Remove all cached data.",
    )

    parser.set_defaults(func=run_cache)


def run_cache(args):

    if args.clear_all:

        _clear_directory(POLYGON_CACHE_DIR)
        _clear_directory(LAKESP_CACHE_DIR)

        print("All cache cleared.")
        return

    if args.clear_polygons:

        _clear_directory(POLYGON_CACHE_DIR)

        print("Reservoir polygon cache cleared.")
        return

    if args.clear_lakesp:

        _clear_directory(LAKESP_CACHE_DIR)

        print("LakeSP granule cache cleared.")
        return

    polygon_count = len(
        list(POLYGON_CACHE_DIR.glob("*.geojson"))
    )

    lakesp_count = len(
        list(LAKESP_CACHE_DIR.glob("*.zip"))
    )

    print("\nCache Summary")
    print("-------------")
    print(f"Reservoir polygon cache : {polygon_count}")
    print(f"LakeSP granule cache  : {lakesp_count}")
    print(f"\nLocation : {CACHE_DIR.resolve()}\n")


def _clear_directory(directory):

    if not directory.exists():
        return

    for file in directory.iterdir():

        if file.is_file():
            file.unlink()