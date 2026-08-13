from pathlib import Path
from urllib.parse import urlparse

import earthaccess

from swot_wse.config import load_config


def _granule_filename(granule):
    """
    Return the PIXC filename associated with
    an Earthaccess granule.
    """

    try:
        links = granule.data_links()

        if not links:
            return None

        return Path(
            urlparse(links[0]).path
        ).name

    except Exception:
        return None


def _extract_cycle(filename):
    """
    Extract the SWOT cycle number from
    a PIXC granule filename.
    """

    if not filename:
        return None

    parts = filename.split("_")

    try:
        return parts[4]

    except IndexError:
        return None


def search_pixc_granules(
    reservoir_polygon,
    start_date,
    end_date,
):
    """
    Search NASA Earthdata for candidate
    SWOT PIXC granules.

    This stage performs metadata discovery only.
    """

    config = load_config()
    pixc_config = config["sources"]["pixc"]

    collection = pixc_config["collection"]
    search_buffer = (
        pixc_config["search_buffer_degrees"]
    )

    science_cycles = {
        str(cycle).zfill(3)
        for cycle in pixc_config[
            "science_cycles"
        ]
    }

    if (
        reservoir_polygon is None
        or reservoir_polygon.empty
    ):
        raise ValueError(
            "A valid reservoir polygon is "
            "required for PIXC granule search."
        )

    xmin, ymin, xmax, ymax = (
        reservoir_polygon.total_bounds
    )

    bounding_box = (
        xmin - search_buffer,
        ymin - search_buffer,
        xmax + search_buffer,
        ymax + search_buffer,
    )

    print(
        "\nSearching NASA Earthdata "
        "for PIXC granules..."
    )

    raw_granules = earthaccess.search_data(
        short_name=collection,
        temporal=(
            start_date,
            end_date,
        ),
        bounding_box=bounding_box,
        count=-1,
    )

    print(
        f"Raw PIXC granules       : "
        f"{len(raw_granules)}"
    )

    granules_by_filename = {}

    for granule in raw_granules:
        filename = _granule_filename(
            granule
        )

        if filename is None:
            continue

        cycle = _extract_cycle(
            filename
        )

        if cycle not in science_cycles:
            continue

        granules_by_filename[
            filename
        ] = granule

    candidate_granules = sorted(
        granules_by_filename.values(),
        key=lambda granule: (
            _granule_filename(granule)
            or ""
        ),
    )

    print(
        f"Candidate PIXC granules : "
        f"{len(candidate_granules)}"
    )

    return candidate_granules