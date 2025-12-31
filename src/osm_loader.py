"""Module for loading OpenStreetMap data for any city."""

import logging
import time
from typing import Optional

import geopandas as gpd
import osmnx as ox
import pandas as pd
from shapely.geometry import Polygon, MultiPolygon
from tqdm import tqdm

from .config import (
    get_category_configs,
    get_all_osm_tags,
    OSM_MAX_RETRIES,
    OSM_RETRY_DELAY_S,
    WGS84_EPSG,
)

logger = logging.getLogger(__name__)


def get_city_boundary(
    city_query: str,
    max_retries: int = OSM_MAX_RETRIES,
    retry_delay: int = OSM_RETRY_DELAY_S
) -> gpd.GeoDataFrame:
    """
    Load administrative boundary of any city from OpenStreetMap.

    Args:
        city_query: Geocoding query string (e.g., "Yerevan, Armenia", "Prague, Czech Republic")
        max_retries: Maximum number of retry attempts for network requests
        retry_delay: Delay in seconds between retries

    Returns:
        GeoDataFrame containing the city's administrative boundary in WGS84

    Raises:
        Exception: If unable to load boundary after all retries

    Examples:
        >>> boundary = get_city_boundary("Yerevan, Armenia")
        >>> boundary = get_city_boundary("Tbilisi, Georgia")
        >>> boundary = get_city_boundary("Prague, Czech Republic")
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Loading boundary for '{city_query}'...")

            boundary = ox.geocode_to_gdf(city_query)

            logger.info(f"Successfully loaded boundary for '{city_query}' (CRS: {boundary.crs})")
            return boundary

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All retry attempts failed")
                raise Exception(f"Failed to load boundary for '{city_query}' after {max_retries} attempts") from e


def load_buildings(
    boundary_gdf: gpd.GeoDataFrame,
    max_retries: int = OSM_MAX_RETRIES,
    retry_delay: int = OSM_RETRY_DELAY_S
) -> gpd.GeoDataFrame:
    """
    Load all buildings within the given boundary from OSM.

    Args:
        boundary_gdf: GeoDataFrame containing the boundary polygon
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries

    Returns:
        GeoDataFrame containing building geometries
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Loading buildings...")

            polygon = boundary_gdf.geometry.unary_union

            print("Downloading buildings from OSM (may take 30-60 seconds)...", flush=True)
            buildings = ox.features_from_polygon(
                polygon,
                tags={'building': True}
            )

            buildings = buildings[buildings.geometry.type.isin(['Polygon', 'MultiPolygon'])]

            logger.info(f"Loaded {len(buildings)} buildings")
            return buildings

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All retry attempts failed for buildings")
                logger.warning("Returning empty buildings dataset")
                return gpd.GeoDataFrame(geometry=[], crs=boundary_gdf.crs)


def load_roads(
    boundary_gdf: gpd.GeoDataFrame,
    max_retries: int = OSM_MAX_RETRIES,
    retry_delay: int = OSM_RETRY_DELAY_S
) -> gpd.GeoDataFrame:
    """
    Load major roads within the given boundary from OSM.

    Args:
        boundary_gdf: GeoDataFrame containing the boundary polygon
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries

    Returns:
        GeoDataFrame containing road geometries
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Loading roads...")

            polygon = boundary_gdf.geometry.unary_union

            roads = ox.features_from_polygon(
                polygon,
                tags={
                    'highway': [
                        'motorway', 'trunk', 'primary', 'secondary',
                        'tertiary', 'motorway_link', 'trunk_link',
                        'primary_link', 'secondary_link', 'tertiary_link'
                    ]
                }
            )

            logger.info(f"Loaded {len(roads)} road segments")
            return roads

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All retry attempts failed for roads")
                logger.warning("Returning empty roads dataset")
                return gpd.GeoDataFrame(geometry=[], crs=boundary_gdf.crs)


def load_parking_areas(
    boundary_gdf: gpd.GeoDataFrame,
    max_retries: int = OSM_MAX_RETRIES,
    retry_delay: int = OSM_RETRY_DELAY_S
) -> gpd.GeoDataFrame:
    """
    Load parking areas within the given boundary from OSM.

    Args:
        boundary_gdf: GeoDataFrame containing the boundary polygon
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries

    Returns:
        GeoDataFrame containing parking area geometries
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Loading parking areas...")

            polygon = boundary_gdf.geometry.unary_union

            parking = ox.features_from_polygon(
                polygon,
                tags={
                    'amenity': 'parking',
                    'landuse': 'parking'
                }
            )

            if len(parking) > 0:
                parking = parking[parking.geometry.type.isin(['Polygon', 'MultiPolygon'])]

            logger.info(f"Loaded {len(parking)} parking areas")
            return parking

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All retry attempts failed for parking areas")
                logger.warning("Returning empty parking dataset")
                return gpd.GeoDataFrame(geometry=[], crs=boundary_gdf.crs)


