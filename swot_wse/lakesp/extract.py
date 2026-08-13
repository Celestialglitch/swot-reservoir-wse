from pathlib import Path
import shutil
import tempfile
import zipfile

import geopandas as gpd

from swot_wse.config import load_config


OUTPUT_COLUMNS = [
    "lake_id",
    "time_str",
    "wse",
    "wse_u",
    "quality_f",
    "partial_f",
]


def find_observation_shapefile(
    folder: Path,
):
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


def has_match(
    value,
    valid_ids,
):
    """
    Check whether a semicolon-separated lake_id field
    contains one of the required IDs.
    """

    if value is None:
        return False

    return any(
        lake_id.strip() in valid_ids
        for lake_id
        in str(value).split(";")
    )


def _load_matching_observations(
    zip_path: Path,
    valid_ids,
    geometry=True,
):
    """
    Extract one LakeSP granule and return
    observations matching the required lake IDs.
    """

    if not zip_path.exists():
        raise FileNotFoundError(
            f"LakeSP granule not found: "
            f"{zip_path}"
        )

    valid_ids = set(
        valid_ids
    )

    config = load_config()

    temp_root = Path(
        config[
            "temp_download_dir"
        ]
    )

    temp_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    workdir = Path(
        tempfile.mkdtemp(
            dir=temp_root,
        )
    )

    try:
        with zipfile.ZipFile(
            zip_path
        ) as archive:
            archive.extractall(
                workdir
            )

        shapefile = (
            find_observation_shapefile(
                workdir
            )
        )

        if shapefile is None:
            return None

        dataframe = gpd.read_file(
            shapefile,
            ignore_geometry=not geometry,
        )

        if dataframe.empty:
            return None

        missing_columns = [
            column
            for column in OUTPUT_COLUMNS
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise RuntimeError(
                "Missing required LakeSP fields: "
                + ", ".join(
                    missing_columns
                )
            )

        if geometry:
            if dataframe.crs is None:
                raise RuntimeError(
                    "LakeSP observation shapefile "
                    f"has no CRS: {shapefile.name}"
                )

            if dataframe.crs.to_epsg() != 4326:
                dataframe = (
                    dataframe.to_crs(
                        "EPSG:4326"
                    )
                )

        dataframe = dataframe[
            dataframe["lake_id"].apply(
                lambda value: has_match(
                    value,
                    valid_ids,
                )
            )
        ]

        if dataframe.empty:
            return None

        return dataframe

    finally:
        shutil.rmtree(
            workdir,
            ignore_errors=True,
        )


def extract_granule(
    zip_path: Path,
    lake_ids,
):
    """
    Extract and filter one LakeSP granule.
    """

    lakes = _load_matching_observations(
        zip_path,
        lake_ids,
        geometry=True,
    )

    if lakes is None:
        return None

    return (
        lakes[
            OUTPUT_COLUMNS
        ]
        .drop_duplicates(
            subset=[
                "lake_id",
                "time_str",
                "wse",
            ]
        )
        .reset_index(
            drop=True
        )
    )


def process_granule(job):
    """
    Process one LakeSP granule.

    Parameters
    ----------
    job : tuple
        Pair containing the ZIP path
        and associated lake IDs.
    """

    zip_path, lake_ids = job

    try:
        observations = (
            _load_matching_observations(
                zip_path,
                lake_ids,
                geometry=False,
            )
        )

        if observations is None:
            return None

        return (
            observations[
                OUTPUT_COLUMNS
            ]
            .drop_duplicates(
                subset=[
                    "lake_id",
                    "time_str",
                    "wse",
                ]
            )
            .reset_index(
                drop=True
            )
        )

    except (
        FileNotFoundError,
        zipfile.BadZipFile,
        OSError,
        RuntimeError,
        KeyError,
    ) as exc:
        print(
            f"Error processing "
            f"{zip_path.name}: {exc}"
        )

        return None