"""Configuration for fireworks safety zones.

This module defines all obstacle categories, their safety buffer distances,
and OSM tag mappings. All values are based on international safety standards
and can be customized for different jurisdictions.

Buffer Distance Standards:
- Critical hazards (fuel, power, airports): 50-300m
- Health/safety facilities (hospitals, schools): 50-100m
- Government/security facilities: 50m
- Cultural/historic sites: 30-50m
- Natural areas and recreation: 20-50m
- Infrastructure and commercial: 20-30m

References:
- Czech Republic: Act No. 344/2025 Coll. (250m hospitals, nursing homes, zoos, animal shelters ONLY)
- NFPA 1123: Professional fireworks safety (USA) - 70 ft/inch aerial shells
- Missouri RSMo 320.151: 600 ft (183m) from churches, schools, hospitals, fuel stations
- Tasmania WorkSafe: 500m from schools verified
- UK Highways Act 1980: 50 ft (15m) from highways
- EU Directive 2013/29/EU: Fireworks classification (F1-F4)
"""

from typing import TypedDict, Literal, Union

try:
    import geopandas as gpd
except ImportError:
    gpd = None


# Type definitions
TagKey = Literal[
    'amenity', 'landuse', 'leisure', 'tourism', 'natural', 'waterway',
    'historic', 'power', 'aeroway', 'railway', 'man_made', 'office',
    'boundary', 'shop'
]

TagValue = Union[str, list[str]]


class CategoryConfig(TypedDict, total=False):
    """Configuration for a single obstacle category.

    Required fields:
        buffer_m: Safety buffer distance in meters
        tags: OSM tag mappings for this category
        description: Human-readable description

    Optional fields (for standards documentation):
        standard: Standard reference code (e.g., 'PH_EO_047_2025', 'NFPA_1123')
        confidence: Confidence level ('HIGH', 'MEDIUM', 'LOW')
        source: Link to STANDARDS.md section (e.g., 'STANDARDS.md#21-hospitals-50m')
    """
    buffer_m: float  # Required
    tags: list[tuple[TagKey, TagValue]]  # Required
    description: str  # Required
    standard: str  # Optional: Standard reference
    confidence: str  # Optional: 'HIGH', 'MEDIUM', 'LOW'
    source: str  # Optional: STANDARDS.md anchor


# Coordinate Reference Systems
WGS84_EPSG = "EPSG:4326"  # Geographic CRS for input/output

# Grid generation
DEFAULT_GRID_STEP_M = 10.0
DEFAULT_MIN_ZONE_AREA_M2 = 2000.0

# Retry settings for OSM downloads
OSM_MAX_RETRIES = 3
OSM_RETRY_DELAY_S = 5


