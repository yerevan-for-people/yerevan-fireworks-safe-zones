"""Grid generation and safe point filtering."""

import logging
from typing import Optional

import geopandas as gpd
import numpy as np
from shapely.geometry import Point, MultiPolygon, Polygon

logger = logging.getLogger(__name__)


def generate_grid_points(
    boundary: Polygon,
    grid_step_m: float,
    crs: str
) -> gpd.GeoDataFrame:
    """
    Generate a regular grid of points within a boundary polygon.

    Args:
        boundary: Boundary polygon in projected CRS (meters)
        grid_step_m: Grid spacing in meters
        crs: CRS of the boundary

    Returns:
        GeoDataFrame with grid points
    """
    logger.info(f"Generating grid points with {grid_step_m}m spacing...")

    minx, miny, maxx, maxy = boundary.bounds

    x_coords = np.arange(minx, maxx, grid_step_m)
    y_coords = np.arange(miny, maxy, grid_step_m)

    logger.info(f"Grid dimensions: {len(x_coords)} x {len(y_coords)} = {len(x_coords) * len(y_coords)} potential points")

    points = []
    for x in x_coords:
        for y in y_coords:
            point = Point(x, y)
            if boundary.contains(point):
                points.append(point)

    logger.info(f"Generated {len(points)} grid points inside boundary")

    if not points:
        logger.warning("No grid points generated inside boundary")
        return gpd.GeoDataFrame(geometry=[], crs=crs)

    grid_gdf = gpd.GeoDataFrame(geometry=points, crs=crs)

    return grid_gdf


def filter_safe_points(
    grid_points: gpd.GeoDataFrame,
    forbidden_zone: MultiPolygon
) -> gpd.GeoDataFrame:
    """
    Filter grid points to keep only those outside the forbidden zone.

    Args:
        grid_points: GeoDataFrame with candidate points
        forbidden_zone: MultiPolygon representing forbidden areas

    Returns:
        GeoDataFrame with safe points only
    """
    logger.info(f"Filtering {len(grid_points)} grid points...")

    if len(grid_points) == 0:
        logger.warning("No grid points to filter")
        return grid_points

    from tqdm import tqdm

    if len(grid_points) > 100000:
        logger.info("Checking points against forbidden zone (this may take a few minutes)...")

        # Chunk processing with progress bar for better performance
        chunk_size = 50000
        safe_indices = []

        with tqdm(total=len(grid_points), desc="Filtering points", unit="pts", ncols=100, colour='cyan') as pbar:
            for start_idx in range(0, len(grid_points), chunk_size):
                end_idx = min(start_idx + chunk_size, len(grid_points))
                chunk = grid_points.iloc[start_idx:end_idx]

                chunk_safe_mask = ~chunk.geometry.within(forbidden_zone)

                chunk_intersect_mask = chunk.geometry.intersects(forbidden_zone)
                chunk_safe_mask = chunk_safe_mask & ~chunk_intersect_mask

                safe_indices.extend(chunk[chunk_safe_mask].index.tolist())

                pbar.update(len(chunk))

        safe_points = grid_points.loc[safe_indices].copy()
    else:
        # For smaller datasets, process all at once (faster)
        safe_mask = ~grid_points.geometry.within(forbidden_zone)
        intersect_mask = grid_points.geometry.intersects(forbidden_zone)
        safe_mask = safe_mask & ~intersect_mask
        safe_points = grid_points[safe_mask].copy()

    logger.info(f"Found {len(safe_points)} safe points ({len(safe_points)/len(grid_points)*100:.1f}% of total)")

    return safe_points


def thin_points(
    points_gdf: gpd.GeoDataFrame,
    max_points: Optional[int] = None,
    method: str = 'uniform'
) -> gpd.GeoDataFrame:
    """
    Reduce number of points if needed for output size management.

    Args:
        points_gdf: GeoDataFrame with points
        max_points: Maximum number of points to keep (None = keep all)
        method: Thinning method ('uniform' or 'random')

    Returns:
        Thinned GeoDataFrame
    """
    if max_points is None or len(points_gdf) <= max_points:
        return points_gdf

    logger.info(f"Thinning {len(points_gdf)} points to {max_points} using {method} method...")

    if method == 'uniform':
        step = len(points_gdf) // max_points
        thinned = points_gdf.iloc[::step].copy()
    elif method == 'random':
        thinned = points_gdf.sample(n=max_points, random_state=42).copy()
    else:
        raise ValueError(f"Unknown thinning method: {method}")

    logger.info(f"Thinned to {len(thinned)} points")
    return thinned


def generate_safe_points(
    boundary_gdf: gpd.GeoDataFrame,
    forbidden_zone: MultiPolygon,
    grid_step_m: float,
    target_crs: str,
    max_output_points: Optional[int] = None
) -> gpd.GeoDataFrame:
    """
    Main pipeline to generate safe points for fireworks.

    Args:
        boundary_gdf: City boundary GeoDataFrame
        forbidden_zone: Forbidden zone MultiPolygon
        grid_step_m: Grid spacing in meters
        target_crs: Target CRS for calculations
        max_output_points: Maximum points in output (for CSV size management)

    Returns:
        GeoDataFrame with safe points in projected CRS
    """
    logger.info("Starting safe point generation pipeline...")

    from .geometry_utils import reproject_to_meters
    boundary_proj = reproject_to_meters(boundary_gdf, target_crs)

    boundary_polygon = boundary_proj.geometry.unary_union
    if isinstance(boundary_polygon, MultiPolygon):
        boundary_polygon = max(boundary_polygon.geoms, key=lambda p: p.area)

    grid_points = generate_grid_points(boundary_polygon, grid_step_m, target_crs)

    if len(grid_points) == 0:
        logger.error("No grid points generated")
        return grid_points

    safe_points = filter_safe_points(grid_points, forbidden_zone)

    if len(safe_points) == 0:
        logger.warning("No safe points found!")
        return safe_points

    if max_output_points is not None:
        safe_points = thin_points(safe_points, max_output_points, method='uniform')

    safe_points['x_utm'] = safe_points.geometry.x
    safe_points['y_utm'] = safe_points.geometry.y

    logger.info(f"Safe point generation complete: {len(safe_points)} points")
    return safe_points
