
import shutil
import tempfile
import warnings
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import earthaccess
import geopandas as gpd
from tqdm import tqdm

from swot_wse.config import (
    LAKESP_CACHE_DIR,
    load_config,
)


warnings.filterwarnings(
    "ignore",
    category=FutureWarning,
)


def has_match(value, valid_ids):
    """
    Check whether a semicolon-separated lake_id field
    contains one of the required lake IDs.
    """

    if value is None:
        return False

    ids = (
        str(value)
        .split(";")
    )

    return any(
        lake_id.strip() in valid_ids
        for lake_id in ids
    )


def find_observation_shapefile(folder: Path):
    """
    Locate the LakeSP observation shapefile.
    """

    shapefiles = sorted(
        folder.rglob("*.shp")
    )

    if not shapefiles:
        return None

    for shp in shapefiles:

        name = shp.name.lower()

        if (
            "obs" in name
            and "prior" not in name
            and "unknown" not in name
            and "unassigned" not in name
        ):
            return shp

    return shapefiles[0]


def _granule_filename(granule):
    """
    Return the LakeSP ZIP filename from a CMR granule.
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


def _process_granule(
    granule,
    polygon,
    lakesp_cache_enabled,
):
    """
    Download or reuse one LakeSP granule and verify
    whether it intersects the reservoir polygon.
    """

    config = load_config()

    temp_root = Path(
        config["temp_download_dir"]
    )

    temp_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    if lakesp_cache_enabled:

        LAKESP_CACHE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

    workdir = Path(
        tempfile.mkdtemp(
            dir=temp_root,
        )
    )

    temporary = False

    try:

        granule_filename = _granule_filename(
            granule
        )

        cached_zip = None

        if (
            lakesp_cache_enabled
            and granule_filename is not None
        ):

            candidate = (
                LAKESP_CACHE_DIR
                / granule_filename
            )

            if candidate.is_file():

                cached_zip = candidate

        if cached_zip is not None:

            zip_file = cached_zip

        else:

            downloaded = earthaccess.download(
                [granule],
                local_path=workdir,
            )

            if not downloaded:
                return None

            zip_file = Path(
                downloaded[0]
            )

        extract_dir = (
            workdir / "extract"
        )

        extract_dir.mkdir()

        with zipfile.ZipFile(zip_file) as zf:
            zf.extractall(extract_dir)

        shp = find_observation_shapefile(
            extract_dir
        )

        if shp is None:
            return None

        observations = gpd.read_file(
            shp
        )

        if observations.crs is None:
            raise RuntimeError(
                f"Observation shapefile has no CRS: "
                f"{shp.name}"
            )

        if polygon.crs is None:
            raise RuntimeError(
                "Reservoir polygon has no CRS."
            )

        polygon_for_intersection = (
            polygon.to_crs(
                observations.crs
            )
        )

        hits = observations[
            observations.intersects(
                polygon_for_intersection
                .geometry
                .iloc[0]
            )
        ]

        if hits.empty:
            return None

        lake_ids = set()

        for value in hits["lake_id"].dropna():

            for lake_id in str(value).split(";"):

                lake_id = lake_id.strip()

                if lake_id:
                    lake_ids.add(lake_id)

        if cached_zip is not None:

            final_zip = cached_zip

        elif lakesp_cache_enabled:

            final_zip = (
                LAKESP_CACHE_DIR
                / zip_file.name
            )

            if final_zip.exists():
                final_zip.unlink()

            shutil.move(
                zip_file,
                final_zip,
            )

        else:

            final_zip = (
                temp_root
                / f"{workdir.name}_{zip_file.name}"
            )

            shutil.move(
                zip_file,
                final_zip,
            )

            temporary = True

        return {
            "granule": granule,
            "zip": final_zip,
            "hits": len(hits),
            "lake_ids": sorted(lake_ids),
            "temporary": temporary,
        }

    except (
        zipfile.BadZipFile,
        OSError,
        RuntimeError,
        KeyError,
    ) as exc:

        print(
            f"\nError processing LakeSP granule: "
            f"{exc}"
        )

        return None

    finally:

        shutil.rmtree(
            workdir,
            ignore_errors=True,
        )


def discover_granules(
    granules,
    polygon,
    max_workers=None,
):
    """
    Discover LakeSP granules intersecting
    the reservoir footprint.
    """

    config = load_config()

    if max_workers is None:

        max_workers = config[
            "max_workers"
        ]

    lakesp_cache_enabled = config[
        "lakesp_cache_enabled"
    ]

    discovered = []

    with ThreadPoolExecutor(
        max_workers=max_workers,
    ) as executor:

        futures = [
            executor.submit(
                _process_granule,
                granule,
                polygon,
                lakesp_cache_enabled,
            )
            for granule in granules
        ]

        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Checking LakeSP granules",
            leave=False,
        ):

            result = future.result()

            if result is not None:

                discovered.append(
                    result
                )

    print(
        f"Verified LakeSP granules : "
        f"{len(discovered)}"
    )

    return discovered
