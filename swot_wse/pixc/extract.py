from pathlib import Path
import shutil
import tempfile

import earthaccess
import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr

from swot_wse.config import (
    RUNTIME_ROOT,
    load_config,
)


# Bits 0 and 1 of classification_qual are excluded by the current PIXC workflow.
BAD_CLASSIFICATION_FLAGS = (
    (1 << 0)
    | (1 << 1)
)


def _resolve_temp_directory(path):
    """
    Resolve the configured temporary
    processing directory.
    """

    path = Path(path).expanduser()

    if not path.is_absolute():
        path = RUNTIME_ROOT / path

    return path.resolve()


def _granule_filename(granule):
    """
    Return a readable filename for an
    Earthaccess granule.
    """

    try:
        links = granule.data_links()

        if not links:
            return None

        return Path(
            links[0]
        ).name

    except Exception:
        return None


def _acquisition_time(
    dataset,
    nc_file,
):
    """
    Determine the PIXC acquisition time.

    """

    time_string = (
        dataset.attrs.get(
            "time_coverage_start"
        )
        or dataset.attrs.get(
            "time_granule_start"
        )
    )

    if isinstance(
        time_string,
        bytes,
    ):
        time_string = (
            time_string.decode()
        )

    if time_string is not None:
        acquisition_time = (
            pd.to_datetime(
                time_string,
                errors="coerce",
            )
        )

        if not pd.isna(
            acquisition_time
        ):
            return acquisition_time

    # Example:
    #
    # SWOT_L2_HR_PIXC_044_505_151L_20260121T102634_20260121T102641_PID0_01.nc
    # Index 7 contains the start time.

    parts = nc_file.stem.split("_")

    try:
        time_string = parts[7]

    except IndexError as exc:
        raise RuntimeError(
            "Could not determine PIXC "
            "acquisition time from "
            f"{nc_file.name}."
        ) from exc

    acquisition_time = (
        pd.to_datetime(
            time_string,
            format="%Y%m%dT%H%M%S",
            errors="coerce",
        )
    )

    if pd.isna(
        acquisition_time
    ):
        raise RuntimeError(
            "Could not parse PIXC "
            "acquisition time from "
            f"{nc_file.name}."
        )

    return acquisition_time


