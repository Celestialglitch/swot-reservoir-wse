from pathlib import Path
import copy
import json
import os


# -------------------------------------------------
# Package runtime location
# -------------------------------------------------

RUNTIME_ROOT = (
    Path.home()
    / ".swot_wse"
).resolve()


CONFIG_FILE = (
    RUNTIME_ROOT
    / "config.json"
)


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
        RUNTIME_ROOT / "cache"
    ),

    "output_dir": str(
        RUNTIME_ROOT / "outputs"
    ),

    # ------------------------------------------
    # Temporary extraction workspace
    # ------------------------------------------

    "temp_download_dir": str(
        RUNTIME_ROOT
        / "downloads"
        / "temp"
    ),

    # ------------------------------------------
    # Observation sources
    # ------------------------------------------

    "sources": {

        "lakesp": {

            "collection": (
                "SWOT_L2_HR_LakeSP_Obs_D"
            ),

            "search_buffer_degrees": 0.5,

            "science_cycles": [
                f"{i:03d}"
                for i in range(1, 53)
            ],

            "mad_threshold": 3.0,

        },

    },

}


def _merge_config(
    default,
    user,
):
    """
    Recursively merge user configuration
    with the package defaults.

    Unknown configuration keys are ignored.
    """

    merged = copy.deepcopy(
        default
    )

    for key, value in user.items():

        if key not in merged:
            continue

        if (
            isinstance(
                merged[key],
                dict,
            )
            and isinstance(
                value,
                dict,
            )
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
    Load the active package configuration.

    Missing configuration values are restored
    automatically from DEFAULT_CONFIG.
    """

    config = copy.deepcopy(
        DEFAULT_CONFIG
    )

    if CONFIG_FILE.exists():

        try:

            with open(
                CONFIG_FILE,
                "r",
                encoding="utf-8",
            ) as file:

                user = json.load(
                    file
                )

        except json.JSONDecodeError as exc:

            raise RuntimeError(
                "The swot-reservoir-wse "
                "configuration file is invalid:\n\n"
                f"    {CONFIG_FILE}"
            ) from exc

        except OSError as exc:

            raise RuntimeError(
                "The swot-reservoir-wse "
                "configuration file could not "
                "be read."
            ) from exc

        if not isinstance(
            user,
            dict,
        ):

            raise RuntimeError(
                "Configuration file must "
                "contain a JSON object."
            )

        config = _merge_config(
            config,
            user,
        )

    return config


def save_config(config):
    """
    Save package configuration.
    """

    RUNTIME_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:

        with open(
            CONFIG_FILE,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                config,
                file,
                indent=4,
            )

    except OSError as exc:

        raise RuntimeError(
            "The swot-reservoir-wse "
            "configuration could not be saved."
        ) from exc


def _resolve_directory(path):
    """
    Resolve a configured directory path.

    Relative paths are resolved from the
    swot-reservoir-wse runtime directory.
    """

    path = Path(
        path
    ).expanduser()

    if not path.is_absolute():

        path = (
            RUNTIME_ROOT
            / path
        )

    return path.resolve()


CONFIG = load_config()


CACHE_DIR = _resolve_directory(
    CONFIG["cache_dir"]
)


POLYGON_CACHE_DIR = (
    CACHE_DIR
    / "reservoir_polygons"
)


LAKESP_CACHE_DIR = (
    CACHE_DIR
    / "lakesp_granules"
)


DOWNLOAD_DIR = (
    RUNTIME_ROOT
    / "downloads"
)


TEMP_DOWNLOAD_DIR = _resolve_directory(
    CONFIG[
        "temp_download_dir"
    ]
)


OUTPUT_DIR = _resolve_directory(
    CONFIG[
        "output_dir"
    ]
)


def initialize_directories():
    """
    Create all runtime directories required
    by the package.
    """

    for directory in (

        RUNTIME_ROOT,

        CACHE_DIR,
        POLYGON_CACHE_DIR,
        LAKESP_CACHE_DIR,

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
            copy.deepcopy(
                DEFAULT_CONFIG
            )
        )