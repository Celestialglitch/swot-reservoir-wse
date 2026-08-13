import earthaccess

from swot_reservoir_wse.config import load_config
from swot_reservoir_wse.earthdata import initialize_earthdata


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
    Extract the SWOT science cycle from a LakeSP filename.
    """

    try:
        return filename.split("_")[5]

    except (AttributeError, IndexError):
        return None


def search_lakesp_granules(
    polygon,
    start_date,
    end_date,
):
    """
    Search NASA CMR for candidate LakeSP granules.
    """

    initialize_earthdata()

    config = load_config()
    lakesp_config = config["sources"]["lakesp"]

    search_buffer_degrees = (
        lakesp_config["search_buffer_degrees"]
    )

    collection = lakesp_config["collection"]

    science_cycles = set(
        lakesp_config["science_cycles"]
    )

    xmin, ymin, xmax, ymax = (
        polygon.total_bounds
    )

    bbox = (
        xmin - search_buffer_degrees,
        ymin - search_buffer_degrees,
        xmax + search_buffer_degrees,
        ymax + search_buffer_degrees,
    )

    raw_granules = earthaccess.search_data(
        short_name=collection,
        bounding_box=bbox,
        temporal=(
            start_date,
            end_date,
        ),
        count=-1,
    )

    unique = {}

    for granule in raw_granules:
        filename = _granule_filename(
            granule
        )

        if filename is None:
            continue

        cycle = _cycle_from_filename(
            filename
        )

        if cycle not in science_cycles:
            continue

        unique[
            filename
        ] = granule

    granules = sorted(
        unique.values(),
        key=_granule_filename,
    )

    print(
        f"Candidate LakeSP granules : "
        f"{len(granules)}"
    )

    return granules