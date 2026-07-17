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
        project_id = input("Enter your Earth Engine project ID: ").strip()
        if not project_id:
            print("No project ID provided. Exiting.")
            return

    try:
        ee.Initialize(project=project_id)
        print(f"Earth Engine initialized successfully !")

    except ee.EEException:
        print(f"Failed to initialize Earth Engine with project '{project_id}'.")
        print("Please check validity of your project ID ")
        return

    except Exception:
        print("Authenticating Earth Engine...")
        ee.Authenticate()
        try:
            ee.Initialize(project=project_id)
        except ee.EEException:
            print(f"Project '{project_id}' is invalid or inaccessible.")
            return

    _initialized = True
