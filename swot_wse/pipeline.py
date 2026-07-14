from swot_wse.cache.polygon_cache import (
    polygon_exists,
    load_polygon,
    save_polygon,
)

from swot_wse.geometry.reservoir_extractor import (
    extract_reservoir_polygon,
)


def get_wse(lat: float, lon: float):

    if polygon_exists(lat, lon):

        print("✓ Polygon found in cache.")

        polygon = load_polygon(lat, lon)

    else:

        print("Generating reservoir polygon from Pekel...")

        polygon = extract_reservoir_polygon(lat, lon)

        save_polygon(lat, lon, polygon)

        print("✓ Polygon saved to cache.")

    print()

    print(polygon)