from shapely.geometry import Polygon, box


def _extract_granule_polygon(granule):
    """
    Build a Shapely geometry representing
    the PIXC granule footprint from NASA CMR metadata.
    """

    try:
        geometry = (
            granule["umm"]
            ["SpatialExtent"]
            ["HorizontalSpatialDomain"]
            ["Geometry"]
        )

    except (KeyError, TypeError):
        return None

    bounding_rectangles = (
        geometry.get(
            "BoundingRectangles"
        )
    )

    if bounding_rectangles:
        try:
            rectangle = (
                bounding_rectangles[0]
            )

            return box(
                float(
                    rectangle[
                        "WestBoundingCoordinate"
                    ]
                ),
                float(
                    rectangle[
                        "SouthBoundingCoordinate"
                    ]
                ),
                float(
                    rectangle[
                        "EastBoundingCoordinate"
                    ]
                ),
                float(
                    rectangle[
                        "NorthBoundingCoordinate"
                    ]
                ),
            )

        except (
            KeyError,
            TypeError,
            ValueError,
            IndexError,
        ):
            pass

    gpolygons = geometry.get(
        "GPolygons"
    )

    if not gpolygons:
        return None

    if isinstance(
        gpolygons,
        list,
    ):
        if not gpolygons:
            return None

        gpolygon = gpolygons[0]

    else:
        gpolygon = gpolygons

    try:
        points = (
            gpolygon["Boundary"]["Points"]
        )

        coordinates = [
            (
                float(
                    point["Longitude"]
                ),
                float(
                    point["Latitude"]
                ),
            )
            for point in points
        ]

    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        return None

    if len(coordinates) < 3:
        return None

    polygon = Polygon(
        coordinates
    )

    if not polygon.is_valid:
        polygon = polygon.buffer(0)

    if polygon.is_empty:
        return None

    return polygon


def discover_pixc_granules(
    granules,
    reservoir_polygon,
):
    """
    Verify which candidate PIXC granules
    intersect the reservoir footprint using
    NASA CMR metadata.
    """

    if (
        reservoir_polygon is None
        or reservoir_polygon.empty
    ):
        raise ValueError(
            "A valid reservoir polygon is "
            "required for PIXC discovery."
        )

    if reservoir_polygon.crs is None:
        raise RuntimeError(
            "Reservoir polygon has no CRS."
        )

    reservoir_wgs84 = (
        reservoir_polygon.to_crs(
            "EPSG:4326"
        )
    )

    reservoir = (
        reservoir_wgs84
        .geometry
        .iloc[0]
    )

    verified = []

    for granule in granules:
        footprint = (
            _extract_granule_polygon(
                granule
            )
        )

        if footprint is None:
            continue

        if not footprint.intersects(
            reservoir
        ):
            continue

        verified.append(
            {
                "granule": granule,
                "footprint": footprint,
            }
        )

    print(
        f"Verified PIXC granules : "
        f"{len(verified)}"
    )

    return verified