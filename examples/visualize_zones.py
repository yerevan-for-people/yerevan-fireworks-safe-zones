#!/usr/bin/env python3
"""
Example: Visualize safe zones for any city using matplotlib.

Requires: matplotlib
Install: pip install matplotlib

For interactive web visualization, export data and use QGIS or similar GIS software.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from src.osm_loader import get_city_boundary, load_all_obstacles
from src.geometry_utils import create_forbidden_zone_with_custom_buffers
from src.zones_generator import create_zones_from_free_space, add_zone_metadata
from src.config import get_buffer_distances, get_utm_crs_for_location, DEFAULT_MIN_ZONE_AREA_M2
from src.exporters import slugify_city_name


def main(city: str = "Yerevan, Armenia"):
    """
    Visualize safe zones with matplotlib.

    Args:
        city: City query string (e.g., "Prague, Czech Republic")
    """
    print(f"Loading data and generating zones for '{city}'...")

    boundary = get_city_boundary(city)
    target_crs = get_utm_crs_for_location(boundary)
    print(f"Using {target_crs} for visualization")

    obstacles = load_all_obstacles(boundary, include_sensitive=True, split_sensitive=True)

    buffer_distances = get_buffer_distances()
    forbidden_zone, target_crs = create_forbidden_zone_with_custom_buffers(obstacles, target_crs, buffer_distances)

    zones = create_zones_from_free_space(boundary, forbidden_zone, target_crs, DEFAULT_MIN_ZONE_AREA_M2)
    zones = add_zone_metadata(zones, boundary)

    print(f"Found {len(zones)} safe zones")

    boundary_utm = boundary.to_crs(target_crs)
    zones_utm = zones.to_crs(target_crs)

    buildings = obstacles.get('buildings', gpd.GeoDataFrame())
    if len(buildings) > 0:
        buildings_utm = buildings.to_crs(target_crs)
    else:
        buildings_utm = None

    print("Creating visualization...")
    fig, ax = plt.subplots(figsize=(16, 12))

    boundary_utm.boundary.plot(ax=ax, color='black', linewidth=2, label='City Boundary')

    if buildings_utm is not None and len(buildings_utm) > 0:
        sample_size = min(5000, len(buildings_utm))
        buildings_sample = buildings_utm.sample(sample_size)
        buildings_sample.plot(ax=ax, facecolor='lightgray', edgecolor='gray',
                             alpha=0.3, linewidth=0.5)

    size_colors = {
        'small': '#90EE90',
        'medium': '#00FF00',
        'large': '#00CC00',
        'very_large': '#008800'
    }

    for size_class, color in size_colors.items():
        subset = zones_utm[zones_utm['size_class'] == size_class]
        if len(subset) > 0:
            subset.plot(ax=ax, facecolor=color, edgecolor='darkgreen',
                       alpha=0.6, linewidth=0.5, label=f'{size_class} ({len(subset)})')

    ax.set_title(f'{city} - Fireworks Safe Zones\n' +
                 f'{len(zones)} zones covering {zones["area_m2"].sum()/1e6:.1f} km²',
                 fontsize=16, fontweight='bold')
    ax.set_xlabel('X (UTM meters)', fontsize=12)
    ax.set_ylabel('Y (UTM meters)', fontsize=12)

    handles = [
        Patch(facecolor='black', edgecolor='black', label='City Boundary'),
        Patch(facecolor='lightgray', alpha=0.3, label='Buildings (sample)'),
    ]
    for size_class, color in size_colors.items():
        subset = zones_utm[zones_utm['size_class'] == size_class]
        if len(subset) > 0:
            handles.append(Patch(facecolor=color, alpha=0.6, label=f'{size_class}: {len(subset)} zones'))

    ax.legend(handles=handles, loc='upper right', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.2)
    ax.set_aspect('equal')

    plt.tight_layout()

    city_slug = slugify_city_name(city)
    output_dir = Path(__file__).parent / "output" / city_slug
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "safe_zones_map.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\nSaved map to: {output_path}")

    print("\nStatistics by size class:")
    for size_class in ['small', 'medium', 'large', 'very_large']:
        subset = zones[zones['size_class'] == size_class]
        if len(subset) > 0:
            total_area = subset['area_m2'].sum() / 1e6
            print(f"  {size_class:12s}: {len(subset):4d} zones, {total_area:6.2f} km²")

    print("\nDisplaying map (close window to exit)...")
    plt.show()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Visualize safe zones for any city')
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
