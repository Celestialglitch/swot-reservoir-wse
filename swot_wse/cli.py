import argparse

from swot_wse.config import initialize_directories

from swot_wse.commands.auth import register_auth_command
from swot_wse.commands.cache import register_cache_command
from swot_wse.commands.config import register_config_command
from swot_wse.commands.polygon import register_polygon_command


def main():

    initialize_directories()

    parser = argparse.ArgumentParser(
        prog="swot-wse",
        description="Reservoir Water Surface Elevation toolkit built on SWOT observations.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    register_polygon_command(subparsers)
    register_config_command(subparsers)
    register_cache_command(subparsers)
    register_auth_command(subparsers)

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()