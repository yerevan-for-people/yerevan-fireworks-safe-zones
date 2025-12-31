# Fireworks Safe Zones Finder

Geospatial analysis tool identifying safe zones for consumer fireworks using OpenStreetMap data and international safety standards. Supports any city worldwide via `--city` parameter.

**⚠️ ARMENIA USERS**: This tool uses international safety standards as reference. Armenian law requires fireworks licensing, restricts sale to licensed traders, and bans use 23:00-07:00 (except Dec 31-Jan 1). No specific distance buffers found in Armenian law. Verify compliance with Armenian Ministry of Internal Affairs before use.

## Summary (Yerevan, Armenia - Example Results)

**393 safe zones** covering **63.57 km²** (28.5% of Yerevan) identified through processing **84,147 obstacles** across **40 categories** with differentiated safety buffers (50-1500m).

---

## Key Results

| Metric              | Value              |
| ------------------- | ------------------ |
| Safe zones          | 393 polygons       |
| Total safe area     | 63.57 km²          |
| Coverage            | 28.5% of Yerevan   |
| Excluded area       | 159.43 km² (71.5%) |
| Obstacles processed | 84,147 features    |
| Categories          | 40 distinct types  |
| Buffer range        | 50-1500 meters     |

### Zone Distribution

| Size Class | Count | %     | Area Range       |
| ---------- | ----- | ----- | ---------------- |
| Small      | 146   | 37.2% | 2,000-5,000 m²   |
| Medium     | 84    | 21.4% | 5,000-10,000 m²  |
| Large      | 99    | 25.2% | 10,000-50,000 m² |
| Very Large | 64    | 16.3% | >50,000 m²       |

---

## Safety Buffer Standards

Buffer distances based on **verified international standards** with citations:

### Critical Hazards (50-1500m)

| Category                    | Buffer | Standard Source                                                |
| --------------------------- | ------ | -------------------------------------------------------------- |
| **Aviation infrastructure** | 1500m  | UK CAA CAP 736 (3nm/5.6km notify, 10nm/18.5km extended) + ICAO |  | **Helipads**               | 500m | ICAO aviation safety (300-500 ft operations)         |  | **Fuel stations** | 100m | NFPA 1123 (91m hazmat) + Missouri (183m) adapted |
| **Military installations**  | 100m   | Security (500m for conflict zones; US bases: full bans)        |
| **Power plants**            | 100m   | US Municipal Codes (150 ft electrical) + transformer fire risk |
| **Zoos, theme parks**       | 100m   | Czech Act 344/2025 (250m adapted)                              |
| **Electrical substations**  | 50m    | US Municipal Codes (150 ft/45m from electrical lines)          |  | **Power lines (overhead)** | 30m  | US Municipal Codes (150 ft/45m adapted for consumer) |
### Health & Education (50-100m)

| Category                  | Buffer | Standard Source                                                |
| ------------------------- | ------ | -------------------------------------------------------------- |
| **Schools, universities** | 100m   | International standards (Missouri 183m, Tasmania 500m) adapted |
| **Hospitals**             | 50m    | Czech Pyrotechnic Articles Act 2025 (250m adapted)             |
| **Nursing homes**         | 50m    | Czech Pyrotechnic Articles Act 2025 (250m adapted)             |

### Government & Security (50m)

| Category                           | Buffer | Standard Source                          |
| ---------------------------------- | ------ | ---------------------------------------- |
| **Government buildings**           | 50m    | Embassies, town halls, National Assembly |
| **Police, fire stations, prisons** | 50m    | Public safety facilities                 |

### Cultural & Historic (30-50m)

| Category                 | Buffer | Standard Source                                     |
| ------------------------ | ------ | --------------------------------------------------- |
| **Memorials**            | 50m    | CFPA-E Guideline 30:2013 (heritage fire protection) |
| **Monuments**            | 50m    | CFPA-E Guideline 30:2013 (heritage fire protection) |
| **Archaeological sites** | 50m    | Historic preservation                               |
| **Religious sites**      | 50m    | Missouri 183m adapted + cultural heritage           |
| **Cemeteries**           | 50m    | Respect for the deceased                            |
| **Museums, galleries**   | 30m    | CFPA-E Guideline 30:2013 (cultural collections)     |
| **Tourist attractions**  | 30m    | Viewpoints, public art                              |

