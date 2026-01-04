"""Generate safe zones (polygons) from safe points or free space."""

import logging
from typing import Optional

import geopandas as gpd
import numpy as np
from shapely.geometry import MultiPolygon, Polygon, GeometryCollection
from shapely.ops import unary_union

logger = logging.getLogger(__name__)


def create_zones_from_points(
    safe_points_gdf: gpd.GeoDataFrame,
    zone_radius_m: float,
    min_zone_area_m2: Optional[float] = None,
    dissolve: bool = True
) -> gpd.GeoDataFrame:
    """
    Create safe zones (polygons) from safe points.

    Args:
        safe_points_gdf: GeoDataFrame with safe points in projected CRS
        zone_radius_m: Radius of safety zone around each point in meters
        min_zone_area_m2: Minimum area for a zone to be kept (filters small zones)
        dissolve: Whether to merge overlapping/touching zones into larger zones

    Returns:
        GeoDataFrame with safe zone polygons
    """
    logger.info(f"Creating safe zones from {len(safe_points_gdf)} points...")
    logger.info(f"Zone radius: {zone_radius_m}m")

    if len(safe_points_gdf) == 0:
        logger.warning("No safe points provided")
        return gpd.GeoDataFrame(geometry=[], crs=safe_points_gdf.crs)

    logger.info(f"Buffering points with {zone_radius_m}m radius...")
    buffered_zones = safe_points_gdf.geometry.buffer(zone_radius_m)

    if dissolve:
        logger.info("Merging overlapping zones...")
        merged_geometry = unary_union(buffered_zones)

        if isinstance(merged_geometry, Polygon):
            zones = gpd.GeoDataFrame(
                geometry=[merged_geometry],
                crs=safe_points_gdf.crs
            )
        elif isinstance(merged_geometry, MultiPolygon):
            zones = gpd.GeoDataFrame(
                geometry=list(merged_geometry.geoms),
                crs=safe_points_gdf.crs
            )
        else:
            logger.warning(f"Unexpected geometry type: {type(merged_geometry)}")
            zones = gpd.GeoDataFrame(geometry=[], crs=safe_points_gdf.crs)
    else:
        zones = gpd.GeoDataFrame(
            geometry=buffered_zones,
            crs=safe_points_gdf.crs
        )

    logger.info(f"Created {len(zones)} zone(s)")

    if min_zone_area_m2 is not None and len(zones) > 0:
        logger.info(f"Filtering zones smaller than {min_zone_area_m2}m²...")
        zones['area_m2'] = zones.geometry.area
        zones = zones[zones['area_m2'] >= min_zone_area_m2].copy()
        logger.info(f"Kept {len(zones)} zone(s) after filtering")
    else:
        if len(zones) > 0:
            zones['area_m2'] = zones.geometry.area

    if len(zones) > 0:
        zones['zone_id'] = range(1, len(zones) + 1)

        total_area_km2 = zones['area_m2'].sum() / 1_000_000
        avg_area_m2 = zones['area_m2'].mean()

        logger.info(f"Zone statistics:")
        logger.info(f"  Total zones: {len(zones)}")
        logger.info(f"  Total safe area: {total_area_km2:.3f} km²")
        logger.info(f"  Average zone size: {avg_area_m2:.0f} m²")
        logger.info(f"  Largest zone: {zones['area_m2'].max():.0f} m²")
        logger.info(f"  Smallest zone: {zones['area_m2'].min():.0f} m²")

    return zones


