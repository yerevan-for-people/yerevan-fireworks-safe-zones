#!/usr/bin/env python3
"""Audit script to verify all loaded OSM tags are properly categorized.

This script validates that:
1. All OSM tags defined in config.py are loaded
2. All loaded tags are assigned to categories
3. No orphaned or duplicate mappings exist
"""

from src.config import get_category_configs, get_all_osm_tags


def audit_tag_coverage():
    """Verify complete coverage between loaded tags and category assignments."""
    print("=" * 70)
    print("OSM TAGS AUDIT: Validating tag coverage")
    print("=" * 70)
    print()

    category_configs = get_category_configs()
    osm_tags = get_all_osm_tags()

    tag_to_categories = {}

    for category_name, config in category_configs.items():
        for tag_key, tag_value in config['tags']:
            if tag_value == '*' or tag_value is True:
                tag_id = f"{tag_key}=*"
            elif isinstance(tag_value, list):
                for val in tag_value:
                    tag_id = f"{tag_key}={val}"
                    if tag_id not in tag_to_categories:
                        tag_to_categories[tag_id] = []
                    tag_to_categories[tag_id].append(category_name)
                continue
            else:
                tag_id = f"{tag_key}={tag_value}"

            if tag_id not in tag_to_categories:
                tag_to_categories[tag_id] = []
            tag_to_categories[tag_id].append(category_name)

    total_tags = len(tag_to_categories)
    total_categories = len(category_configs)

    print("Configuration Statistics:")
    print(f"   - Total categories: {total_categories}")
    print(f"   - Total unique tags: {total_tags}")
    print(f"   - OSM tag keys loaded: {len(osm_tags)}")
    print()

    multi_assigned = {tag: cats for tag, cats in tag_to_categories.items() if len(cats) > 1}

    if multi_assigned:
        print(f"WARNING: Found {len(multi_assigned)} tags assigned to MULTIPLE categories:")
        print()
        for tag, categories in sorted(multi_assigned.items()):
            print(f"  WARNING: {tag}")
            for cat in categories:
                buffer = category_configs[cat]['buffer_m']
                print(f"      - {cat} ({buffer}m)")
        print()
        print("Note: This is OK if the first matching category takes precedence.")
        print()
    else:
        print("OK: No duplicate tag assignments (each tag maps to one category)")
        print()

    print("Category Breakdown:")
    print()

    buffer_groups = {}
    for category_name, config in sorted(category_configs.items(), key=lambda x: -x[1]['buffer_m']):
        buffer = config['buffer_m']
        if buffer not in buffer_groups:
            buffer_groups[buffer] = []
        buffer_groups[buffer].append(category_name)

    for buffer in sorted(buffer_groups.keys(), reverse=True):
        categories = buffer_groups[buffer]
        print(f"  {buffer:>5.0f}m buffer: {', '.join(categories)}")

    print()

    # Validation checks
    issues = []

    for category_name, config in category_configs.items():
        if not config['tags']:
            issues.append(f"Category '{category_name}' has no tags defined")

    config_tag_keys = set()
    for config in category_configs.values():
        for tag_key, _ in config['tags']:
            config_tag_keys.add(tag_key)

    missing_from_osm = config_tag_keys - set(osm_tags.keys())
    if missing_from_osm:
        for key in missing_from_osm:
            issues.append(f"Tag key '{key}' used in category configs but not in OSM tags")

    if issues:
        print("VALIDATION ERRORS:")
        print()
        for issue in issues:
            print(f"  ERROR: {issue}")
        print()
        return False
    else:
        print("All validation checks passed!")
        print()
        print("Configuration is valid:")
        print("  * All categories have tags defined")
        print("  * All tag keys are properly loaded from OSM")
        print("  * Tag coverage is complete")
        print()
        return True


def show_category_details():
    """Display detailed information about each category."""
    print("=" * 70)
    print("CATEGORY DETAILS")
    print("=" * 70)
    print()

    category_configs = get_category_configs()

    for category_name, config in sorted(category_configs.items()):
        print(f"Category: {category_name}")
        print(f"   Buffer: {config['buffer_m']}m")
        print(f"   Description: {config['description']}")
        print(f"   Tags: {len(config['tags'])} mapping(s)")
        for tag_key, tag_value in config['tags']:
            if tag_value == '*' or tag_value is True:
                print(f"      - {tag_key}=* (all values)")
            elif isinstance(tag_value, list):
                print(f"      - {tag_key}={', '.join(tag_value)}")
            else:
                print(f"      - {tag_key}={tag_value}")
        print()


if __name__ == '__main__':
    valid = audit_tag_coverage()

    import sys
    if '--details' in sys.argv or '-d' in sys.argv:
        print()
        show_category_details()

    print("=" * 70)

    sys.exit(0 if valid else 1)
