import ee

PROJECT_ID = "iitbinternship"


_initialized = False


def initialize_earth_engine():
    global _initialized

    if _initialized:
        return

    try:
        ee.Initialize(project=PROJECT_ID)

    except Exception:

        print("Authenticating Earth Engine...")

        ee.Authenticate()

        ee.Initialize(project=PROJECT_ID)

    _initialized = True