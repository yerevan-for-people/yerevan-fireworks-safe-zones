# Jupyter Notebooks

Interactive analysis and visualization of Yerevan fireworks safe zones.

## Available Notebooks

### `analyze_safe_zones.ipynb`

Comprehensive interactive analysis including:
- Data loading from OpenStreetMap (39 categories)
- Obstacle statistics and visualization
- Safe zone generation with differentiated buffers (20-300m)
- Size distribution analysis
- Interactive maps with matplotlib
- Zone metadata analysis
- Export to GeoJSON and CSV

**Features:**
- Uses current API with differentiated buffers
- Detailed statistics and visualizations
- Interactive exploration
- Well-documented code cells

## Getting Started

### 1. Install Jupyter

```bash
pip install jupyter matplotlib
```

### 2. Launch Notebook

```bash
cd notebooks
jupyter notebook analyze_safe_zones.ipynb
```

### 3. Run Cells

Execute cells sequentially (Shift+Enter) or run all (Cell > Run All).

**Note:** First run takes 2-3 minutes to download OSM data. Subsequent runs use cached data.

## Notebook Structure

1. **Setup** - Import modules, configure parameters
2. **Load Data** - Boundary + obstacles (39 categories)
3. **Obstacle Statistics** - Analysis by category and buffer
4. **Generate Safe Zones** - Apply differentiated buffers
5. **Zone Analysis** - Size distribution, area statistics
6. **Map Visualization** - Interactive matplotlib maps
7. **Top Zones** - Largest zones with coordinates
8. **Export** - Save to GeoJSON/CSV
9. **Summary** - Final statistics

## Output

The notebook generates:
- **Visualizations** - Charts and maps in the notebook
- **Data files** - `data/safe_zones.geojson`, `data/safe_zones.csv`
- **Statistics** - Printed analysis results

## Customization

### Change Minimum Zone Area

```python
MIN_ZONE_AREA = 5000  # Only zones >= 5000 m²
```

### Use Custom Buffers

```python
custom_buffers = {
    'buildings': 50.0,    # Override to 50m
    'hospitals': 100.0,   # Override to 100m
    # ... other categories use defaults
}

forbidden_zone = create_forbidden_zone_with_custom_buffers(
    obstacles,
    custom_buffers=custom_buffers
)
```

### Adjust Visualization

```python
# Sample more/fewer buildings
sample_size = min(5000, len(buildings))  # Adjust 5000

# Change map size
fig, ax = plt.subplots(figsize=(20, 16))  # Larger map
```

## Tips

- **Performance**: First run takes longer due to OSM download
- **Memory**: Uses ~2-3 GB RAM for full Yerevan
- **Cache**: OSMnx caches data in `~/.osmnx/cache/`
- **Restart**: Kernel > Restart & Clear Output if issues occur

## For More Information

- **Main CLI**: `python -m src.main --help`
- **Configuration**: See `src/config.py` for all 39 categories
- **Validation**: Run `python tag_audit.py` to verify config
- **Examples**: See `examples/` for standalone Python scripts

## Alternative Tools

For non-interactive analysis, use:
- **CLI**: `python -m src.main --generate-zones`
- **Python script**: `examples/python_api_example.py`
- **Visualization**: `examples/visualize_zones.py`

## Troubleshooting

**Import errors:**
```bash
pip install -r ../requirements.txt
```

**OSM download fails:**
- Check internet connection
- Wait a moment and retry
- OSMnx may be rate-limited

**Out of memory:**
- Reduce sample size for buildings
- Use smaller minimum zone area
- Close other applications

**Kernel crash:**
- Restart kernel
- Clear output
- Run cells sequentially (not all at once)
