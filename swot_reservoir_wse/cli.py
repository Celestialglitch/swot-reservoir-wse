import argparse
import warnings

from swot_reservoir_wse.commands.auth import register_auth_command
from swot_reservoir_wse.commands.cache import register_cache_command
from swot_reservoir_wse.commands.config import register_config_command
from swot_reservoir_wse.commands.extract import register_extract_command
from swot_reservoir_wse.config import initialize_directories


def main():
    """
    Entry point for the swot-reservoir-wse command-line interface.
    """

    warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
    module=r"earthaccess(\..*)?$",
    )

    
    initialize_directories()

    parser = argparse.ArgumentParser(
        prog="swot-reservoir-wse",
        description=(
            "Generate reservoir Water Surface Elevation "
            "time series from SWOT observations."
        ),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    register_extract_command(subparsers)
    register_config_command(subparsers)
    register_cache_command(subparsers)
    register_auth_command(subparsers)

    args = parser.parse_args()

    try:

        args.func(
        args
    )

    except RuntimeError as exc:

        parser.exit(
        status=1,
        message=f"\nError: {exc}\n",
    )

if __name__ == "__main__":
    main()