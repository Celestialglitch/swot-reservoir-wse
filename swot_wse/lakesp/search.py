import earthaccess

# -------------------------------------------------
# Configuration
# -------------------------------------------------
SEARCH_BUFFER_DEGREES = 0.5
COLLECTION = "SWOT_L2_HR_LakeSP_Obs_D"

SCIENCE_PHASE_CYCLES = {
    f"{cycle:03d}" for cycle in range(1, 53)
}

_logged_in = False


# -------------------------------------------------
# Login
# -------------------------------------------------
def login():
    
    global _logged_in

    if _logged_in:
        return

    earthaccess.login(strategy="interactive")
    _logged_in = True


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def _granule_filename(granule):
    try:
        links = granule.data_links()
        if not links:
            return None
        return links[0].split("/")[-1]
    except Exception:
        return None


def _cycle_from_filename(filename):
    try:
        return filename.split("_")[5]
    except Exception:
        return None


# -------------------------------------------------
# Search
# -------------------------------------------------
def search_lakesp_granules(polygon, start_date, end_date):
    """
    Search NASA CMR for candidate LakeSP granules within the boundary.
    """
    login()

    xmin, ymin, xmax, ymax = polygon.total_bounds
    xmin -= SEARCH_BUFFER_DEGREES
    ymin -= SEARCH_BUFFER_DEGREES
    xmax += SEARCH_BUFFER_DEGREES
    ymax += SEARCH_BUFFER_DEGREES

    raw_granules = earthaccess.search_data(
        short_name=COLLECTION,
        bounding_box=(xmin, ymin, xmax, ymax),
        temporal=(start_date, end_date),
    )

    invalid = 0
    calibration = 0
    unique = {}

    for granule in raw_granules:
        filename = _granule_filename(granule)
        if filename is None:
            invalid += 1
            continue

        cycle = _cycle_from_filename(filename)
        if cycle not in SCIENCE_PHASE_CYCLES:
            calibration += 1
            continue

        unique[filename] = granule

    granules = list(unique.values())
    granules.sort(key=lambda g: _granule_filename(g))

    return granules
