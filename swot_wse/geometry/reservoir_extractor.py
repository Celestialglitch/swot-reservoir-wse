import ee
import geemap
import geopandas as gpd


SEARCH_RADIUS_M = 50_000
PEKEL_THRESHOLD = 20

# Raster-to-Vector conversion commonly produces small minor fragments. Following common practice, we ignore any polygons smaller than 0.1 km² (100,000 m²) when selecting the reservoir footprint."
MIN_PLAUSIBLE_AREA_M2 = 100_000


def extract_reservoir_polygon(lat: float, lon: float) -> gpd.GeoDataFrame:
    """
    Extract the reservoir footprint surrounding a user-supplied point
    using the JRC Global Surface Water (Pekel) dataset.

    Parameters
    ----------
    lat : float
        Latitude of the dam/reservoir point.
    lon : float
        Longitude of the dam/reservoir point.

    Returns
    -------
    GeoDataFrame
        Single polygon representing the reservoir footprint.
    """

    # ---------------------------------------------------------
    # Earth Engine geometries
    # ---------------------------------------------------------
    point = ee.Geometry.Point([lon, lat])
    search_area = point.buffer(SEARCH_RADIUS_M)

    # ---------------------------------------------------------
    # Pekel occurrence
    # ---------------------------------------------------------
    occurrence = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
    water = occurrence.gt(PEKEL_THRESHOLD).focal_max(radius=1, units="pixels")
    local_water = water.clip(search_area)

    # ---------------------------------------------------------
    # Raster -> Vector
    # ---------------------------------------------------------
    polygons = local_water.selfMask().reduceToVectors(
        geometry=search_area,
        scale=30,
        geometryType="polygon",
        eightConnected=True,
        maxPixels=1e10,
    )

    gdf = geemap.ee_to_gdf(polygons)
    if gdf.empty:
        raise RuntimeError("No reservoir polygon could be extracted.")

    # ---------------------------------------------------------
    # Project everything into metric CRS
    # ---------------------------------------------------------
    WORKING_CRS = "EPSG:32721"
    gdf = gdf.to_crs(WORKING_CRS)

    dam = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy([lon], [lat]),
        crs="EPSG:4326",
    ).to_crs(WORKING_CRS)

    dam_point = dam.geometry.iloc[0]

   
    gdf["area_m2"] = gdf.geometry.area

    # ---------------------------------------------------------
    # First condition: Reservoir containing the dam
    # ---------------------------------------------------------
    containing = gdf[gdf.geometry.contains(dam_point)].copy()
    if not containing.empty:
        selected = containing.sort_values("area_m2", ascending=False).head(1).copy()
        selected["selection_method"] = "DAM_INSIDE_POLYGON"
        print(f"Selected containing polygon ({selected.area_m2.iloc[0]:,.0f} m²)")
        return selected.to_crs("EPSG:4326")

    # ---------------------------------------------------------
    # Second condition: Nearest plausible polygon
    # ---------------------------------------------------------
    candidates = gdf[gdf["area_m2"] >= MIN_PLAUSIBLE_AREA_M2].copy()
    if candidates.empty:
        raise RuntimeError("Only tiny water fragments were found near the supplied point.")

    candidates["distance_m"] = candidates.geometry.distance(dam_point)
    selected = candidates.sort_values("distance_m").head(1).copy()
    selected["selection_method"] = "NEAREST_POLYGON"

    print(
        f"Nearest polygon selected "
        f"(distance = {selected.distance_m.iloc[0]:.1f} m, "
        f"area = {selected.area_m2.iloc[0]:,.0f} m²)"
    )

    return selected.to_crs("EPSG:4326")
