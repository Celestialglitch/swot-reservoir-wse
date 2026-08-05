import earthaccess

from swot_wse.config import load_config


CONFIG = load_config()

SEARCH_BUFFER_DEGREES = CONFIG["sources"]["lakesp"]["search_buffer_degrees"]
COLLECTION = CONFIG["sources"]["lakesp"]["collection"]
SCIENCE_PHASE_CYCLES = set(CONFIG["sources"]["lakesp"]["science_cycles"])

_logged_in = False


def login():
    """
    Authenticate with NASA Earthdata once per session.
    """

    global _logged_in

    if _logged_in:
        return

    earthaccess.login(strategy="interactive")
    _logged_in = True


def _granule_filename(granule):
    """
    Return the LakeSP filename from a CMR granule.
    """

    try:

        links = granule.data_links()

        if not links:
            return None

        return links[0].split("/")[-1]

    except Exception:
        return None


def _cycle_from_filename(filename):
    """
    Extract SWOT science cycle from a LakeSP filename.
    """

    try:
        return filename.split("_")[5]

    except Exception:
        return None


def search_lakesp_granules(
    polygon,
    start_date,
    end_date,
):
    """
    Search NASA CMR for candidate LakeSP granules.
    """

    login()

    xmin, ymin, xmax, ymax = polygon.total_bounds

    bbox = (
        xmin - SEARCH_BUFFER_DEGREES,
        ymin - SEARCH_BUFFER_DEGREES,
        xmax + SEARCH_BUFFER_DEGREES,
        ymax + SEARCH_BUFFER_DEGREES,
    )

    raw_granules = earthaccess.search_data(
        short_name=COLLECTION,
        bounding_box=bbox,
        temporal=(start_date, end_date),
        count=-1,
    )

    unique = {}

    for granule in raw_granules:

        filename = _granule_filename(granule)

        if filename is None:
            continue

        cycle = _cycle_from_filename(filename)

        if cycle not in SCIENCE_PHASE_CYCLES:
            continue

        unique[filename] = granule

    granules = sorted(
        unique.values(),
        key=_granule_filename,
    )

    print(f"Candidate LakeSP granules : {len(granules)}")

    return granules