### Natural & Recreation (20-50m)

| Category                        | Buffer | Standard Source                                |
| ------------------------------- | ------ | ---------------------------------------------- |
| **Protected areas**             | 50m    | Environmental protection                       |
| **Cliffs, valleys, wetlands**   | 50m    | Geological hazards                             |
| **Quarries**                    | 50m    | Industrial extraction sites                    |
| **Parks, gardens, stadiums**    | 30m    | Recreation + fire safety                       |
| **Forests, woods**              | 30m    | Fire risk from vegetation                      |
| **Farmland, orchards**          | 30m    | Agricultural protection                        |
| **Animal shelters, veterinary** | 30m    | Czech Act 344/2025 (250m adapted for consumer) |
| **Water bodies**                | 20m    | Pollution prevention                           |
| **Waterways**                   | 20m    | Rivers, canals (pollution)                     |

### Infrastructure & Commercial (30-50m)

| Category               | Buffer | Standard Source                                          |
| ---------------------- | ------ | -------------------------------------------------------- |
| **Railways**           | 50m    | UK Network Rail safety (radio interference, debris risk) |
| **Buildings**          | 30m    | All structures                                           |
| **Roads**              | 30m    | UK Highways Act 1980 (50 ft/15m minimum)                 |
| **Driving schools**    | 30m    | Training facilities                                      |
| **Construction sites** | 30m    | Active hazards                                           |
| **Towers**             | 30m    | Communication/water infrastructure                       |
| **Reservoirs**         | 30m    | Water storage                                            |
| **Marketplaces**       | 30m    | High foot traffic                                        |
| **Commercial zones**   | 30m    | Shops, restaurants, retail                               |
| **Industrial zones**   | 30m    | Manufacturing areas                                      |
| **Parking lots**       | 50m    | NFPA 1124 fallout zone (vehicle protection)              |
| **Garages**            | 20m    | Vehicle storage                                          |

---

## International Standards

All standards fact-checked via web search December 2025. **See [STANDARDS.md](STANDARDS.md)**

### Important: Consumer vs. Professional Fireworks

**This tool is designed for CONSUMER FIREWORKS only** (small shells, 1-3 inches).

**Professional fireworks displays** (3-12 inch shells) require much larger safety distances per NFPA 1123:
- 6-inch professional shell: **128 meters minimum** (our tool uses 30m for buildings - NOT SUFFICIENT!)
- Professional displays MUST follow NFPA 1123 directly, not this tool's defaults

