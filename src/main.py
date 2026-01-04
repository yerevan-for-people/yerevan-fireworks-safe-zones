"""Main CLI script for finding safe firework zones in any city."""

import argparse
import logging
from pathlib import Path
import sys

from .osm_loader import get_city_boundary, load_all_obstacles
from .config import get_utm_crs_for_location
from .grid_generator import generate_safe_points
from .zones_generator import generate_safe_zones, create_zones_from_free_space
from .exporters import (export_all, save_obstacles_for_visualization,
                        export_zones_to_geojson, export_zones_to_csv,
                        export_zones_to_kml, export_zones_to_kmz)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the application."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Find safe zones for fireworks in any city using OpenStreetMap data',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        '--city',
        type=str,
        default='Yerevan, Armenia',
        help='City to analyze (geocoding query, e.g., "Prague, Czech Republic")'
    )

    parser.add_argument(
        '--buffer-radius',
        type=float,
        default=35.0,
        help='Buffer radius around obstacles in meters (deprecated, uses category-specific buffers)'
    )

    parser.add_argument(
        '--grid-step',
        type=float,
        default=10.0,
        help='Grid spacing in meters'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='data',
        help='Output directory for results'
    )

    parser.add_argument(
        '--max-points',
        type=int,
        default=None,
        help='Maximum number of points in output (for thinning large datasets)'
    )

    parser.add_argument(
        '--save-obstacles',
        action='store_true',
        help='Save obstacle layers for visualization'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--generate-zones',
        action='store_true',
        help='Generate safe zones (polygons) instead of points'
    )

    parser.add_argument(
        '--zone-radius',
        type=float,
        default=15.0,
        help='Radius of safe zones around points in meters (only with --generate-zones)'
    )

    parser.add_argument(
        '--min-zone-area',
        type=float,
        default=2000.0,
        help='Minimum zone area in m² to keep (only with --generate-zones)'
    )

    parser.add_argument(
        '--zones-method',
        type=str,
        choices=['points', 'freespace'],
        default='freespace',
        help='Zone generation method: points (circles around points) or freespace (actual open areas)'
    )

    parser.add_argument(
        '--include-sensitive',
        action='store_true',
        default=True,
        help='Include sensitive areas (cemeteries, hospitals, schools, water) as obstacles'
    )

    return parser.parse_args()


def main() -> int:
    """Main execution function."""
    args = parse_args()
    setup_logging(args.verbose)

    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("Fireworks Safe Zones Finder")
    logger.info("=" * 60)
    logger.info(f"Configuration:")
    logger.info(f"  City: {args.city}")
    logger.info(f"  Grid step: {args.grid_step}m")
    logger.info(f"  Output directory: {args.output_dir}")
    logger.info(f"  Max points: {args.max_points or 'unlimited'}")
    logger.info("=" * 60)

    try:
        logger.info(f"\n[1/5] Loading administrative boundary for '{args.city}'...")
        boundary_gdf = get_city_boundary(args.city)

        logger.info("Detecting appropriate UTM zone for location...")
        target_crs = get_utm_crs_for_location(boundary_gdf)
        logger.info(f"Using {target_crs} for metric calculations")

        logger.info("\n[2/5] Loading obstacles from OpenStreetMap...")
        obstacles = load_all_obstacles(
            boundary_gdf,
            include_sensitive=args.include_sensitive,
            split_sensitive=True
        )

        logger.info("\n[3/5] Creating forbidden zone with category-specific buffers...")
        from .geometry_utils import create_forbidden_zone_with_custom_buffers
        forbidden_zone, target_crs = create_forbidden_zone_with_custom_buffers(
            obstacles,
            target_crs,
            custom_buffers=None
        )

        logger.info("\n[4/5] Generating safe point candidates...")
        safe_points = generate_safe_points(
            boundary_gdf=boundary_gdf,
            forbidden_zone=forbidden_zone,
            grid_step_m=args.grid_step,
            target_crs=target_crs,
            max_output_points=args.max_points
        )

        if len(safe_points) == 0:
            logger.error("No safe points found! Try increasing grid step or decreasing buffer radius.")
            return 1

        if args.generate_zones:
            if args.zones_method == 'freespace':
                logger.info("\n[4.5/5] Generating safe zones from free space...")
                safe_zones = create_zones_from_free_space(
                    boundary_gdf=boundary_gdf,
                    forbidden_zone=forbidden_zone,
                    target_crs=target_crs,
                    min_zone_area_m2=args.min_zone_area,
                    add_metadata=True,
                    classify_size=True
                )
            else:
                logger.info("\n[4.5/5] Generating safe zones from points...")
                safe_zones = generate_safe_zones(
                    safe_points_gdf=safe_points,
                    zone_radius_m=args.zone_radius,
                    min_zone_area_m2=args.min_zone_area,
                    dissolve=True,
                    add_metadata=True,
                    classify_size=True,
                    boundary_gdf=boundary_gdf
                )

            if len(safe_zones) == 0:
                logger.warning("No safe zones generated!")
            else:
                logger.info("\n[5/5] Exporting safe zones...")
                output_dir = Path(args.output_dir)

                zones_path = export_zones_to_geojson(safe_zones, output_dir, city_name=args.city, target_crs=target_crs)
                csv_path = export_zones_to_csv(safe_zones, output_dir, city_name=args.city)
                kml_path = export_zones_to_kml(safe_zones, output_dir, city_name=args.city)
                kmz_path = export_zones_to_kmz(safe_zones, output_dir, city_name=args.city)
                output_paths = export_all(safe_points, output_dir, basename='safe_points', city_name=args.city)

                logger.info("\nResults:")
                logger.info(f"  Total safe zones found: {len(safe_zones)}")
                logger.info(f"  Total safe area: {safe_zones['area_m2'].sum() / 1_000_000:.3f} km²")
                logger.info(f"  Zones GeoJSON: {zones_path}")
                logger.info(f"  Zones CSV: {csv_path}")
                logger.info(f"  Zones KML: {kml_path}")
                logger.info(f"  Zones KMZ: {kmz_path} (recommended for mobile)")
                logger.info(f"  Points GeoJSON: {output_paths['geojson']}")
                logger.info(f"  Points CSV: {output_paths['csv']}")
        else:
            logger.info("\n[5/5] Exporting results...")
            output_dir = Path(args.output_dir)
            output_paths = export_all(safe_points, output_dir, city_name=args.city)

            logger.info("\nResults:")
            logger.info(f"  Total safe points found: {len(safe_points)}")
            logger.info(f"  GeoJSON: {output_paths['geojson']}")
            logger.info(f"  CSV: {output_paths['csv']}")

        if args.save_obstacles:
            logger.info("\nSaving obstacle data for visualization...")
            save_obstacles_for_visualization(obstacles, boundary_gdf, output_dir)

        logger.info("\n" + "=" * 60)
        logger.info("SUCCESS: Processing complete!")
        logger.info("=" * 60)

        return 0

    except KeyboardInterrupt:
        logger.error("\nProcess interrupted by user")
        return 130

    except Exception as e:
        logger.error(f"\nFATAL ERROR: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
