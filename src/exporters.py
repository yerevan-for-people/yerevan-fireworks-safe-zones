"""Export safe points and zones to various formats (GeoJSON, CSV, KML, KMZ)."""

import json
import logging
import re
import zipfile
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import geopandas as gpd
import pandas as pd

logger = logging.getLogger(__name__)


def slugify_city_name(city_name: str) -> str:
    """
    Convert city name to filesystem-safe slug.

    Examples:
        "Prague, Czech Republic "prague-czech-republic"
        "Yerevan, Armenia" -> "yerevan-armenia"
        "Kyiv, Ukraine" -> "kyiv-ukraine"

    Args:
        city_name: City name (e.g., "Prague, Czech Republic")

    Returns:
        Slugified city name safe for filesystem
    """
    slug = city_name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = slug.strip('-')

    return slug


def get_geojson_metadata(city_name: str = "Unknown City", processing_crs: str = "Auto-detected UTM") -> dict:
    """
    Generate GeoJSON metadata with city-specific information.

    Args:
        city_name: Name of the city (e.g., "Yerevan, Armenia")
        processing_crs: CRS used for processing (e.g., "EPSG:32638")

    Returns:
        Dictionary with metadata fields
    """
    return {
        "name": f"{city_name} - Fireworks Safe Zones",
        "description": f"Geospatial analysis identifying safe zones for fireworks in {city_name} using OpenStreetMap data and international safety standards",
        "author": "Alex Kraiz",
        "contact": "https://github.com/yerevan-for-people/yerevan-fireworks-safe-zones",
        "license": "Code: MIT License | Data: OpenStreetMap (ODbL)",
        "methodology": "39 obstacle categories with differentiated safety buffers (20-300m) based on international standards (NFPA 1123, Philippines EO 047/2025, Czech Republic Pyrotechnic Articles Act)",
        "data_source": "OpenStreetMap contributors",
        "coordinate_system": "WGS84 (EPSG:4326)",
        "processing_crs": processing_crs,
        "city": city_name,
    }


def export_geojson(
    safe_points_gdf: gpd.GeoDataFrame,
    output_path: Path
) -> None:
    """
    Export safe points to GeoJSON format.

    Args:
        safe_points_gdf: GeoDataFrame with safe points (in projected CRS)
        output_path: Path to output GeoJSON file
    """
    logger.info(f"Exporting {len(safe_points_gdf)} points to GeoJSON...")

    if safe_points_gdf.crs.to_string() != "EPSG:4326":
        points_wgs84 = safe_points_gdf.to_crs("EPSG:4326")
    else:
        points_wgs84 = safe_points_gdf

    output_path.parent.mkdir(parents=True, exist_ok=True)
    points_wgs84.to_file(output_path, driver='GeoJSON')

    logger.info(f"GeoJSON saved to {output_path}")


def export_csv(
    safe_points_gdf: gpd.GeoDataFrame,
    output_path: Path
) -> None:
    """
    Export safe points to CSV format with lat/lon and projected coordinates.

    Args:
        safe_points_gdf: GeoDataFrame with safe points (in projected CRS)
        output_path: Path to output CSV file
    """
    logger.info(f"Exporting {len(safe_points_gdf)} points to CSV...")

    if safe_points_gdf.crs.to_string() != "EPSG:4326":
        points_wgs84 = safe_points_gdf.to_crs("EPSG:4326")
    else:
        points_wgs84 = safe_points_gdf

    df = pd.DataFrame({
        'lon': points_wgs84.geometry.x,
        'lat': points_wgs84.geometry.y,
        'x_utm': safe_points_gdf.geometry.x,
        'y_utm': safe_points_gdf.geometry.y
    })

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, float_format='%.6f')

    logger.info(f"CSV saved to {output_path}")


