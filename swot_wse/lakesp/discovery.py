import shutil
import geopandas as gpd
from pathlib import Path
import tempfile
from tqdm import tqdm
import zipfile
import earthaccess
import warnings
from swot_wse.config import LAKESP_CACHE_DIR
from concurrent.futures import ThreadPoolExecutor, as_completed

# Suppress noisy warnings from geopandas/fiona
warnings.filterwarnings("ignore", category=FutureWarning)




def has_match(value, valid_ids):
    if value is None:
        return False
    ids = [x.strip() for x in str(value).split(";")]
    return any(i in valid_ids for i in ids)


def find_observation_shapefile(folder: Path):
    """Find the correct observation shapefile inside a granule folder."""
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



def _process_granule(granule, polygon):
    """Download and inspect one granule for reservoir intersection."""
    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            earthaccess.download([granule], local_path=tmp)

            zip_file = next(tmp.glob("*.zip"))
            extract_dir = tmp / "extract"
            extract_dir.mkdir()

            with zipfile.ZipFile(zip_file, "r") as zf:
                zf.extractall(extract_dir)

            shp = find_observation_shapefile(extract_dir)
            if shp is None:
                return None

            df = gpd.read_file(shp)

        
            hits = df[df.intersects(polygon.geometry.iloc[0])]
            if hits.empty:
                return None

            lake_ids = set()
            for value in hits["lake_id"].dropna():
                for lake_id in str(value).split(";"):
                    lake_id = lake_id.strip()
                    if lake_id:
                        lake_ids.add(lake_id)

            cache_zip = LAKESP_CACHE_DIR / zip_file.name
            shutil.move(zip_file, cache_zip)

            return {
                "granule": granule,
                "zip": cache_zip,
                "hits": len(hits),
                "lake_ids": sorted(lake_ids),
            }
    except Exception:
        return None



def discover_granules(granules, polygon, max_workers=None):
    """
    Discover LakeSP granules that intersect with the reservoir polygon.
    Downloads granules in parallel and caches them locally.
    """
    kept = []
    intersections = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_process_granule, g, polygon): g for g in granules}
        for future in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Checking LakeSP granules",
            leave=False,
        ):
            result = future.result()
            if result:
                intersections += 1
                kept.append(result)

    if intersections > 0:
        print(f"LakeSP intersections found: {intersections}")
    else:
        print("No LakeSP intersections found")

    return kept
