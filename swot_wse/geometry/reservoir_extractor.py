import ee
import geemap
import geopandas as gpd

SEARCH_RADIUS_M = 50000
PEKEL_THRESHOLD = 20


def extract_reservoir_polygon(lat: float, lon: float) -> gpd.GeoDataFrame:
    """
    Extract the reservoir footprint surrounding a user supplied point
    using the JRC Global Surface Water (Pekel) dataset.

    Parameters
    ----------
    lat : float
        Latitude.
    lon : float
        Longitude.

    Returns
    -------
    GeoDataFrame
        Single polygon representing the reservoir footprint.
    """

    # ---------------------------------------
    # Build Earth Engine geometries
    # ---------------------------------------

    point = ee.Geometry.Point([lon, lat])
    search_area = point.buffer(SEARCH_RADIUS_M)

    # ---------------------------------------
    # Load Pekel occurrence
    # ---------------------------------------

    occurrence = (
        ee.Image("JRC/GSW1_4/GlobalSurfaceWater")
        .select("occurrence")
    )

    water = (
        occurrence
        .gt(PEKEL_THRESHOLD)
        .focal_max(radius=1, units="pixels")
    )

    local_water = water.clip(search_area)

    # ---------------------------------------
    # Raster -> Vector
    # ---------------------------------------

    polygons = local_water.selfMask().reduceToVectors(
        geometry=search_area,
        scale=30,
        geometryType="polygon",
        eightConnected=True,
        maxPixels=1e10,
    )

    gdf = geemap.ee_to_gdf(polygons)

    if gdf.empty:
        raise RuntimeError(
            "No reservoir polygon could be extracted."
        )

    # ---------------------------------------
    # Work in projected CRS
    # ---------------------------------------

    WORKING_CRS = "EPSG:32721"

    gdf = gdf.to_crs(WORKING_CRS)

    dam = (
        gpd.GeoDataFrame(
            geometry=gpd.points_from_xy([lon], [lat]),
            crs="EPSG:4326",
        )
        .to_crs(WORKING_CRS)
    )

    dam_point = dam.iloc[0].geometry

    # ---------------------------------------
    # Select best polygon
    # ---------------------------------------

    containing = gdf[gdf.geometry.contains(dam_point)]

    if not containing.empty:

        containing["area_m2"] = containing.geometry.area

        selected = (
            containing
            .sort_values("area_m2", ascending=False)
            .head(1)
            .copy()
        )

        selected["selection_method"] = "DAM_INSIDE_POLYGON"

    else:

        gdf["distance_m"] = gdf.geometry.distance(dam_point)

        selected = (
            gdf
            .sort_values("distance_m")
            .head(1)
            .copy()
        )

        selected["selection_method"] = "NEAREST_POLYGON"

    return selected.to_crs("EPSG:4326")