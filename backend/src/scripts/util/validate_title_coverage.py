"""Validate political title coverage for a map (county provinces + duchy refs)."""

from __future__ import annotations

import json
import os
import sys

from src.scripts.loader.provinces import load_province_catalog
from src.scripts.util.dirs import defines_file, validate_map


def _load_title_json(map_name: str, filename: str) -> dict:
    path = defines_file(map_name, filename)
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{filename} must be a JSON object")
    return data


def validate_title_coverage(map_name: str) -> list[str]:
    """Return a list of human-readable validation errors (empty if valid)."""
    validate_map(map_name)
    errors: list[str] = []

    catalog = load_province_catalog(map_name)
    catalog_ids = {row["id"] for row in catalog}

    county_data = _load_title_json(map_name, "county.json")
    duchy_data = _load_title_json(map_name, "duchy.json")

    province_to_county: dict[int, str] = {}
    county_ids = set(county_data.keys())

    for county_id, entry in county_data.items():
        if not isinstance(entry, dict):
            errors.append(f"County '{county_id}' must be a JSON object")
            continue
        provinces = entry.get("provinces")
        if not isinstance(provinces, list):
            errors.append(f"County '{county_id}' requires a provinces array")
            continue
        for item in provinces:
            if not isinstance(item, int):
                errors.append(
                    f"County '{county_id}' provinces must contain integers only"
                )
                continue
            if item in province_to_county:
                other = province_to_county[item]
                errors.append(
                    f"Province {item} is assigned to both '{other}' and '{county_id}'"
                )
            province_to_county[item] = county_id

    unassigned = sorted(catalog_ids - set(province_to_county.keys()))
    if unassigned:
        preview = ", ".join(str(pid) for pid in unassigned[:20])
        suffix = "" if len(unassigned) <= 20 else f" ... ({len(unassigned)} total)"
        errors.append(f"Provinces not in any county: {preview}{suffix}")

    orphan_provinces = sorted(set(province_to_county.keys()) - catalog_ids)
    if orphan_provinces:
        preview = ", ".join(str(pid) for pid in orphan_provinces[:20])
        suffix = "" if len(orphan_provinces) <= 20 else f" ... ({len(orphan_provinces)} total)"
        errors.append(f"County provinces missing from catalog: {preview}{suffix}")

    if duchy_data:
        county_to_duchy: dict[str, str] = {}
        for duchy_id, entry in duchy_data.items():
            if not isinstance(entry, dict):
                errors.append(f"Duchy '{duchy_id}' must be a JSON object")
                continue
            titles = entry.get("titles")
            if not isinstance(titles, list):
                errors.append(f"Duchy '{duchy_id}' requires a titles array")
                continue
            for item in titles:
                child_id = str(item).strip()
                if not child_id:
                    errors.append(f"Duchy '{duchy_id}' has an empty child id in titles")
                    continue
                if child_id not in county_ids:
                    errors.append(
                        f"Duchy '{duchy_id}' references unknown county '{child_id}'"
                    )
                if child_id in county_to_duchy:
                    other = county_to_duchy[child_id]
                    errors.append(
                        f"County '{child_id}' is assigned to both '{other}' and '{duchy_id}'"
                    )
                county_to_duchy[child_id] = duchy_id

    return errors


def format_report(map_name: str, errors: list[str]) -> str:
    catalog_count = len(load_province_catalog(map_name))
    county_data = _load_title_json(map_name, "county.json")
    duchy_data = _load_title_json(map_name, "duchy.json")

    lines = [
        f"Title coverage report for map '{map_name}'",
        f"  Provinces in catalog: {catalog_count}",
        f"  Counties: {len(county_data)}",
        f"  Duchies: {len(duchy_data)}",
    ]

    if errors:
        lines.append("Errors:")
        for error in errors:
            lines.append(f"  - {error}")
    else:
        lines.append("OK: all checks passed.")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    map_name = args[0] if args else "main"

    try:
        errors = validate_title_coverage(map_name)
    except (ValueError, FileNotFoundError) as exc:
        print(f"Error: {exc}")
        return 1

    print(format_report(map_name, errors))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
