
import math
from datetime import datetime

from swot_wse.pipeline import get_wse


def register_polygon_command(subparsers):
    """
    Register the reservoir WSE extraction command.
    """

    parser = subparsers.add_parser(
        "polygon",
        help="Extract reservoir WSE time series.",
        description=(
            "Extract reservoir Water Surface Elevation "
            "(WSE) time series from SWOT observations."
        ),
    )

    parser.add_argument(
        "--lat",
        metavar="",
        type=float,
        required=True,
        help="Reservoir latitude.",
    )

    parser.add_argument(
        "--lon",
        metavar="",
        type=float,
        required=True,
        help="Reservoir longitude.",
    )

    parser.add_argument(
        "--start-date",
        metavar="",
        required=True,
        help="Start date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--end-date",
        metavar="",
        required=True,
        help="End date in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--source",
        metavar="",
        default="auto",
        help=(
            "SWOT observation source. "
            "By default, the package selects the source automatically."
        ),
    )

    parser.set_defaults(
        func=run_polygon_command
    )


def run_polygon_command(args):
    """
    Execute the polygon command.
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

        if start > end:
            raise ValueError(
                "Start date must not be after end date."
            )

    except ValueError as exc:

        print(
            f"\nError: {exc}"
        )

        return

    get_wse(
        lat=args.lat,
        lon=args.lon,
        start_date=args.start_date,
        end_date=args.end_date,
        source=args.source,
    )
