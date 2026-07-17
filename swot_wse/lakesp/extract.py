from pathlib import Path
import tempfile
import zipfile
import geopandas as gpd


OUTPUT_COLUMNS = [
    "lake_id",
    "time_str",
    "wse",
    "wse_u",
    "area_total",
    "quality_f",
    "partial_f",
]



def find_observation_shapefile(folder: Path):
    """Locate the correct observation shapefile inside a granule folder."""
    shp_files = sorted(folder.rglob("*.shp"))
    if not shp_files:
        return None

    for shp in shp_files:
        name = shp.name.lower()
        if (
            "obs" in name
            and "prior" not in name
            and "unknown" not in name
            and "unassigned" not in name
        ):
            return shp
    return shp_files[0]



def has_match(value, valid_ids):
    """Check if any of the semicolon-separated lake_ids match the valid set."""
    if value is None:
        return False
    ids = [x.strip() for x in str(value).split(";")]
    return any(i in valid_ids for i in ids)



def extract_granule(zip_path: Path, lake_ids):
    """Extract and filter a granule ZIP for matching lake_ids."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(tmpdir)

        shp = find_observation_shapefile(Path(tmpdir))
        if shp is None:
            return None

        lakes = gpd.read_file(shp)
        if lakes.empty:
            return None

        # Ensure CRS is WGS84
        if lakes.crs is None:
            lakes = lakes.set_crs("EPSG:4326")
        elif lakes.crs.to_epsg() != 4326:
            lakes = lakes.to_crs("EPSG:4326")

        lakes = lakes[lakes["lake_id"].apply(lambda x: has_match(x, set(lake_ids)))]
        if lakes.empty:
            return None

        lakes = lakes[OUTPUT_COLUMNS].copy()
        lakes = lakes.drop_duplicates(
            subset=["lake_id", "time_str", "wse"]
        ).reset_index(drop=True)

        return lakes



def process_granule(job):
    """
    Process a cached granule ZIP for matching lake_ids.

    Parameters
    ----------
    job : tuple
        (zip_path, lake_ids)
        zip_path : Path to cached granule ZIP
        lake_ids : list of normalized lake IDs
    """
    zip_path, lake_ids = job
    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            with tempfile.TemporaryDirectory() as tmpdir:
                zf.extractall(tmpdir)

                shp = find_observation_shapefile(Path(tmpdir))
                if shp is None:
                    print(f"No observation shapefile found in {zip_path}")
                    return None

                df = gpd.read_file(shp, ignore_geometry=True)

                df = df[df["lake_id"].apply(lambda x: has_match(x, set(lake_ids)))]
                if df.empty:
                    print(f"No matching lake_ids in {zip_path}")
                    return None

                return df
    except Exception as e:
        print(f"Error processing {zip_path}: {e}")
        return None