def get_category_configs() -> dict[str, CategoryConfig]:
    """
    Get complete obstacle category configuration.

    Returns:
        Dictionary mapping category names to their configuration.
        Each category has buffer distance, OSM tags, and description.
    """
    return {
        # === CRITICAL HAZARDS (50-300m) ===

        'fuel_stations': {
            'buffer_m': 100.0,
            'tags': [('amenity', 'fuel')],
            'description': 'Gas stations and fuel depots',
            'standard': 'NFPA_1123 (91m hazmat) + Missouri (183m)',
            'confidence': 'MEDIUM',
            'source': 'STANDARDS.md#11-fuel-stations-100m'
        },

        'power_plants': {
            'buffer_m': 100.0,
            'tags': [('power', ['plant', 'generator'])],
            'description': 'Power generation facilities',
            'standard': 'US_Municipal_Codes (150 ft electrical) + critical infrastructure',
            'confidence': 'MEDIUM'
        },

        'substations': {
            'buffer_m': 50.0,
            'tags': [
                ('power', 'substation'),
                ('man_made', 'substation')
            ],
            'description': 'Electrical substations and transformers',
            'standard': 'US_Municipal_Codes (150 ft/45m from electrical lines)',
            'confidence': 'MEDIUM'
        },

        'power_lines': {
            'buffer_m': 30.0,
            'tags': [
                ('power', ['line', 'minor_line'])
            ],
            'description': 'Overhead electrical power lines',
            'standard': 'US_Municipal_Codes (150 ft/45m from overhead electrical lines)',
            'confidence': 'MEDIUM'
        },

        'airports': {
            'buffer_m': 1500.0,
            'tags': [('aeroway', ['aerodrome', 'runway', 'taxiway'])],
            'description': 'Airports and airport infrastructure (runways, taxiways)',
            'standard': 'UK_CAA_CAP_736 (5.6km notification) + ICAO',
            'confidence': 'HIGH',
            'source': 'STANDARDS.md#12-airports-1500m'
        },

        'helipads': {
            'buffer_m': 500.0,
            'tags': [('aeroway', 'helipad')],
            'description': 'Helicopter landing pads and helipads',
            'standard': 'ICAO aviation safety (300-500 ft operations, 500m conservative)',
            'confidence': 'MEDIUM',
            'source': 'STANDARDS.md#13-helipads-500m'
        },

        'military': {
            'buffer_m': 100.0,
            'tags': [('landuse', 'military')],
            'description': 'Military bases and installations',
            'standard': 'Security considerations (500m recommended for conflict zones)',
            'confidence': 'LOW'
        },

        # === HEALTH & SAFETY (50m) ===

        'hospitals': {
            'buffer_m': 50.0,
            'tags': [('amenity', 'hospital')],
            'description': 'Hospitals and medical centers',
            'standard': 'CZ_Act_344_2025 (250m adapted)',
            'confidence': 'MEDIUM',
            'source': 'STANDARDS.md#21-hospitals-50m'
        },

        'schools': {
            'buffer_m': 100.0,
            'tags': [('amenity', ['school', 'kindergarten', 'university', 'college'])],
            'description': 'Educational facilities',
            'standard': 'Missouri RSMo 320.151 (183m) + Tasmania WorkSafe (500m) adapted',
            'confidence': 'MEDIUM',
            'source': 'STANDARDS.md#22-schools-100m'
        },

        'nursing_homes': {
            'buffer_m': 50.0,
            'tags': [('amenity', ['nursing_home', 'social_facility'])],
            'description': 'Care facilities for elderly and vulnerable populations',
            'standard': 'CZ_Act_344_2025 (250m adapted)',
            'confidence': 'MEDIUM'
        },

        # === ANIMAL FACILITIES (30-100m) ===

        'animal_facilities': {
            'buffer_m': 30.0,
            'tags': [('amenity', ['animal_shelter', 'animal_boarding', 'veterinary'])],
            'description': 'Animal shelters, boarding facilities, and veterinary clinics',
            'standard': 'CZ_Act_344_2025 (250m from animal shelters) adapted for small facilities',
            'confidence': 'MEDIUM'
        },

        'theme_parks': {
            'buffer_m': 100.0,
            'tags': [('tourism', ['zoo', 'aquarium', 'theme_park'])],
            'description': 'Zoos, aquariums, and theme parks',
            'standard': 'CZ_Pyrotechnic_2025 (reduced from 250m)',
            'confidence': 'MEDIUM',
            'source': 'STANDARDS.md#31-zoos--theme-parks-100m'
        },

        # === GOVERNMENT & SECURITY (50m) ===

        'government': {
            'buffer_m': 50.0,
            'tags': [
                ('amenity', ['townhall', 'embassy']),
                ('office', ['government', 'diplomatic']),
                ('landuse', 'institutional')
            ],
            'description': 'Government buildings, embassies, and institutional complexes'
        },

        'security': {
            'buffer_m': 50.0,
            'tags': [('amenity', ['police', 'fire_station', 'prison'])],
            'description': 'Police stations, fire stations, and correctional facilities'
        },

        # === CULTURAL & HISTORIC (30-50m) ===

        'memorials': {
            'buffer_m': 50.0,
            'tags': [('historic', 'memorial')],
            'description': 'Memorial sites (e.g., Tsitsernakaberd Genocide Memorial)',
            'standard': 'CFPA_E_Guideline_30_2013 (heritage fire protection)',
            'confidence': 'MEDIUM'
        },

        'monuments': {
            'buffer_m': 50.0,
            'tags': [('historic', 'monument')],
            'description': 'Historic monuments and landmarks',
            'standard': 'CFPA_E_Guideline_30_2013 (heritage fire protection)',
            'confidence': 'MEDIUM'
        },

        'historic_sites': {
            'buffer_m': 50.0,
            'tags': [('historic', ['archaeological_site', 'castle', 'fort', 'heritage', 'ruins'])],
            'description': 'Archaeological sites, castles, forts, and heritage sites',
            'standard': 'CFPA_E_Guideline_30_2013 (heritage fire protection)',
            'confidence': 'MEDIUM'
        },

        'museums': {
            'buffer_m': 30.0,
            'tags': [('tourism', ['museum', 'gallery'])],
            'description': 'Museums and art galleries',
            'standard': 'CFPA_E_Guideline_30_2013 (cultural collections protection)',
            'confidence': 'MEDIUM'
        },

        'tourism_attractions': {
            'buffer_m': 30.0,
            'tags': [('tourism', ['attraction', 'artwork', 'viewpoint'])],
            'description': 'Tourist attractions, public artwork, and viewpoints (e.g., Cascade Complex)'
        },

        'religious': {
            'buffer_m': 50.0,
            'tags': [('landuse', 'religious')],
            'description': 'Churches, monasteries, and religious sites',
            'standard': 'Missouri RSMo 320.151 (183m from churches) adapted',
            'confidence': 'MEDIUM',
            'source': 'STANDARDS.md#41-churches--religious-sites-50m'
        },

        'cemeteries': {
            'buffer_m': 50.0,
            'tags': [
                ('landuse', 'cemetery'),
                ('amenity', 'grave_yard')
            ],
            'description': 'Cemeteries and burial grounds'
        },

        # === NATURAL & RECREATION (20-50m) ===

        'parks': {
            'buffer_m': 30.0,
            'tags': [
                ('leisure', ['park', 'garden', 'playground', 'pitch', 'stadium',
                            'sports_centre', 'nature_reserve', 'track'])
            ],
            'description': 'Parks, gardens, playgrounds, and sports facilities'
        },

        'forests': {
            'buffer_m': 30.0,
            'tags': [
                ('landuse', 'forest'),
                ('natural', ['wood', 'scrub', 'tree_row', 'shrubbery'])
            ],
            'description': 'Forests, woods, and tree-covered areas (fire risk)'
        },

        'agriculture': {
            'buffer_m': 30.0,
            'tags': [('landuse', ['farmland', 'orchard', 'vineyard', 'meadow', 'greenfield'])],
            'description': 'Agricultural land, orchards, vineyards, and meadows'
        },

        'protected_areas': {
            'buffer_m': 50.0,
            'tags': [('boundary', 'protected_area')],
            'description': 'Nature reserves and protected environmental areas'
        },

        'water_bodies': {
            'buffer_m': 20.0,
            'tags': [('natural', 'water')],
            'description': 'Lakes, ponds, and reservoirs'
        },

        'waterways': {
            'buffer_m': 20.0,
            'tags': [('waterway', '*')],
            'description': 'Rivers, streams, canals (e.g., Hrazdan River)'
        },

        'natural_hazards': {
            'buffer_m': 50.0,
            'tags': [('natural', ['cliff', 'valley', 'wetland'])],
            'description': 'Cliffs, valleys, wetlands, and hazardous terrain'
        },

        # === INFRASTRUCTURE (30-50m) ===

        'railways': {
            'buffer_m': 50.0,
            'tags': [
                ('railway', '*'),
                ('landuse', 'railway')
            ],
            'description': 'Railway infrastructure (stations, tracks, platforms, yards, depots)',
            'standard': 'UK_Network_Rail (radio interference, debris, operational safety)',
            'confidence': 'MEDIUM'
        },

        'driving_facilities': {
            'buffer_m': 30.0,
            'tags': [('amenity', 'driver_training')],
            'description': 'Driving schools and autodromes'
        },

        'construction': {
            'buffer_m': 30.0,
            'tags': [('landuse', ['construction', 'brownfield'])],
            'description': 'Active construction sites and contaminated brownfield land'
        },

        'industrial_extraction': {
            'buffer_m': 50.0,
            'tags': [('landuse', 'quarry')],
            'description': 'Quarries and mineral extraction sites'
        },

        'towers': {
            'buffer_m': 30.0,
            'tags': [('man_made', ['tower', 'water_tower'])],
            'description': 'Communication towers and water towers'
        },

        'reservoirs': {
            'buffer_m': 30.0,
            'tags': [('man_made', 'reservoir_covered')],
            'description': 'Covered water reservoirs'
        },

        # === COMMERCIAL (20-30m) ===

        'marketplaces': {
            'buffer_m': 30.0,
            'tags': [('amenity', 'marketplace')],
            'description': 'Public markets and high foot-traffic commercial areas'
        },

        'commercial_areas': {
            'buffer_m': 30.0,
            'tags': [
                ('landuse', ['commercial', 'retail']),
                ('shop', '*'),
                ('amenity', ['restaurant', 'cafe', 'bar', 'fast_food'])
            ],
            'description': 'Commercial zones, shops, restaurants, and cafes'
        },

        'garages': {
            'buffer_m': 20.0,
            'tags': [('landuse', 'garages')],
            'description': 'Garage complexes and parking structures'
        },

        # === STANDARD OBSTACLES (20-30m) ===

        'buildings': {
            'buffer_m': 30.0,
            'tags': [('building', True)],
            'description': 'All building structures'
        },

        'roads': {
            'buffer_m': 30.0,
            'tags': [
                ('highway', ['motorway', 'trunk', 'primary', 'secondary', 'tertiary',
                            'motorway_link', 'trunk_link', 'primary_link',
                            'secondary_link', 'tertiary_link'])
            ],
            'description': 'Major roads and highways'
        },

        'parking': {
            'buffer_m': 50.0,
            'tags': [
                ('amenity', 'parking'),
                ('landuse', 'parking')
            ],
            'description': 'Parking lots and areas',
            'standard': 'NFPA_1124 (fallout zone for vehicle protection)',
            'confidence': 'MEDIUM'
        },

        'industrial': {
            'buffer_m': 30.0,
            'tags': [('landuse', 'industrial')],
            'description': 'Industrial zones and factories'
        },
    }


