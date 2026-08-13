from swot_reservoir_wse.config import (
    CACHE_DIR,
    LAKESP_CACHE_DIR,
    POLYGON_CACHE_DIR,
)


def register_cache_command(subparsers):
    """
    Register cache inspection and cleanup commands.
    """

    parser = subparsers.add_parser(
        "cache",
        help="Inspect or clear cached files.",
    )

    clear_group = (
        parser.add_mutually_exclusive_group()
    )

    clear_group.add_argument(
        "--clear-polygons",
        action="store_true",
        help="Remove cached reservoir polygons.",
    )

    clear_group.add_argument(
        "--clear-lakesp",
        action="store_true",
        help="Remove cached LakeSP granules.",
    )

    clear_group.add_argument(
        "--clear-all",
        action="store_true",
        help="Remove all cached data.",
    )

    parser.set_defaults(
        func=run_cache
    )


def run_cache(args):
    """
    Display cache information or clear
    the requested cache.
    """

    if args.clear_all:
        _clear_directory(
            POLYGON_CACHE_DIR
        )
        _clear_directory(
            LAKESP_CACHE_DIR
        )

        print("All caches cleared.")
        return

    if args.clear_polygons:
        _clear_directory(
            POLYGON_CACHE_DIR
        )

        print(
            "Reservoir polygon cache cleared."
        )
        return

    if args.clear_lakesp:
        _clear_directory(
            LAKESP_CACHE_DIR
        )

        print(
            "LakeSP granule cache cleared."
        )
        return

    polygon_count = len(
        list(
            POLYGON_CACHE_DIR.glob(
                "*.geojson"
            )
        )
    )

    lakesp_count = len(
        list(
            LAKESP_CACHE_DIR.glob(
                "*.zip"
            )
        )
    )

    print("\nCache Summary")
    print("-------------")
    print(
        f"Reservoir polygons : {polygon_count}"
    )
    print(
        f"LakeSP granules    : {lakesp_count}"
    )
    print(
        f"\nLocation : {CACHE_DIR.resolve()}\n"
    )


def _clear_directory(directory):
    """
    Remove files stored directly in a cache directory.
    """

    if not directory.exists():
        return

    for path in directory.iterdir():
        if path.is_file():
            path.unlink()