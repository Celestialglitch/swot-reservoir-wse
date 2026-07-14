from swot_wse.cache.polygon_cache import polygon_exists

def get_wse(lat, lon):
    """
    Main workflow for extracting a reservoir WSE time series.

    Parameters
    ----------
    lat : float
        Latitude of the user's point.

    lon : float
        Longitude of the user's point.
    """


def get_wse(lat, lon):

    if polygon_exists(lat, lon):
        print("✓ Polygon found in cache")
    else:
        print("✗ Polygon not found")

    print("Step 2 : Generate polygon if required")

    print("Step 3 : Search LakeSP")

    print("Step 4 : Fallback to PIXC if necessary")

    print("Step 5 : Return WSE time series")

    print("Step 2 : Generate polygon if required")

    print("Step 3 : Search LakeSP")

    print("Step 4 : Fallback to PIXC if necessary")

    print("Step 5 : Return WSE time series")