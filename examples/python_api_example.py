#!/usr/bin/env python3
"""
Example: Using the Fireworks Safe Zones API programmatically for any city.

This example demonstrates how to:
1. Load OSM data with differentiated categories (39 types)
2. Auto-detect appropriate UTM zone for the city
3. Create forbidden zones with custom buffers (20-300m)
4. Generate safe zones from free space
5. Export results to GeoJSON and CSV

For CLI usage, see: python -m src.main --help
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.osm_loader import get_city_boundary, load_all_obstacles
from src.geometry_utils import create_forbidden_zone_with_custom_buffers
from src.zones_generator import create_zones_from_free_space, add_zone_metadata
from src.exporters import export_zones_to_geojson, export_zones_to_csv
from src.config import get_buffer_distances, get_utm_crs_for_location, DEFAULT_MIN_ZONE_AREA_M2


def main(city: str = "Yerevan, Armenia"):
    """
    Generate safe zones for any city using the Python API.

    Args:
        city: City query string (e.g., "Prague, Czech Republic", "Tbilisi, Georgia")
    """
    print("=" * 70)
    print("Fireworks Safe Zones - Python API Example")
    print("Using differentiated buffers (20-300m) for 39 obstacle categories")
    print("=" * 70)
    print(f"City: {city}")

    print(f"\n[1/6] Loading boundary for '{city}'...")
    boundary = get_city_boundary(city)
    boundary_area_km2 = boundary.geometry.area.sum() / 1_000_000
    print(f"  Loaded boundary: {boundary_area_km2:.2f} km²")
    print(f"  CRS: {boundary.crs}")

    print("\n[2/6] Auto-detecting UTM zone...")
    target_crs = get_utm_crs_for_location(boundary)
    print(f"  Using {target_crs} for calculations")

    print("\n[3/6] Loading obstacles from OpenStreetMap...")
    print("  Categories: 39 types with differentiated buffers")
    obstacles = load_all_obstacles(
        boundary,
        include_sensitive=True,
        split_sensitive=True
    )

    total_features = sum(len(gdf) for gdf in obstacles.values())
    non_empty = sum(1 for gdf in obstacles.values() if len(gdf) > 0)
    print(f"  Total features: {total_features:,}")
    print(f"  Active categories: {non_empty}/{len(obstacles)}")

    top_categories = sorted(
        [(name, len(gdf)) for name, gdf in obstacles.items()],
        key=lambda x: x[1],
        reverse=True
    )[:5]
    print("  Top 5 categories:")
    for name, count in top_categories:
        print(f"    - {name}: {count:,} features")

    print("\n[4/6] Creating forbidden zone with custom buffers...")
    buffer_distances = get_buffer_distances()
    print(f"  Using {len(buffer_distances)} buffer distances: 20-300m")

    forbidden_zone, target_crs = create_forbidden_zone_with_custom_buffers(
        obstacles,
        target_crs,
        custom_buffers=buffer_distances
    )

    print("  Forbidden zone created")

    print(f"\n[5/6] Generating safe zones (min area: {DEFAULT_MIN_ZONE_AREA_M2} m²)...")
    zones = create_zones_from_free_space(
        boundary,
        forbidden_zone,
        target_crs,
        min_zone_area_m2=DEFAULT_MIN_ZONE_AREA_M2
    )

    zones = add_zone_metadata(zones, boundary)

    total_zones = len(zones)
    safe_area_km2 = zones['area_m2'].sum() / 1_000_000
    coverage_pct = (safe_area_km2 / boundary_area_km2) * 100

    print(f"  Safe zones found: {total_zones}")
    print(f"  Total safe area: {safe_area_km2:.2f} km² ({coverage_pct:.1f}%)")

    size_counts = zones['size_class'].value_counts()
    print("\n  Size distribution:")
    for size_class in ['very_large', 'large', 'medium', 'small']:
        if size_class in size_counts.index:
            count = size_counts[size_class]
            pct = (count / total_zones) * 100
            print(f"    - {size_class}: {count} zones ({pct:.1f}%)")

    print("\n[6/6] Exporting results...")
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    geojson_path = export_zones_to_geojson(zones, output_dir, city_name=city, target_crs=target_crs)
    csv_path = export_zones_to_csv(zones, output_dir, city_name=city)

    print(f"  GeoJSON: {geojson_path}")
    print(f"  CSV: {csv_path}")

    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)

    print("\nTerritory:")
    print(f"  City area:        {boundary_area_km2:.2f} km²")
    print(f"  Safe zones:       {safe_area_km2:.2f} km² ({coverage_pct:.1f}%)")
    print(f"  Excluded:         {boundary_area_km2 - safe_area_km2:.2f} km² ({100-coverage_pct:.1f}%)")

    print("\nObstacles:")
    print(f"  Total features:   {total_features:,}")
    print(f"  Categories:       {len(obstacles)} (39 types)")

    print("\nSafe zones:")
    print(f"  Total zones:      {total_zones}")
    print(f"  Min area:         {zones['area_m2'].min():,.0f} m²")
    print(f"  Max area:         {zones['area_m2'].max():,.0f} m²")
    print(f"  Average area:     {zones['area_m2'].mean():,.0f} m²")

    print("\n" + "=" * 70)

    print("\nTop 5 largest zones:")
    top_zones = zones.nlargest(5, 'area_m2')
    for idx, row in top_zones.iterrows():
        area_ha = row['area_m2'] / 10_000
        print(f"  Zone #{row['zone_id']}: {area_ha:.2f} hectares ({row['size_class']})")

    print("\nRandom sample of 3 zone centroids (lat/lon):")
    sample = zones.sample(min(3, len(zones)))
    zones_wgs84 = sample.to_crs("EPSG:4326")
    for idx, row in zones_wgs84.iterrows():
        centroid = row.geometry.centroid
        print(f"  Zone #{row['zone_id']}: {centroid.y:.6f}°N, {centroid.x:.6f}°E")

    print("\n" + "=" * 70)
    print("Done! Check examples/output/ for exported files.")
    print("=" * 70)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate safe zones for any city')
    parser.add_argument('--city', type=str, default='Yerevan, Armenia',
                       help='City to analyze (e.g., "Prague, Czech Republic")')
    args = parser.parse_args()

    try:
        main(city=args.city)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
