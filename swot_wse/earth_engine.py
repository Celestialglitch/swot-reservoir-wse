import os
import ee

_initialized = False

def initialize_earth_engine(project_id: str | None = None) -> None:
    """
    Initialize Google Earth Engine for the given project.
    Prompts interactively if no project ID is provided.
    """
    global _initialized
    if _initialized:
        return

    project_id = project_id or os.getenv("EE_PROJECT_ID")
    if not project_id:
        project_id = input("Enter your Google Earth Engine project ID: ").strip()
        if not project_id:
            print("No project ID provided. Exiting.")
            return

    try:
        ee.Initialize(project=project_id)
    except ee.EEException:
        print("Authenticating Google Earth Engine...")
        ee.Authenticate()
        ee.Initialize(project=project_id)

    _initialized = True
