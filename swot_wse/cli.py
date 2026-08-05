
import argparse
from pathlib import Path

from swot_wse.config import initialize_directories

from swot_wse.commands.auth import register_auth_command
from swot_wse.commands.cache import register_cache_command
from swot_wse.commands.config import register_config_command
from swot_wse.commands.polygon import register_polygon_command


def main():

    current_directory = Path.cwd()

    project_file = (
        current_directory / "pyproject.toml"
    )

    package_directory = (
        current_directory / "swot_wse"
    )

    if (not project_file.is_file()
        or not package_directory.is_dir()
    ):

        raise RuntimeError(
            "SWOT-WSE must be run from the project directory.\n\n"
            "Change to the cloned repository directory first, for example:\n\n"
            "    cd D:\\test-install-2\\swot-reservoir-wse\n"
        )

    initialize_directories()

    parser = argparse.ArgumentParser(
        prog="swot-wse",
        description=(
            "Reservoir Water Surface Elevation toolkit "
            "built on SWOT observations."
        ),
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