def export_all(
    safe_points_gdf: gpd.GeoDataFrame,
    output_dir: Path,
    basename: str = 'safe_points',
    city_name: str = "Unknown City"
) -> dict[str, Path]:
    """
    Export safe points to all supported formats.

    Args:
        safe_points_gdf: GeoDataFrame with safe points
        output_dir: Directory for output files (city subdirectory will be created)
        basename: Base filename (without extension)
        city_name: Name of the city for creating subdirectory

    Returns:
        Dictionary with format names and output paths
    """
    logger.info(f"Exporting to multiple formats in {output_dir}...")

    city_slug = slugify_city_name(city_name)
    city_output_dir = output_dir / city_slug
    city_output_dir.mkdir(parents=True, exist_ok=True)

    output_paths = {}

    geojson_path = city_output_dir / f"{basename}.geojson"
    export_geojson(safe_points_gdf, geojson_path)
    output_paths['geojson'] = geojson_path

    csv_path = city_output_dir / f"{basename}.csv"
    export_csv(safe_points_gdf, csv_path)
    output_paths['csv'] = csv_path

    logger.info("Export complete")
    return output_paths


def save_obstacles_for_visualization(
    obstacles_dict: dict[str, gpd.GeoDataFrame],
    boundary_gdf: gpd.GeoDataFrame,
    output_dir: Path
) -> None:
    """
    Save obstacle data for visualization purposes.

    Args:
        obstacles_dict: Dictionary of obstacle GeoDataFrames
        boundary_gdf: City boundary GeoDataFrame
        output_dir: Directory for output files
    """
    logger.info("Saving obstacle data for visualization...")

    output_dir.mkdir(parents=True, exist_ok=True)

    boundary_wgs84 = boundary_gdf.to_crs("EPSG:4326")
    boundary_path = output_dir / "boundary.geojson"
    boundary_wgs84.to_file(boundary_path, driver='GeoJSON')
    logger.info(f"Boundary saved to {boundary_path}")

    for obstacle_type, gdf in obstacles_dict.items():
        if len(gdf) == 0:
            logger.info(f"Skipping empty {obstacle_type} dataset")
            continue

        gdf_wgs84 = gdf.to_crs("EPSG:4326")

        obstacle_path = output_dir / f"{obstacle_type}.geojson"
        gdf_wgs84.to_file(obstacle_path, driver='GeoJSON')
        logger.info(f"{obstacle_type.capitalize()} saved to {obstacle_path}")


def export_zones_to_geojson(
    zones_gdf: gpd.GeoDataFrame,
    output_dir: Path,
    filename: str = "safe_zones.geojson",
    city_name: str = "Unknown City",
    target_crs: str = "Auto-detected UTM"
) -> Path:
    """
    Export safe zones to GeoJSON format with metadata.

    Args:
        zones_gdf: GeoDataFrame with safe zones (any CRS)
        output_dir: Directory for output file (city subdirectory will be created)
        filename: Output filename
        city_name: Name of the city for metadata
        target_crs: CRS used for processing

    Returns:
        Path to exported GeoJSON file
    """
    logger.info(f"Exporting {len(zones_gdf)} zones to GeoJSON...")

    if zones_gdf.crs.to_string() != "EPSG:4326":
        zones_wgs84 = zones_gdf.to_crs("EPSG:4326")
    else:
        zones_wgs84 = zones_gdf

    city_slug = slugify_city_name(city_name)
    city_output_dir = output_dir / city_slug
    city_output_dir.mkdir(parents=True, exist_ok=True)
    output_path = city_output_dir / filename

    zones_wgs84.to_file(output_path, driver='GeoJSON')

    with open(output_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)

    metadata = get_geojson_metadata(city_name, target_crs)
    metadata["generated_at"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    metadata["feature_count"] = len(zones_gdf)
    metadata["total_area_km2"] = round(zones_gdf['area_m2'].sum() / 1_000_000, 2)

    geojson_data.update(metadata)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson_data, f, ensure_ascii=False, indent=2)

    logger.info(f"GeoJSON with metadata saved to {output_path}")
    return output_path