def get_buffer_distances() -> dict[str, float]:
    """
    Get buffer distances for all categories.

    Returns:
        Dictionary mapping category name to buffer distance in meters.
    """
    configs = get_category_configs()
    return {name: config['buffer_m'] for name, config in configs.items()}


def get_all_osm_tags() -> dict[TagKey, TagValue]:
    """
    Get all OSM tags that should be loaded from OpenStreetMap.

    Returns:
        Dictionary suitable for OSMnx features_from_polygon() tags parameter.
    """
    configs = get_category_configs()

    # Collect all unique tag combinations
    tags_dict: dict[TagKey, set[str]] = {}
    wildcard_tags: set[TagKey] = set()
    boolean_tags: set[TagKey] = set()

    for config in configs.values():
        for tag_key, tag_value in config['tags']:
            if tag_value == '*':
                wildcard_tags.add(tag_key)
            elif tag_value is True:
                boolean_tags.add(tag_key)
            elif isinstance(tag_value, list):
                if tag_key not in tags_dict:
                    tags_dict[tag_key] = set()
                tags_dict[tag_key].update(tag_value)
            else:
                if tag_key not in tags_dict:
                    tags_dict[tag_key] = set()
                tags_dict[tag_key].add(tag_value)

    # Build final tags dictionary
    result: dict[TagKey, Union[bool, list[str]]] = {}

    # Add wildcard tags (e.g., waterway=*)
    for tag_key in wildcard_tags:
        result[tag_key] = True

    # Add boolean tags (e.g., building=True)
    for tag_key in boolean_tags:
        result[tag_key] = True

    # Add specific value tags
    for tag_key, values in tags_dict.items():
        if tag_key in wildcard_tags or tag_key in boolean_tags:
            continue
        result[tag_key] = sorted(list(values))

    return result


