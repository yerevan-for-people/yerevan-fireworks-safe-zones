"""Utilities for geometric transformations and spatial operations."""

import logging
from typing import Optional

import geopandas as gpd
from shapely.geometry import MultiPolygon, GeometryCollection, Polygon
from shapely.ops import unary_union
from tqdm import tqdm

from .config import get_buffer_distances

logger = logging.getLogger(__name__)


def reproject_to_meters(gdf: gpd.GeoDataFrame, target_crs: str) -> gpd.GeoDataFrame:
    """
    Reproject GeoDataFrame to a coordinate system using meters.

    Args:
        gdf: Input GeoDataFrame
        target_crs: Target CRS (e.g., "EPSG:32638" for UTM Zone 38N)

    Returns:
        Reprojected GeoDataFrame
    """
    if gdf.crs is None:
        logger.warning("Input GeoDataFrame has no CRS, assuming EPSG:4326")
        gdf = gdf.set_crs("EPSG:4326")

    if gdf.crs.to_string() != target_crs:
        logger.info(f"Reprojecting from {gdf.crs} to {target_crs}")
        return gdf.to_crs(target_crs)

    return gdf


def create_forbidden_zone_with_custom_buffers(
    obstacles_dict: dict[str, gpd.GeoDataFrame],
    target_crs: str,
    custom_buffers: Optional[dict[str, float]] = None
) -> tuple[MultiPolygon, str]:
    """
    Create forbidden zone with different buffer distances per obstacle type.

    Args:
        obstacles_dict: Dictionary of obstacle GeoDataFrames
        target_crs: Target CRS for buffering (e.g., "EPSG:32638" for UTM Zone 38N)
        custom_buffers: Optional custom buffer distances (uses defaults if None)

    Returns:
        Tuple of (forbidden zone MultiPolygon, CRS string)
    """
    if custom_buffers is None:
        custom_buffers = get_buffer_distances()

    logger.info("Creating forbidden zone with custom buffers...")
    logger.info("Buffer distances by type:")
    for obs_type, buffer in custom_buffers.items():
        if obs_type in obstacles_dict and len(obstacles_dict[obs_type]) > 0:
            logger.info(f"  {obs_type}: {buffer}m")

    all_buffered_geometries = []

    obstacle_items = [(t, gdf) for t, gdf in obstacles_dict.items() if len(gdf) > 0]

    with tqdm(obstacle_items, desc="Buffering obstacles", unit="type", ncols=100, colour='blue') as pbar:
        for obstacle_type, gdf in pbar:
            buffer_dist = custom_buffers.get(obstacle_type, 30.0)

            gdf_proj = reproject_to_meters(gdf, target_crs)

            pbar.set_description(f"Buffering {obstacle_type:15s} ({buffer_dist}m)")

            for geom in tqdm(gdf_proj.geometry,
                           desc=f"  {obstacle_type}",
                           leave=False,
                           ncols=100,
                           disable=len(gdf_proj) < 100):
                if geom is not None and not geom.is_empty:
                    try:
                        buffered = geom.buffer(buffer_dist)
                        all_buffered_geometries.append(buffered)
                    except Exception as e:
                        logger.warning(f"Failed to buffer {obstacle_type} geometry: {e}")
                        continue

    if not all_buffered_geometries:
        logger.warning("No buffered geometries, returning empty forbidden zone")
        return MultiPolygon(), target_crs

    logger.info(f"Created {len(all_buffered_geometries)} total buffered geometries")

    logger.info("Merging buffered geometries into forbidden zone...")
    forbidden_union = unary_union(all_buffered_geometries)

    if isinstance(forbidden_union, Polygon):
        forbidden_zone = MultiPolygon([forbidden_union])
    elif isinstance(forbidden_union, MultiPolygon):
        forbidden_zone = forbidden_union
    elif isinstance(forbidden_union, GeometryCollection):
        polygons = [geom for geom in forbidden_union.geoms
                   if isinstance(geom, (Polygon, MultiPolygon))]
        if polygons:
            forbidden_zone = MultiPolygon(polygons) if len(polygons) > 1 else MultiPolygon([polygons[0]])
        else:
            forbidden_zone = MultiPolygon()
    else:
        logger.warning(f"Unexpected geometry type: {type(forbidden_union)}")
        forbidden_zone = MultiPolygon()

    logger.info(f"Forbidden zone created with {len(forbidden_zone.geoms)} polygon(s)")
    return forbidden_zone, target_crs
