
from pathlib import Path
import copy
import json
import os


PACKAGE_ROOT = Path(__file__).resolve().parent.parent

CONFIG_FILE = PACKAGE_ROOT / "config.json"


DEFAULT_CONFIG = {

    # ------------------------------------------
    # Google Earth Engine
    # ------------------------------------------

    "earth_engine_project": None,

    # ------------------------------------------
    # Reservoir extraction
    # ------------------------------------------

    "search_radius_m": 50000,
    "pekel_threshold": 20,
    "working_crs": "auto",

    # ------------------------------------------
    # Parallel processing
    # ------------------------------------------

    "max_workers": max(
        1,
        (os.cpu_count() or 1) - 1,
    ),

    # ------------------------------------------
    # Behaviour
    # ------------------------------------------

    "generate_plot": True,
    "polygon_cache_enabled": True,
    "lakesp_cache_enabled": True,

    # ------------------------------------------
    # Runtime directories
    # ------------------------------------------

    "cache_dir": str(
        PACKAGE_ROOT / "cache"
    ),

    "output_dir": str(
        PACKAGE_ROOT / "outputs"
    ),

    # ------------------------------------------
    # Temporary extraction workspace
    # ------------------------------------------

    "temp_download_dir": str(
        PACKAGE_ROOT / "downloads" / "temp"
    ),

    # ------------------------------------------
    # Observation sources
    # ------------------------------------------

    "sources": {

        "lakesp": {

            "collection": "SWOT_L2_HR_LakeSP_Obs_D",

            "search_buffer_degrees": 0.5,

            "science_cycles": [
                f"{i:03d}"
                for i in range(1, 53)
            ],

            "mad_threshold": 3.0,

        },

    },

}


def _merge_config(default, user):
    """
    Recursively merge user configuration with defaults.
    """

    merged = copy.deepcopy(default)

    for key, value in user.items():

        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):

            merged[key] = _merge_config(
                merged[key],
                value,
            )

        else:

            merged[key] = value

    return merged


def load_config():
    """
    Load package configuration.

    Missing keys are automatically restored
    from DEFAULT_CONFIG.
    """

    config = copy.deepcopy(DEFAULT_CONFIG)

    if CONFIG_FILE.exists():

        with open(
            CONFIG_FILE,
            "r",
            encoding="utf-8",
        ) as f:

            user = json.load(f)

        if not isinstance(user, dict):
            raise RuntimeError(
                "Configuration file must contain a JSON object."
            )

        config = _merge_config(
            config,
            user,
        )

    return config


def save_config(config):
    """
    Save configuration to disk.
    """

    CONFIG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        CONFIG_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            config,
            f,
            indent=4,
        )


def _resolve_directory(path):
    """
    Resolve a configured directory path.

    Relative paths are resolved from the package root.
    """

    path = Path(path).expanduser()

    if not path.is_absolute():
        path = PACKAGE_ROOT / path

    return path.resolve()


CONFIG = load_config()


CACHE_DIR = _resolve_directory(
    CONFIG["cache_dir"]
)

POLYGON_CACHE_DIR = (
    CACHE_DIR / "reservoir_polygons"
)

LAKESP_CACHE_DIR = (
    CACHE_DIR / "lakesp_granules"
)


DATA_DIR = PACKAGE_ROOT / "data"

DOWNLOAD_DIR = PACKAGE_ROOT / "downloads"

TEMP_DOWNLOAD_DIR = _resolve_directory(
    CONFIG["temp_download_dir"]
)


OUTPUT_DIR = _resolve_directory(
    CONFIG["output_dir"]
)


def initialize_directories():
    """
    Create all package directories.
    """

    for directory in (

        CACHE_DIR,
        POLYGON_CACHE_DIR,
        LAKESP_CACHE_DIR,

        DATA_DIR,
        DOWNLOAD_DIR,
        TEMP_DOWNLOAD_DIR,

        OUTPUT_DIR,

    ):

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    if not CONFIG_FILE.exists():

        save_config(
            copy.deepcopy(DEFAULT_CONFIG)
        )
