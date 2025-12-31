# Examples

Code examples demonstrating how to use the Yerevan Fireworks Safe Zones library programmatically.

## Available Examples

### 1. Basic API Usage (`python_api_example.py`)

Complete example showing:
- Loading OSM data with 39 differentiated categories
- Creating forbidden zones with custom buffers (20-300m)
- Generating safe zones from free space
- Exporting results to GeoJSON and CSV
- Analyzing results

**Usage:**
```bash
cd examples
python python_api_example.py
```

**Output:** `examples/output/safe_zones.geojson`, `safe_zones.csv`

### 2. Visualization (`visualize_zones.py`)

Creates a matplotlib map showing:
- City boundary
- Buildings (sampled for performance)
- Safe zones colored by size class

**Requirements:**
```bash
pip install matplotlib
```

**Usage:**
```bash
cd examples
python visualize_zones.py
```

**Output:** `examples/output/safe_zones_map.png` + interactive window

## Understanding the Code

### Key Functions

```python
from src.osm_loader import get_yerevan_boundary, load_all_obstacles
from src.geometry_utils import create_forbidden_zone_with_custom_buffers
from src.zones_generator import create_zones_from_free_space, add_zone_metadata
from src.config import get_buffer_distances
```

### Basic Workflow

```python
# 1. Load boundary
boundary = get_yerevan_boundary()

# 2. Load obstacles (39 categories)
obstacles = load_all_obstacles(
    boundary,
    include_sensitive=True,
    split_sensitive=True
)

# 3. Create forbidden zone with differentiated buffers
buffers = get_buffer_distances()  # 20-300m per category
forbidden_zone = create_forbidden_zone_with_custom_buffers(
    obstacles,
    custom_buffers=buffers
)

# 4. Generate safe zones
zones = create_zones_from_free_space(
    boundary,
    forbidden_zone,
    min_zone_area_m2=2000
)

# 5. Add metadata
zones = add_zone_metadata(zones)  # Adds area, perimeter, size_class, etc.
```

### Customization

**Custom buffer distances:**
```python
custom_buffers = {
    'buildings': 50.0,    # Override to 50m
    'hospitals': 100.0,   # Override to 100m
    # ... other categories use defaults from config.py
}

forbidden_zone = create_forbidden_zone_with_custom_buffers(
    obstacles,
    custom_buffers=custom_buffers
)
```

**Custom minimum zone area:**
```python
zones = create_zones_from_free_space(
    boundary,
    forbidden_zone,
    min_zone_area_m2=5000  # Only zones >= 5000 m²
)
```

## Output Format

### GeoJSON Properties

Each safe zone has:
```json
{
  "zone_id": 1,
  "area_m2": 5432.1,
  "perimeter_m": 312.4,
  "compactness": 0.78,
  "size_class": "medium",
  "centroid_x": 449597.2,
  "centroid_y": 4449151.8
}
```

### Size Classes

- `small`: 2,000-5,000 m²
- `medium`: 5,000-10,000 m²
- `large`: 10,000-50,000 m²
- `very_large`: >50,000 m²

## For More Information

- **Main CLI**: `python -m src.main --help`
- **Configuration**: See `src/config.py` for all 39 categories and buffers
- **Validation**: Run `python tag_audit.py` to verify configuration

## Notes

- All examples use the current API with differentiated buffers
- Processing time: ~8-10 minutes for full Yerevan
- Memory usage: ~2-3 GB
- Results are cached by OSMnx for faster subsequent runs