See [STANDARDS.md](STANDARDS.md#critical-distinction-consumer-vs-professional-fireworks) for details.

### Primary Sources (Verified)

| Standard            | Buffer          | Application                               | Verification                                                                                                                                                                                        |
| ------------------- | --------------- | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **UK CAA CAP 736**  | 5.6 km          | Aviation notification zone                | [UK CAA](https://www.caa.co.uk/our-work/publications/documents/content/cap-736/) - 3 nm notification, 10 nm extended control                                                                        |
| **UK Highways Act** | 50 ft           | Roads prohibition distance                | UK Highways Act 1980 - 50 feet (15m) minimum from highways                                                                                                                                          |
| **UK Gov 2025**     | F2: 5m, F3: 25m | Consumer fireworks safe distances         | [UK Government October 2025](https://www.gov.uk/guidance/organising-non-professional-fireworks-displays) - Official injury prevention guidance                                                      |
| **NFPA 1123** (USA) | 70 ft/inch      | Professional aerial shells                | [NFPA Official](https://www.nfpa.org/codes-and-standards/nfpa-1123-standard-development/1123) - Formula: 70 ft × diameter (in)                                                                      |
| **NFPA 1124** (USA) | Fallout zone    | Consumer fireworks retail/use             | [NFPA Official](https://www.nfpa.org/codes-and-standards/nfpa-1124-standard-development/1124) - Vehicle protection and spark scatter                                                                |
| **Czech Republic**  | 250m            | Hospitals, zoos, animal shelters **ONLY** | [Act No. 344/2025 Coll.](https://www.zakonyprolidi.cz/cs/2025-344) - effective 1 December 2025 (schools/churches NOT included)                                                                      |
| **Missouri (USA)**  | 600 ft          | Churches, schools, hospitals              | Missouri Regulations 320.151 RSMo - professional display separations                                                                                                                                |
| **US Municipal**    | 150 ft          | Electrical lines                          | Kittitas County WA, Massachusetts 527 CMR - overhead electrical safety                                                                                                                              |
| **Canada**          | 100-300m        | Schools, hospitals (varies)               | Municipal bylaws: [Caledon 300m](https://www.caledon.ca/en/town-services/fireworks.aspx), [Toronto 100m](https://www.toronto.ca/city-government/public-notices-bylaws/bylaw-enforcement/fireworks/) |

### Applied Values (For Consumer Fireworks)

- **1500m**: Aviation infrastructure - airports, runways (UK CAA 5.6km notification zone, 1500m practical no-fire zone for glide path protection)
- **500m**: Helipads (ICAO: helicopter operations 300-500 ft altitude, conservative civilian buffer)
- **100m**: Fuel stations (NFPA 1123 91m hazmat + Missouri 183m adapted), military (500m for conflict zones; US bases: full bans), schools (international 183-500m adapted), zoos (Czech Act 344/2025 250m adapted), power plants (US Municipal 150 ft electrical + transformer fire risk)
- **50m**: Hospitals (Czech Act 344/2025 250m adapted), nursing homes (Czech Act 344/2025), churches (Missouri 183m adapted), cultural sites (CFPA-E heritage), government, substations (US Municipal 150 ft), railways (Network Rail: radio interference, debris risk), parking (NFPA 1124 fallout zone)
- **30m**: Buildings (NFPA 1123 for 1-2" aerial shells: 21-43m minimum, adapted for consumer practicality; UK Gov 2025: F3 safe >25m), roads (UK Highways Act 1980: 50 ft/15m), parks, forests, museums (CFPA-E), animal shelters (Czech Act 344/2025 250m adapted), power lines overhead (US Municipal 150 ft/45m adapted)
- **20m**: Water bodies, garages (environmental protection, low fire risk)

**CRITICAL**: Aviation 1500m minimum exclusion zone. Professional displays require 5.6 km (3 nm) notification, 18.5 km (10 nm) for extended control zones per UK CAA CAP 736.

**Note**: Buffers based on 2025 verification: UK CAA aviation standards (3nm/10nm zones), UK Highways Act 1980 (50 ft roads), UK Government 2025 (F2 >5m, F3 >25m), US Municipal electrical codes (150 ft), NFPA 1124 fallout zones, CFPA-E heritage protection. Most US military bases impose full fireworks bans.

---

## Installation

### Requirements
- Python 3.11+
- 4 GB RAM (recommended 8 GB)
- 2 GB disk space
- Internet connection (OSM download)

### Setup

```bash
# Clone repository
git clone <repository>
cd yerevan-fireworks-safe-zones

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

---

## Usage

### Generate Safe Zones for Any City

```bash
# Activate environment
source venv/bin/activate

# Yerevan, Armenia (default)
python -m src.main --generate-zones --min-zone-area 2000

# Prague, Czech Republic
python -m src.main --city "Prague, Czech Republic" --generate-zones

# Tbilisi, Georgia
python -m src.main --city "Tbilisi, Georgia" --generate-zones

# Any city with OpenStreetMap data
python -m src.main --city "Your City, Country" --generate-zones

# Validate configuration
python tag_audit.py --details
```

**Supported**: Any city with OpenStreetMap coverage. UTM zone auto-detected.

### Output Files

Generated in `data/{city-slug}/` folder (e.g., `data/yerevan-armenia/`, `data/prague-czech-republic/`):

- **safe_zones.geojson**: Polygon zones with metadata (GeoJSON format)
- **safe_zones.csv**: Zone statistics (CSV format)
- **safe_zones.kml**: Google Earth compatible format (4.1 MB for Yerevan)
- **safe_zones.kmz**: Compressed KML for mobile apps (1.4 MB for Yerevan) ⭐ **Recommended for smartphones**
- **safe_points.geojson**: Point grid (10m spacing, GeoJSON format)
- **safe_points.csv**: Point coordinates (CSV format)

**Mobile Distribution**: Use `.kmz` format - it's compressed and opens directly in:
- Google Maps (Android/iOS)
- Apple Maps (iOS)
- Maps.me
- Most navigation apps

Example sizes for Yerevan:
- safe_zones.geojson: 6.3 MB (393 zones)
- safe_zones.kmz: 1.4 MB (compressed, mobile-friendly) ⭐
- safe_points.geojson: 116 MB (point grid)
- safe_points.csv: 30 MB

### Using on Mobile Devices

**How to open KMZ files on your smartphone:**

1. **Download** `safe_zones.kmz` to your phone
2. **Open with**:
   - **Google Maps** (Android/iOS): Tap file → "Open in Maps"
   - **Apple Maps** (iOS 18+): Tap file → Import
   - **Maps.me**: Tap file → Opens automatically
   - **Google Earth**: Tap file → View in Earth

**Advantages of KMZ:**
- ✅ 3× smaller than GeoJSON (1.4 MB vs 4.1 MB for KML)
- ✅ Color-coded zones by size (yellow to orange)
- ✅ Offline viewing after download
- ✅ Works on any smartphone
- ✅ Clickable zones with details (area, ID, safety class)

### Processing Performance

Example for Yerevan (large city ~223 km², ~84k obstacles):

| Parameter       | Value        |
| --------------- | ------------ |
| Processing time | 8-10 minutes |
| Memory usage    | 2-3 GB       |
| OSM download    | ~20 MB       |
| Output size     | ~152 MB      |

Smaller cities will process faster and use less memory.

---

## Technical Methodology

### Algorithm

```
1. Load OSM data - 39 categories by tags
2. Categorize - Assign each feature to category
3. Auto-detect UTM zone - Based on city centroid
4. Create buffers - 50-1500m per category (in UTM CRS)
5. Union - Merge all buffered obstacles
6. Free space - City boundary MINUS forbidden zones
7. Filter - Remove zones < 2000 m² (default)
8. Metadata - Add area, perimeter, compactness, centroid
9. Export - GeoJSON, CSV, KML, KMZ (WGS84) to city-specific directory
```

### Coordinate Systems

- **Input/Output**: WGS84 (EPSG:4326) - standard GPS
- **Processing**: UTM (auto-detected zone) - accurate meters
- **Auto-detection**: Calculates appropriate UTM zone from city centroid
  - Yerevan (40.18°N, 44.51°E) -> UTM Zone 38N (EPSG:32638)
  - Prague (50.08°N, 14.42°E) -> UTM Zone 33N (EPSG:32633)
  - Tbilisi (41.69°N, 44.80°E) -> UTM Zone 38N (EPSG:32638)

### Data Sources

- **OpenStreetMap**: Open Database License (ODbL), December 2025
- **Territory**: Any city administrative boundary from OSM
- **Coverage**: Global (any city with OSM data)

---

## Configuration

All categories and buffers defined in **single source of truth**: `src/config.py`

### Customize Buffers

```python
# Edit src/config.py
'fuel_stations': {
    'buffer_m': 100.0,  # Change to your jurisdiction
    'tags': [('amenity', 'fuel')],
    'description': 'Gas stations and fuel depots'
}
```

### Add New Category

```python
'your_category': {
    'buffer_m': 50.0,
    'tags': [('your_key', 'your_value')],
    'description': 'Your description'
}
```

### Validate Changes

```bash
python tag_audit.py --details
```

Ensures:
- All OSM tags are categorized (0% data loss)
- No duplicate mappings
- Complete configuration coverage

---

## Viewing Results

### QGIS (Recommended)

1. Install [QGIS](https://qgis.org) (free)
2. Add Layer > Vector > `data/safe_zones.geojson`
3. Add basemap: Web > QuickMapServices > OSM
4. Style by `size_class` or `area_m2`

### Python Analysis

```python
import geopandas as gpd

# Load zones
zones = gpd.read_file('data/safe_zones.geojson')

# Total safe area
total_km2 = zones['area_m2'].sum() / 1_000_000
print(f"Total: {total_km2:.2f} km²")

# Filter by size
large = zones[zones['size_class'] == 'very_large']
print(f"Very large zones: {len(large)}")
```

---

## Error Analysis

### Data Sources

- **OSM incompleteness**: ~5-10% (small objects)
- **OSM accuracy**: ±1-5m (buildings), ±10-50m (natural features)
- **Update lag**: Depends on OSM contributor activity

### Methodology

- **Fixed buffers**: Don't account for firework power, wind
- **2D analysis**: No building heights, terrain slope
- **Temporal**: No temporary obstacles (events, construction)

### Geometric Operations

- **Polygon simplification**: ±1m
- **Coordinate rounding**: ±0.0001°
- **UTM projection**: Minimal distortion for Yerevan

### Total Uncertainty

- **Area**: ±2-5%
- **Zone count**: ±5-10%

---

## Limitations & Disclaimers

### CRITICAL: Fireworks Type Limitation

**This tool is designed ONLY for CONSUMER FIREWORKS** (small aerial shells 1-3 inches).

**DO NOT USE for professional fireworks displays** without professional pyrotechnician input!

Professional displays (3-12 inch shells) require:
- **NFPA 1123 compliance**: 70 feet × shell diameter (in inches)
- **Example**: 6-inch shell = 420 feet (128m) minimum - our tool's 30m building buffer is **INSUFFICIENT**
- **Professional licensing**: Certified pyrotechnician required
- **Site-specific calculations**: Every shell size must be individually calculated

**If planning professional display**: Use this tool ONLY for preliminary site selection, then hire licensed pyrotechnician for final safety plan.

### Scope

**Suitable for**:
- **Consumer fireworks** preliminary location analysis (1-3 inch shells)
- Event planning research (consumer fireworks only)
- Territorial risk assessment for residential fireworks
- Educational purposes

**NOT a substitute for**:
- Official permits from authorities (ALWAYS REQUIRED)
- On-site inspection by qualified personnel
- Professional safety assessment for any display
- Real-time weather analysis (wind critical!)
- NFPA 1123 compliance for professional displays

### Standards Confidence Levels

**HIGH Confidence** (direct official regulations):
- UK CAA CAP 736: 3 nm (5.6 km) notification zone, 10 nm (18.5 km) extended control zone for fireworks near aerodromes
- UK Highways Act 1980: 50 ft (15m) prohibition distance from highways
- Czech Pyrotechnic Articles Act 2025: 250m from hospitals, nursing homes, zoos, animal shelters **ONLY** (schools and churches NOT included in Czech law)
- EU Directive 2013/29/EU: Fireworks classification system (F1-F4)
- ICAO: Aviation safety standards for airspace obstruction

**MEDIUM Confidence** (standards applied or adapted):
- Airports: 1500m exclusion zone (UK CAA 3nm notification, 10nm extended control - practical no-fire zone)
- Helipads: 500m (ICAO aviation safety: helicopter operations 300-500 ft altitude, conservative civilian buffer)
- Roads: 30m (UK Highways Act 1980: 50 ft/15m minimum - tool buffer is conservative)
- Schools: 100m (international standards: Missouri 183m, Tasmania 500m verified; **Czech Act 344/2025 does NOT protect schools**)
- Hospitals: 50m (Czech Act 344/2025 250m adapted for consumer fireworks)
- Fuel stations: 100m (NFPA 1123 91m hazmat storage + Missouri 183m adapted)
- Power plants: 100m (US Municipal Codes 150 ft electrical + transformer fire risk)
- Substations: 50m (US Municipal Codes 150 ft/45m from electrical lines)
- Power lines (overhead): 30m (US Municipal Codes 150 ft/45m adapted for consumer fireworks)
- Railways: 50m (UK Network Rail - radio interference, debris risk, not visual confusion)
- Parking: 50m (NFPA 1124 fallout zone for vehicle protection)
- Museums/Heritage: 30-50m (CFPA-E Guideline No. 30:2013 for combustible heritage structures)
- Animal shelters: 30m (Czech Act 344/2025 250m adapted for consumer fireworks at smaller facilities)
- Buildings: 30m (NFPA 1123 for 1-2" consumer shells + safety margin; UK Gov 2025: F3 safe >25m)

**LOW/Expert Judgment** (no direct authoritative standard):
- Military (100m, 500m for conflict zones): Security-classified, no public fireworks standards; most US bases impose full bans
- Churches (50m): Missouri regulation 183m adapted; **Czech Act 344/2025 does NOT protect churches**
- Garages (20m): Conservative safety principles
- **Users MUST verify local regulations**

### Required Additional Steps

**Mandatory before ANY fireworks use**:
1. **Verify fireworks type**: Consumer (1-3") vs. Professional (3-12")
2. **On-site verification**: Physical inspection of location
3. **Weather check**: Wind direction critical for debris/sparks
4. **Crowd density assessment**: Where will people be
5. **Official permits**: From local authorities (ALWAYS REQUIRED)
6. **Professional safety equipment**: Fire extinguishers, water source
7. **Trained operators**: Responsible adults only
8. **Local regulations**: Verify all local laws and restrictions

**For professional displays, ALSO required**:
- Licensed pyrotechnician (certified professional)
- NFPA 1123 compliance calculations (by professional)
- Site-specific safety plan (by professional)
- Professional liability insurance
- Fire marshal approval
- Emergency response coordination

### Exclusions

Not considered in analysis:
- **Fireworks size**: Assumes consumer fireworks (1-3"), NOT professional (3-12")
- **Weather conditions**: Wind, rain, temperature, humidity
- **Crowd locations**: Dynamic gathering areas
- **Temporary obstacles**: Events, construction, parked vehicles
- **Building heights**: Assumes ground-level only
- **Terrain elevation**: Slope, hills, valleys
- **Time-of-day factors**: Darkness, visibility
- **Operator skill level**: Assumes trained, responsible use
- **Fireworks quality**: Assumes properly manufactured products

---

## Reproducibility

### Environment

```bash
# Exact versions
OSMnx==2.0.7
GeoPandas==1.1.2
Shapely==2.1.2
PyProj==3.7.2
Pandas==2.2.3
NumPy==2.2.1
```

### Validation

```bash
# Verify all tags are categorized
python tag_audit.py

# Expected output:
# All loaded tags are categorized (0% orphaned)
# 39 categories configured
# ~83,000 features processed
```

---

## Project Structure

```
yerevan-fireworks-safe-zones/
├── src/
│   ├── config.py              # 39 categories + buffers + OSM tags
│   ├── osm_loader.py          # Load & categorize OSM data
│   ├── geometry_utils.py      # Buffers, CRS transforms
│   ├── zones_generator.py     # Free space calculation
│   ├── exporters.py           # GeoJSON, CSV export
│   └── main.py                # CLI interface
├── tag_audit.py               # Configuration validator
├── requirements.txt           # Python dependencies
├── examples/                  # Python API usage examples
│   ├── README.md              # Examples documentation
│   ├── python_api_example.py  # Basic API usage
│   └── visualize_zones.py     # Matplotlib visualization
├── notebooks/                 # Jupyter notebooks
│   ├── README.md              # Notebook documentation
│   └── analyze_safe_zones.ipynb  # Interactive analysis
└── data/                      # Output files (generated)
```

---

## References

### Safety Standards

- **NFPA 1123** - Code for Fireworks Display (USA)
  https://www.nfpa.org/codes-and-standards/nfpa-1123-standard-development/1123

- **Czech Republic** - Pyrotechnic Articles Act 2025 (Act No. 344/2025 Coll., 250m from hospitals, nursing homes, zoos, animal shelters)
  https://www.zakonyprolidi.cz/cs/2025-344

- **EU Directive 2013/29/EU** - Fireworks classification and safety requirements
  https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32013L0029

### Software

- OSMnx. *Computers
- OpenStreetMap contributors (2025). https://planet.osm.org
- GeoPandas, Shapely, PyProj - Python geospatial ecosystem

### Data License

- **Code**: MIT License
- **OpenStreetMap Data**: OpenStreetMap contributors (Open Database License - ODbL)

---

## Version

- **Version**: 1.0
- **Date**: December 2025
- **Language**: Python 3.11+
- **Status**: Production Ready

---

## Contact & Contribution

For questions, improvements, or adaptations to other cities, please open an issue or pull request.

**Use for Other Cities**: Just use `--city "Your City, Country"` - all buffer standards are internationally applicable.

### Example for Different Cities

```bash
# European cities
python -m src.main --city "Prague, Czech Republic" --generate-zones
python -m src.main --city "Berlin, Germany" --generate-zones

# Post-Soviet cities
python -m src.main --city "Tbilisi, Georgia" --generate-zones
python -m src.main --city "Kyiv, Ukraine" --generate-zones

# Asian cities
python -m src.main --city "Tokyo, Japan" --generate-zones

# American cities
python -m src.main --city "New York, USA" --generate-zones
```

---

**Safety Notice**: This tool provides preliminary analysis only. Always verify locations on-site, obtain official permits, check weather conditions, and use professional safety equipment before any fireworks display.
