import ee
import geemap
import geopandas as gpd

from swot_reservoir_wse.config import load_config


CONFIG = load_config()

SEARCH_RADIUS_M = CONFIG["search_radius_m"]
PEKEL_THRESHOLD = CONFIG["pekel_threshold"]
WORKING_CRS = CONFIG["working_crs"]


def extract_reservoir_polygon(
    lat: float,
    lon: float,
) -> gpd.GeoDataFrame:
    """
    Extract the reservoir footprint surrounding a user-supplied point
    using the JRC Global Surface Water dataset.
    """

    point = ee.Geometry.Point(
        [lon, lat]
    )

    search_area = point.buffer(
        SEARCH_RADIUS_M
    )

    water = (
        ee.Image(
            "JRC/GSW1_4/GlobalSurfaceWater"
        )
        .select("occurrence")
        .gt(PEKEL_THRESHOLD)
        .focal_max(
            radius=1,
            units="pixels",
        )
        .clip(search_area)
    )

    polygons = water.selfMask().reduceToVectors(
        geometry=search_area,
        scale=30,
        geometryType="polygon",
        eightConnected=True,
        maxPixels=1e10,
    )

    if polygons.size().getInfo() == 0:
        return None

    gdf = geemap.ee_to_gdf(
        polygons
    )

    if gdf.empty:
        raise RuntimeError(
            "No reservoir polygon could be extracted."
        )

    if (
        WORKING_CRS is None
        or str(WORKING_CRS).lower() == "auto"
    ):
        working_crs = (
            gdf.estimate_utm_crs()
        )

        if working_crs is None:
            raise RuntimeError(
                "Could not determine a suitable projected CRS "
                "for reservoir geometry calculations."
            )

    else:
        working_crs = WORKING_CRS

    gdf = gdf.to_crs(
        working_crs
    )

    dam = (
        gpd.GeoDataFrame(
            geometry=gpd.points_from_xy(
                [lon],
                [lat],
            ),
            crs="EPSG:4326",
        )
        .to_crs(
            working_crs
        )
        .geometry.iloc[0]
    )

    gdf["area_m2"] = (
        gdf.geometry.area
    )

    containing = gdf[
        gdf.geometry.contains(
            dam
        )
    ]

    if not containing.empty:
        selected = (
            containing
            .sort_values(
                "area_m2",
                ascending=False,
            )
            .head(1)
            .copy()
        )

        selected[
            "selection_method"
        ] = "DAM_INSIDE_POLYGON"

        print(
            "Selected containing polygon "
            f"({selected.area_m2.iloc[0]:,.0f} m²)"
        )

        return selected.to_crs(
            "EPSG:4326"
        )

    gdf["distance_m"] = (
        gdf.geometry.distance(
            dam
        )
    )

    selected = (
        gdf
        .sort_values(
            "distance_m"
        )
        .head(1)
        .copy()
    )

    selected[
        "selection_method"
    ] = "NEAREST_POLYGON"

    print(
        "Nearest polygon selected "
        f"(distance = {selected.distance_m.iloc[0]:.1f} m, "
        f"area = {selected.area_m2.iloc[0]:,.0f} m²)"
    )

    return selected.to_crs(
        "EPSG:4326"
    )