def export_zones_to_csv(
    zones_gdf: gpd.GeoDataFrame,
    output_dir: Path,
    filename: str = "safe_zones.csv",
    city_name: str = "Unknown City"
) -> Path:
    """
    Export safe zones to CSV format with zone metadata.

    Args:
        zones_gdf: GeoDataFrame with safe zones (any CRS)
        output_dir: Directory for output file (city subdirectory will be created)
        filename: Output filename
        city_name: Name of the city for creating subdirectory

    Returns:
        Path to exported CSV file
    """
    logger.info(f"Exporting {len(zones_gdf)} zones to CSV...")

    # Check if CRS is geographic (WGS84) - if so, need to use projected CRS for accurate centroids
    if zones_gdf.crs.is_geographic:
        # Import here to avoid circular dependency
        from .config import get_utm_crs_for_location

        # Auto-detect appropriate UTM zone
        utm_crs = get_utm_crs_for_location(zones_gdf)
        zones_projected = zones_gdf.to_crs(utm_crs)
        # Calculate centroids in projected CRS
        centroids_projected = zones_projected.geometry.centroid
        # Create GeoDataFrame with projected centroids
        centroids_gdf = gpd.GeoDataFrame(geometry=centroids_projected, crs=utm_crs)
        # Convert to WGS84 for output
        centroids_wgs84 = centroids_gdf.to_crs("EPSG:4326")
    else:
        # Already in projected CRS, calculate centroids directly
        centroids_projected = zones_gdf.geometry.centroid
        # Create GeoDataFrame with centroids
        centroids_gdf = gpd.GeoDataFrame(geometry=centroids_projected, crs=zones_gdf.crs)
        # Convert to WGS84 for output
        centroids_wgs84 = centroids_gdf.to_crs("EPSG:4326")

    df = pd.DataFrame({
        'zone_id': zones_gdf['zone_id'],
        'area_m2': zones_gdf['area_m2'].round(2),
        'perimeter_m': zones_gdf['perimeter_m'].round(2),
        'compactness': zones_gdf['compactness'].round(4),
        'size_class': zones_gdf['size_class'],
        'centroid_lat': centroids_wgs84.geometry.y.round(6),
        'centroid_lon': centroids_wgs84.geometry.x.round(6),
    })

    city_slug = slugify_city_name(city_name)
    city_output_dir = output_dir / city_slug
    city_output_dir.mkdir(parents=True, exist_ok=True)
    output_path = city_output_dir / filename

    df.to_csv(output_path, index=False)

    logger.info(f"CSV saved to {output_path}")
    return output_path