def classify_zones_by_size(
    zones_gdf: gpd.GeoDataFrame
) -> gpd.GeoDataFrame:
    """
    Classify zones by size categories.

    Args:
        zones_gdf: GeoDataFrame with zones and area_m2 column

    Returns:
        GeoDataFrame with added 'size_class' column
    """
    if len(zones_gdf) == 0 or 'area_m2' not in zones_gdf.columns:
        return zones_gdf

    logger.info("Classifying zones by size...")

    def classify_size(area_m2):
        if area_m2 < 1000:
            return 'very_small'
        elif area_m2 < 5000:
            return 'small'
        elif area_m2 < 10000:
            return 'medium'
        elif area_m2 < 50000:
            return 'large'
        else:
            return 'very_large'

    zones_gdf['size_class'] = zones_gdf['area_m2'].apply(classify_size)

    size_counts = zones_gdf['size_class'].value_counts()
    logger.info("Zone size distribution:")
    for size_class, count in size_counts.items():
        logger.info(f"  {size_class}: {count} zones")

    return zones_gdf


def add_zone_metadata(
    zones_gdf: gpd.GeoDataFrame,
    boundary_gdf: Optional[gpd.GeoDataFrame] = None
) -> gpd.GeoDataFrame:
    """
    Add metadata to zones (perimeter, compactness, etc.).

    Args:
        zones_gdf: GeoDataFrame with zones
        boundary_gdf: City boundary for reference (currently unused, kept for compatibility)

    Returns:
        GeoDataFrame with added metadata columns
    """
    if len(zones_gdf) == 0:
        return zones_gdf

    logger.info("Adding zone metadata...")

    zones_gdf['perimeter_m'] = zones_gdf.geometry.length

    # Formula: 4π * area / perimeter² (circle = 1, elongated closer to 0)
    zones_gdf['compactness'] = (
        4 * np.pi * zones_gdf['area_m2'] / (zones_gdf['perimeter_m'] ** 2)
    )

    centroids = zones_gdf.geometry.centroid
    zones_gdf['centroid_x'] = centroids.x
    zones_gdf['centroid_y'] = centroids.y

    logger.info("Metadata added successfully")

    return zones_gdf


def generate_safe_zones(
    safe_points_gdf: gpd.GeoDataFrame,
    zone_radius_m: float = 15.0,
    min_zone_area_m2: Optional[float] = 2000.0,
    dissolve: bool = True,
    add_metadata: bool = True,
    classify_size: bool = True,
    boundary_gdf: Optional[gpd.GeoDataFrame] = None
) -> gpd.GeoDataFrame:
    """
    Main pipeline to generate safe zones from safe points.

    Args:
        safe_points_gdf: GeoDataFrame with safe points
        zone_radius_m: Radius of zone around each point
        min_zone_area_m2: Minimum zone area to keep
        dissolve: Whether to merge overlapping zones
        add_metadata: Whether to add metadata columns
        classify_size: Whether to classify zones by size
        boundary_gdf: Optional city boundary for metadata

    Returns:
        GeoDataFrame with safe zones
    """
    logger.info("=" * 60)
    logger.info("Safe Zones Generation Pipeline")
    logger.info("=" * 60)

    zones = create_zones_from_points(
        safe_points_gdf,
        zone_radius_m=zone_radius_m,
        min_zone_area_m2=min_zone_area_m2,
        dissolve=dissolve
    )

    if len(zones) == 0:
        logger.warning("No zones created")
        return zones

    if classify_size and 'area_m2' in zones.columns:
        zones = classify_zones_by_size(zones)

    if add_metadata and boundary_gdf is not None:
        zones = add_zone_metadata(zones, boundary_gdf)

    logger.info("=" * 60)
    logger.info(f"Safe zones generation complete: {len(zones)} zones")
    logger.info("=" * 60)

    return zones