def load_railways(
    boundary_gdf: gpd.GeoDataFrame,
    max_retries: int = OSM_MAX_RETRIES,
    retry_delay: int = OSM_RETRY_DELAY_S
) -> gpd.GeoDataFrame:
    """
    Load railway infrastructure within the given boundary from OSM.

    Args:
        boundary_gdf: GeoDataFrame containing the boundary polygon
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries

    Returns:
        GeoDataFrame containing railway geometries
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Loading railway infrastructure...")

            polygon = boundary_gdf.geometry.unary_union

            railways = ox.features_from_polygon(
                polygon,
                tags={
                    'landuse': 'railway',
                    'railway': True
                }
            )

            if len(railways) > 0:
                # Keep Polygons (stations, yards) AND LineStrings (tracks)
                railways = railways[railways.geometry.type.isin(['Polygon', 'MultiPolygon', 'LineString', 'MultiLineString'])]

            logger.info(f"Loaded {len(railways)} railway features")
            return railways

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All retry attempts failed for railways")
                logger.warning("Returning empty railways dataset")
                return gpd.GeoDataFrame(geometry=[], crs=boundary_gdf.crs)


def load_industrial(
    boundary_gdf: gpd.GeoDataFrame,
    max_retries: int = OSM_MAX_RETRIES,
    retry_delay: int = OSM_RETRY_DELAY_S
) -> gpd.GeoDataFrame:
    """
    Load industrial zones within the given boundary from OSM.

    Args:
        boundary_gdf: GeoDataFrame containing the boundary polygon
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries

    Returns:
        GeoDataFrame containing industrial zone geometries
    """
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Loading industrial zones...")

            polygon = boundary_gdf.geometry.unary_union

            industrial = ox.features_from_polygon(
                polygon,
                tags={'landuse': 'industrial'}
            )

            if len(industrial) > 0:
                industrial = industrial[industrial.geometry.type.isin(['Polygon', 'MultiPolygon'])]

            logger.info(f"Loaded {len(industrial)} industrial zones")
            return industrial

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All retry attempts failed for industrial zones")
                logger.warning("Returning empty industrial dataset")
                return gpd.GeoDataFrame(geometry=[], crs=boundary_gdf.crs)


def load_sensitive_areas(
    boundary_gdf: gpd.GeoDataFrame,
    max_retries: int = OSM_MAX_RETRIES,
    retry_delay: int = OSM_RETRY_DELAY_S
) -> gpd.GeoDataFrame:
    """
    Load sensitive areas following global best practices and Yerevan-specific restrictions.

    All OSM tags and categories are defined in config.py for easy customization.

    Args:
        boundary_gdf: GeoDataFrame containing the boundary polygon
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries

    Returns:
        GeoDataFrame containing sensitive area geometries
    """
    osm_tags = get_all_osm_tags()

    # Exclude tags already loaded by dedicated loaders:
    # - building, highway (loaded by load_buildings, load_roads)
    # - landuse=parking, amenity=parking (loaded by load_parking_areas)
    # - landuse=industrial (loaded by load_industrial)
    # - landuse=railway, railway=* (loaded by load_railways)
    osm_tags_sensitive = {}
    for k, v in osm_tags.items():
        if k in ['building', 'highway', 'railway']:
            continue
        if k == 'landuse':
            # Exclude parking, industrial, railway from landuse
            if isinstance(v, list):
                filtered = [val for val in v if val not in ['parking', 'industrial', 'railway']]
                if filtered:
                    osm_tags_sensitive[k] = filtered
            elif v not in ['parking', 'industrial', 'railway']:
                osm_tags_sensitive[k] = v
        elif k == 'amenity':
            # Exclude parking from amenity
            if isinstance(v, list):
                filtered = [val for val in v if val != 'parking']
                if filtered:
                    osm_tags_sensitive[k] = filtered
            elif v != 'parking':
                osm_tags_sensitive[k] = v
        else:
            osm_tags_sensitive[k] = v

    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}: Loading sensitive areas...")
            logger.info(f"Loading {len(osm_tags_sensitive)} OSM tag types from configuration")

            polygon = boundary_gdf.geometry.unary_union

            print("Downloading OSM data (this may take 1-2 minutes)...", flush=True)
            sensitive = ox.features_from_polygon(polygon, tags=osm_tags_sensitive)

            if len(sensitive) > 0:
                # Keep Polygons AND LineStrings (for waterways, power lines, etc.)
                sensitive = sensitive[sensitive.geometry.type.isin(['Polygon', 'MultiPolygon', 'LineString', 'MultiLineString'])]

            logger.info(f"Loaded {len(sensitive)} sensitive areas")
            return sensitive

        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("All retry attempts failed for sensitive areas")
                logger.warning("Returning empty sensitive areas dataset")
                return gpd.GeoDataFrame(geometry=[], crs=boundary_gdf.crs)


def split_sensitive_by_category(
    sensitive_gdf: gpd.GeoDataFrame,
    exclude_categories: Optional[list[str]] = None
) -> dict[str, gpd.GeoDataFrame]:
    """
    Split sensitive areas into specific categories for differentiated buffering.

    This function ensures COMPLETE coverage of all loaded OSM tags.
    Every tag loaded in load_sensitive_areas() MUST be categorized here.

    All category definitions come from config.py for consistency.

    Args:
        sensitive_gdf: GeoDataFrame with all sensitive areas
        exclude_categories: List of category names to exclude (categories loaded separately)

    Returns:
        Dictionary with categorized sensitive areas

    Raises:
        Warning: If any loaded features are not assigned to a category
    """
    category_configs = get_category_configs()

    # Exclude categories that are loaded separately to avoid overwriting them
    if exclude_categories is None:
        exclude_categories = []

    sensitive_categories = [
        name for name in category_configs.keys()
        if name not in exclude_categories
    ]

    if len(sensitive_gdf) == 0:
        empty = gpd.GeoDataFrame(geometry=[], crs=sensitive_gdf.crs)
        return {name: empty for name in sensitive_categories}

    logger.info("Splitting sensitive areas by category using config definitions...")

    def make_mask(tag_key: str, tag_value) -> pd.Series:
        """Create boolean mask for features matching a tag condition."""
        if tag_key not in sensitive_gdf.columns:
            return pd.Series([False] * len(sensitive_gdf), index=sensitive_gdf.index)

        if tag_value == '*':
            return sensitive_gdf[tag_key].notna()
        elif tag_value is True:
            return sensitive_gdf[tag_key].notna()
        elif isinstance(tag_value, list):
            return sensitive_gdf[tag_key].isin(tag_value)
        else:
            return sensitive_gdf[tag_key] == tag_value

    categories: dict[str, gpd.GeoDataFrame] = {}

    for category_name in sensitive_categories:
        config = category_configs[category_name]

        category_mask = pd.Series([False] * len(sensitive_gdf), index=sensitive_gdf.index)

        for tag_key, tag_value in config['tags']:
            tag_mask = make_mask(tag_key, tag_value)
            category_mask = category_mask | tag_mask

        categories[category_name] = sensitive_gdf[category_mask].copy()

    all_categorized_indices = set()
    for category_gdf in categories.values():
        if len(category_gdf) > 0:
            all_categorized_indices.update(category_gdf.index)

    all_categorized_mask = sensitive_gdf.index.isin(all_categorized_indices)

    uncategorized = sensitive_gdf[~all_categorized_mask]
    if len(uncategorized) > 0:
        logger.warning(f"WARNING: Found {len(uncategorized)} uncategorized features!")
        logger.warning("These features were loaded but not assigned to any category:")

        tag_columns = ['amenity', 'landuse', 'leisure', 'tourism', 'natural', 'waterway',
                      'historic', 'power', 'aeroway', 'railway', 'man_made', 'office', 'boundary']

        for idx, row in uncategorized.head(10).iterrows():
            tags = []
            for col in tag_columns:
                if col in row and pd.notna(row[col]):
                    tags.append(f"{col}={row[col]}")
            logger.warning(f"  - {', '.join(tags) if tags else 'unknown tags'}")

        if len(uncategorized) > 10:
            logger.warning(f"  ... and {len(uncategorized) - 10} more")

    total_categorized = sum(len(gdf) for gdf in categories.values())
    logger.info(f"Categorization complete: {total_categorized} features across {len([c for c in categories.values() if len(c) > 0])} categories")

    for category, gdf in categories.items():
        if len(gdf) > 0:
            logger.info(f"  {category}: {len(gdf)} features")

    return categories


def load_all_obstacles(
    boundary_gdf: gpd.GeoDataFrame,
    max_retries: int = OSM_MAX_RETRIES,
    retry_delay: int = OSM_RETRY_DELAY_S,
    include_sensitive: bool = True,
    split_sensitive: bool = True
) -> dict[str, gpd.GeoDataFrame]:
    """
    Load all obstacle types (buildings, roads, parking, railways, industrial, sensitive areas).

    Args:
        boundary_gdf: GeoDataFrame containing the boundary polygon
        max_retries: Maximum number of retry attempts
        retry_delay: Delay in seconds between retries
        include_sensitive: Whether to include sensitive areas (cemeteries, hospitals, etc.)
        split_sensitive: Whether to split sensitive areas by category for custom buffers

    Returns:
        Dictionary with obstacle types as keys
    """
    logger.info("Loading all obstacle data from OpenStreetMap...")

    # Define dedicated loaders (these categories are loaded separately, not from sensitive areas)
    dedicated_loaders = [
        ('buildings', lambda: load_buildings(boundary_gdf, max_retries, retry_delay)),
        ('roads', lambda: load_roads(boundary_gdf, max_retries, retry_delay)),
        ('parking', lambda: load_parking_areas(boundary_gdf, max_retries, retry_delay)),
        ('railways', lambda: load_railways(boundary_gdf, max_retries, retry_delay)),
        ('industrial', lambda: load_industrial(boundary_gdf, max_retries, retry_delay)),
    ]

    tasks = dedicated_loaders.copy()

    if include_sensitive:
        tasks.append(('sensitive', lambda: load_sensitive_areas(boundary_gdf, max_retries, retry_delay)))

    obstacles = {}

    with tqdm(tasks, desc="Loading OSM data", unit="layer", ncols=100, colour='green') as pbar:
        for name, loader_func in pbar:
            pbar.set_description(f"Loading {name:12s}")
            obstacles[name] = loader_func()

    if include_sensitive and 'sensitive' in obstacles:
        sensitive_all = obstacles.pop('sensitive')

        if split_sensitive and len(sensitive_all) > 0:
            logger.info("Splitting sensitive areas into categories...")
            # Pass list of dedicated categories to avoid overwriting them
            dedicated_categories = [name for name, _ in dedicated_loaders]
            sensitive_split = split_sensitive_by_category(sensitive_all, exclude_categories=dedicated_categories)
            obstacles.update(sensitive_split)
        else:
            obstacles['sensitive'] = sensitive_all

    total_features = sum(len(gdf) for gdf in obstacles.values())
    logger.info(f"Loaded total of {total_features} obstacle features")

    return obstacles
