import ee

from swot_wse.config import load_config


_initialized = False


def initialize_earth_engine():
    """
    Initialize Google Earth Engine once.
    """

    global _initialized
    if _initialized:
        return

    project = load_config()["earth_engine_project"]

    if not project:

        raise RuntimeError(
            "Earth Engine project is not configured.\n"
            "Run:\n\n"
            "    swot-wse auth\n"
        )

    try:

        ee.Initialize(project=project)

    except Exception as exc:

        raise RuntimeError(
            "Failed to initialize Google Earth Engine.\n"
            "Please verify your authentication and project ID.\n"
            "Run 'swot-wse auth' if necessary."
        ) from exc

    _initialized = True