def get_utm_crs_for_location(boundary_gdf: 'gpd.GeoDataFrame') -> str:
    """
    Automatically determine appropriate UTM CRS for a given boundary.

    Uses the centroid of the boundary to calculate the correct UTM zone.

    Args:
        boundary_gdf: GeoDataFrame with boundary geometry (any CRS)

    Returns:
        EPSG code string for the appropriate UTM zone (e.g., "EPSG:32638")

    Examples:
        - Yerevan (40.18°N, 44.51°E) -> UTM Zone 38N -> EPSG:32638
        - Tbilisi (41.69°N, 44.80°E) -> UTM Zone 38N -> EPSG:32638
        - Prague (50.08°N, 14.42°E) -> UTM Zone 33N -> EPSG:32633
        - Sydney (33.87°S, 151.21°E) -> UTM Zone 56S -> EPSG:32756
    """
    # Ensure we're working in WGS84 for centroid calculation
    if boundary_gdf.crs is None:
        raise ValueError("Boundary GeoDataFrame has no CRS")

    if boundary_gdf.crs.to_string() != WGS84_EPSG:
        boundary_wgs84 = boundary_gdf.to_crs(WGS84_EPSG)
    else:
        boundary_wgs84 = boundary_gdf

    # Get centroid coordinates
    centroid = boundary_wgs84.geometry.unary_union.centroid
    lon = centroid.x
    lat = centroid.y

    # Calculate UTM zone number (1-60)
    # Formula: zone = floor((longitude + 180) / 6) + 1
    utm_zone = int((lon + 180) / 6) + 1

    # Determine hemisphere (North or South)
    if lat >= 0:
        # Northern hemisphere: EPSG:326xx
        epsg_code = 32600 + utm_zone
    else:
        # Southern hemisphere: EPSG:327xx
        epsg_code = 32700 + utm_zone

    return f"EPSG:{epsg_code}"
