import os
import ee

from swot_wse.config import load_config, save_config

_initialized = False

def initialize_earth_engine(project_id: str | None = None) -> None:
    """
    Initialize Google Earth Engine for the given project.
    Prompts interactively if no project ID is provided.
    """
    global _initialized
    if _initialized:
        return
    config = load_config()
    project_id = project_id or os.getenv("EE_PROJECT_ID") or config.get("earth_engine_project")
    if not project_id:
        project_id = input("Enter your Google Earth Engine project ID: ").strip()
        if not project_id:
            print("No project ID provided. Exiting.")
            return
        config["earth_engine_project"] = project_id
        save_config(config)

    try:
        ee.Initialize(project=project_id)
    except ee.EEException:
        print("Authenticating Google Earth Engine...")
        ee.Authenticate()
        ee.Initialize(project=project_id)

    _initialized = True