def process_pixc_granule(
    granule,
    reservoir_polygon,
):
    """
    Process one verified PIXC granule and
    return accepted reservoir pixels.
    """

    if (
        reservoir_polygon is None
        or reservoir_polygon.empty
    ):
        raise ValueError(
            "A valid reservoir polygon is "
            "required for PIXC extraction."
        )

    if reservoir_polygon.crs is None:
        raise RuntimeError(
            "Reservoir polygon has no CRS."
        )

    config = load_config()
    pixc_config = config["sources"]["pixc"]

    water_classification = int(
        pixc_config[
            "water_classification"
        ]
    )

    temp_root = (
        _resolve_temp_directory(
            config[
                "temp_download_dir"
            ]
        )
    )

    temp_root.mkdir(
        parents=True,
        exist_ok=True,
    )

    polygon_wgs84 = (
        reservoir_polygon.to_crs(
            "EPSG:4326"
        )
    )

    reservoir = (
        polygon_wgs84
        .geometry
        .iloc[0]
    )

    xmin, ymin, xmax, ymax = (
        reservoir.bounds
    )

    workdir = Path(
        tempfile.mkdtemp(
            prefix="pixc_",
            dir=temp_root,
        )
    )

    try:
        downloaded = (
            earthaccess.download(
                [granule],
                local_path=workdir,
            )
        )

        if not downloaded:
            return None

        nc_file = Path(
            downloaded[0]
        )

        if not nc_file.is_file():
            raise RuntimeError(
                "Downloaded PIXC file "
                "could not be located."
            )

        with xr.open_dataset(
            nc_file,
            group="pixel_cloud",
            engine="h5netcdf",
        ) as dataset:
            longitude = (
                dataset[
                    "longitude"
                ].values
            )

            latitude = (
                dataset[
                    "latitude"
                ].values
            )

            bbox_mask = (
                np.isfinite(longitude)
                & np.isfinite(latitude)
                & (longitude >= xmin)
                & (longitude <= xmax)
                & (latitude >= ymin)
                & (latitude <= ymax)
            )

            if not np.any(
                bbox_mask
            ):
                return None

            longitude = (
                longitude[
                    bbox_mask
                ]
            )

            latitude = (
                latitude[
                    bbox_mask
                ]
            )

            height = (
                dataset[
                    "height"
                ]
                .values[
                    bbox_mask
                ]
            )

            geoid = (
                dataset[
                    "geoid"
                ]
                .values[
                    bbox_mask
                ]
            )

            classification = (
                dataset[
                    "classification"
                ]
                .values[
                    bbox_mask
                ]
            )

            classification_qual = (
                dataset[
                    "classification_qual"
                ]
                .values[
                    bbox_mask
                ]
            )

            if "water_frac" in dataset:
                water_frac = (
                    dataset[
                        "water_frac"
                    ]
                    .values[
                        bbox_mask
                    ]
                )

            else:
                water_frac = (
                    np.ones_like(
                        height,
                        dtype=float,
                    )
                )

            if "phase_noise_std" in dataset:
                phase_noise_std = (
                    dataset[
                        "phase_noise_std"
                    ]
                    .values[
                        bbox_mask
                    ]
                )

            else:
                phase_noise_std = (
                    np.zeros_like(
                        height,
                        dtype=float,
                    )
                )

            if (
                "cross_track_distance"
                in dataset
            ):
                cross_track_distance = (
                    dataset[
                        "cross_track_distance"
                    ]
                    .values[
                        bbox_mask
                    ]
                )

            else:
                cross_track_distance = (
                    np.full_like(
                        height,
                        np.nan,
                        dtype=float,
                    )
                )

            acquisition_time = (
                _acquisition_time(
                    dataset,
                    nc_file,
                )
            )

        dataframe = pd.DataFrame(
            {
                "longitude": longitude,
                "latitude": latitude,
                "height": height,
                "geoid": geoid,
                "classification": classification,
                "classification_qual": (
                    classification_qual
                ),
                "water_frac": water_frac,
                "phase_noise_std": (
                    phase_noise_std
                ),
                "cross_track_distance": (
                    cross_track_distance
                ),
            }
        )

        dataframe = dataframe[
            np.isfinite(
                dataframe["height"]
            )
            & np.isfinite(
                dataframe["geoid"]
            )
        ].copy()

        if dataframe.empty:
            return None

        points = gpd.GeoDataFrame(
            dataframe,
            geometry=gpd.points_from_xy(
                dataframe["longitude"],
                dataframe["latitude"],
            ),
            crs="EPSG:4326",
        )

        hits = points[
            points.geometry.intersects(
                reservoir
            )
        ].copy()

        if hits.empty:
            return None

        hits = hits[
            hits["classification"]
            == water_classification
        ].copy()

        if hits.empty:
            return None

        quality = (
            hits[
                "classification_qual"
            ]
            .fillna(0)
            .astype(np.int64)
        )

        hits = hits[
            (
                quality
                & BAD_CLASSIFICATION_FLAGS
            )
            == 0
        ].copy()

        if hits.empty:
            return None

        hits["wse"] = (
            hits["height"]
            - hits["geoid"]
        )

        hits = hits[
            np.isfinite(
                hits["wse"]
            )
        ].copy()

        if hits.empty:
            return None

        hits[
            "time_str"
        ] = acquisition_time

        return (
            hits[
                [
                    "time_str",
                    "wse",
                    "longitude",
                    "latitude",
                    "water_frac",
                    "phase_noise_std",
                    "cross_track_distance",
                ]
            ]
            .reset_index(
                drop=True
            )
        )

    except (
        OSError,
        RuntimeError,
        KeyError,
        ValueError,
    ) as exc:
        filename = (
            _granule_filename(
                granule
            )
            or "Unknown PIXC granule"
        )

        print(
            f"\nError processing "
            f"{filename}: {exc}"
        )

        return None

    finally:
        shutil.rmtree(
            workdir,
            ignore_errors=True,
        )