def export_zones_to_kml(
    zones_gdf: gpd.GeoDataFrame,
    output_dir: Path,
    filename: str = "safe_zones.kml",
    city_name: str = "Unknown City"
) -> Path:
    """
    Export safe zones to KML format for Google Earth and mobile apps.

    Args:
        zones_gdf: GeoDataFrame with safe zones (any CRS)
        output_dir: Directory for output file (city subdirectory will be created)
        filename: Output filename
        city_name: Name of the city for metadata

    Returns:
        Path to exported KML file
    """
    logger.info(f"Exporting {len(zones_gdf)} zones to KML...")

    # Convert to WGS84 (required for KML)
    if zones_gdf.crs.to_string() != "EPSG:4326":
        zones_wgs84 = zones_gdf.to_crs("EPSG:4326")
    else:
        zones_wgs84 = zones_gdf

    city_slug = slugify_city_name(city_name)
    city_output_dir = output_dir / city_slug
    city_output_dir.mkdir(parents=True, exist_ok=True)
    output_path = city_output_dir / filename

    # Create KML structure
    kml = ET.Element('kml', xmlns='http://www.opengis.net/kml/2.2')
    document = ET.SubElement(kml, 'Document')

    # Add metadata
    ET.SubElement(document, 'name').text = f"{city_name} - Fireworks Safe Zones"
    ET.SubElement(document, 'description').text = (
        f"Safe zones for consumer fireworks in {city_name}. "
        f"Based on international safety standards (NFPA 1123, Czech Act 344/2025, Missouri RSMo 320.151). "
        f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}. "
        f"Total zones: {len(zones_gdf)}. "
        f"Total area: {zones_gdf['area_m2'].sum() / 1_000_000:.2f} km²."
    )

    # Add styles for different size classes
    styles = {
        'Small': '#FFE599',     # Light yellow
        'Medium': '#FFD966',    # Yellow
        'Large': '#FFB347',     # Orange
        'Very Large': '#FF8C42' # Dark orange
    }

    for size_class, color in styles.items():
        style = ET.SubElement(document, 'Style', id=f'style_{size_class.replace(" ", "_")}')
        poly_style = ET.SubElement(style, 'PolyStyle')
        ET.SubElement(poly_style, 'color').text = f'7f{color[5:7]}{color[3:5]}{color[1:3]}'  # Convert to KML color
        ET.SubElement(poly_style, 'fill').text = '1'
        ET.SubElement(poly_style, 'outline').text = '1'
        line_style = ET.SubElement(style, 'LineStyle')
        ET.SubElement(line_style, 'color').text = f'ff{color[5:7]}{color[3:5]}{color[1:3]}'
        ET.SubElement(line_style, 'width').text = '2'

    # Add zones as placemarks
    for idx, row in zones_wgs84.iterrows():
        placemark = ET.SubElement(document, 'Placemark')
        ET.SubElement(placemark, 'name').text = f"Zone {row['zone_id']}"

        # Description with zone details
        description = (
            f"<![CDATA["
            f"<b>Zone ID:</b> {row['zone_id']}<br>"
            f"<b>Area:</b> {row['area_m2']:,.0f} m² ({row['area_m2']/10000:.2f} ha)<br>"
            f"<b>Size Class:</b> {row['size_class']}<br>"
            f"<b>Perimeter:</b> {row['perimeter_m']:,.0f} m<br>"
            f"<b>Compactness:</b> {row['compactness']:.3f}<br>"
            f"<br><i>Safe for consumer fireworks (F2/F3 category)</i>"
            f"]]>"
        )
        ET.SubElement(placemark, 'description').text = description

        # Style reference
        ET.SubElement(placemark, 'styleUrl').text = f"#style_{row['size_class'].replace(' ', '_')}"

        # Geometry
        polygon = ET.SubElement(placemark, 'Polygon')
        ET.SubElement(polygon, 'extrude').text = '0'
        ET.SubElement(polygon, 'altitudeMode').text = 'clampToGround'

        outer_boundary = ET.SubElement(polygon, 'outerBoundaryIs')
        linear_ring = ET.SubElement(outer_boundary, 'LinearRing')

        # Extract coordinates
        coords = []
        if row.geometry.geom_type == 'Polygon':
            for x, y in row.geometry.exterior.coords:
                coords.append(f"{x},{y},0")
        elif row.geometry.geom_type == 'MultiPolygon':
            # Use first polygon for simplicity
            for x, y in list(row.geometry.geoms)[0].exterior.coords:
                coords.append(f"{x},{y},0")

        ET.SubElement(linear_ring, 'coordinates').text = ' '.join(coords)

    # Write KML file
    tree = ET.ElementTree(kml)
    ET.indent(tree, space='  ')
    tree.write(output_path, encoding='utf-8', xml_declaration=True)

    logger.info(f"KML saved to {output_path}")
    return output_path


def export_zones_to_kmz(
    zones_gdf: gpd.GeoDataFrame,
    output_dir: Path,
    filename: str = "safe_zones.kmz",
    city_name: str = "Unknown City"
) -> Path:
    """
    Export safe zones to KMZ format (compressed KML) for mobile apps.

    KMZ is the preferred format for mobile distribution as it's compressed
    and supported by Google Maps, Apple Maps, and most navigation apps.

    Args:
        zones_gdf: GeoDataFrame with safe zones (any CRS)
        output_dir: Directory for output file (city subdirectory will be created)
        filename: Output filename
        city_name: Name of the city for metadata

    Returns:
        Path to exported KMZ file
    """
    logger.info(f"Exporting {len(zones_gdf)} zones to KMZ (compressed)...")

    city_slug = slugify_city_name(city_name)
    city_output_dir = output_dir / city_slug
    city_output_dir.mkdir(parents=True, exist_ok=True)

    # First create KML in temporary location
    temp_kml_path = city_output_dir / "temp_doc.kml"
    export_zones_to_kml(zones_gdf, output_dir, "temp_doc.kml", city_name)

    # Create KMZ (zip archive with KML inside)
    output_path = city_output_dir / filename
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as kmz:
        kmz.write(temp_kml_path, arcname='doc.kml')

    # Clean up temporary KML
    temp_kml_path.unlink()

    file_size = output_path.stat().st_size / 1024  # KB
    logger.info(f"KMZ saved to {output_path} ({file_size:.1f} KB)")
    return output_path