def create_zones_from_free_space(
    boundary_gdf: gpd.GeoDataFrame,
    forbidden_zone: MultiPolygon,
    target_crs: str,
    min_zone_area_m2: Optional[float] = 2000.0,
    add_metadata: bool = True,
    classify_size: bool = True
) -> gpd.GeoDataFrame:
    """
    Create safe zones directly from free space (area NOT covered by obstacles).

    This method creates "true" polygons of open spaces rather than circles around points.

    Args:
        boundary_gdf: City boundary GeoDataFrame
        forbidden_zone: MultiPolygon of all forbidden areas
        target_crs: Target CRS for calculations
        min_zone_area_m2: Minimum zone area to keep
        add_metadata: Whether to add metadata columns
        classify_size: Whether to classify zones by size

    Returns:
        GeoDataFrame with safe zone polygons representing actual open spaces
    """
    logger.info("=" * 60)
    logger.info("Safe Zones from Free Space Pipeline")
    logger.info("=" * 60)

    from .geometry_utils import reproject_to_meters
    boundary_proj = reproject_to_meters(boundary_gdf, target_crs)

    boundary_polygon = boundary_proj.geometry.unary_union
    if isinstance(boundary_polygon, MultiPolygon):
        boundary_polygon = max(boundary_polygon.geoms, key=lambda p: p.area)

    logger.info(f"City boundary area: {boundary_polygon.area / 1_000_000:.2f} km²")
    logger.info(f"Forbidden zone has {len(forbidden_zone.geoms)} polygon(s)")

    logger.info("Calculating free space (boundary - forbidden zones)...")
    try:
        free_space = boundary_polygon.difference(forbidden_zone)
    except Exception as e:
        logger.error(f"Error calculating free space: {e}")
        logger.info("Trying with buffer(0) to fix geometry...")
        free_space = boundary_polygon.buffer(0).difference(forbidden_zone.buffer(0))

    logger.info("Extracting individual zones...")
    zones_list = []

    if isinstance(free_space, Polygon):
        zones_list = [free_space]
    elif isinstance(free_space, MultiPolygon):
        zones_list = list(free_space.geoms)
    elif isinstance(free_space, GeometryCollection):
        zones_list = [geom for geom in free_space.geoms
                     if isinstance(geom, (Polygon, MultiPolygon))]
        unpacked = []
        for geom in zones_list:
            if isinstance(geom, MultiPolygon):
                unpacked.extend(list(geom.geoms))
            else:
                unpacked.append(geom)
        zones_list = unpacked

    logger.info(f"Found {len(zones_list)} free space zones")

    if not zones_list:
        logger.warning("No free space zones found!")
        return gpd.GeoDataFrame(geometry=[], crs=target_crs)

    zones_gdf = gpd.GeoDataFrame(geometry=zones_list, crs=target_crs)

    zones_gdf['area_m2'] = zones_gdf.geometry.area

    if min_zone_area_m2 is not None:
        logger.info(f"Filtering zones smaller than {min_zone_area_m2}m²...")
        before_count = len(zones_gdf)
        zones_gdf = zones_gdf[zones_gdf['area_m2'] >= min_zone_area_m2].copy()
        logger.info(f"Kept {len(zones_gdf)} zones after filtering (removed {before_count - len(zones_gdf)})")

    if len(zones_gdf) == 0:
        logger.warning("No zones remain after filtering!")
        return zones_gdf

    zones_gdf['zone_id'] = range(1, len(zones_gdf) + 1)

    total_area_km2 = zones_gdf['area_m2'].sum() / 1_000_000
    avg_area_m2 = zones_gdf['area_m2'].mean()

    logger.info(f"Zone statistics:")
    logger.info(f"  Total zones: {len(zones_gdf)}")
    logger.info(f"  Total safe area: {total_area_km2:.3f} km²")
    logger.info(f"  Average zone size: {avg_area_m2:.0f} m²")
    logger.info(f"  Largest zone: {zones_gdf['area_m2'].max():.0f} m²")
    logger.info(f"  Smallest zone: {zones_gdf['area_m2'].min():.0f} m²")

    if classify_size:
        zones_gdf = classify_zones_by_size(zones_gdf)

    if add_metadata:
        zones_gdf = add_zone_metadata(zones_gdf, boundary_gdf)

    logger.info("=" * 60)
    logger.info(f"Free space zones generation complete: {len(zones_gdf)} zones")
    logger.info("=" * 60)

    return zones_gdf
