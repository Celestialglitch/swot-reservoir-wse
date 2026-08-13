import math
from datetime import datetime

from swot_reservoir_wse.pipeline import get_wse


SUPPORTED_SOURCES = (
    "lakesp",
    "pixc",
)


def register_extract_command(subparsers):
    """
    Register the reservoir WSE extraction command.
    """

    parser = subparsers.add_parser(
        "extract",
        help="Generate a reservoir WSE time series.",
        description=(
            "Generate a reservoir-specific Water Surface "
            "Elevation (WSE) time series from the selected "
            "SWOT observation product."
        ),
    )

    parser.add_argument(
        "--lat",
        type=float,
        required=True,
        help="Latitude of the dam location.",
    )

    parser.add_argument(
        "--lon",
        type=float,
        required=True,
        help="Longitude of the dam location.",
    )

    parser.add_argument(
        "--start-date",
        required=True,
        help="Start date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--end-date",
        required=True,
        help="End date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--source",
        choices=SUPPORTED_SOURCES,
        required=True,
        help=(
            "SWOT observation source to process. "
            "Supported values: lakesp, pixc."
        ),
    )

    parser.set_defaults(
        func=run_extract_command
    )


def run_extract_command(args):
    """
    Validate command arguments and execute
    reservoir WSE generation.
    """

    if not math.isfinite(args.lat):
        print(
            "\nError: Latitude must be a finite number."
        )
        return

    if not -90 <= args.lat <= 90:
        print(
            "\nError: Latitude must be between -90 and 90."
        )
        return

    if not math.isfinite(args.lon):
        print(
            "\nError: Longitude must be a finite number."
        )
        return

    if not -180 <= args.lon <= 180:
        print(
            "\nError: Longitude must be between -180 and 180."
        )
        return

    try:
        start = datetime.strptime(
            args.start_date,
            "%Y-%m-%d",
        )

        end = datetime.strptime(
            args.end_date,
            "%Y-%m-%d",
        )

    except ValueError:
        print(
            "\nError: Dates must use YYYY-MM-DD format."
        )
        return

    if start > end:
        print(
            "\nError: Start date must not be after end date."
        )
        return

    get_wse(
        lat=args.lat,
        lon=args.lon,
        start_date=args.start_date,
        end_date=args.end_date,
        source=args.source,
    )