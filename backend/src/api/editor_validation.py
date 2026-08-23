"""Validation for map title editor tier JSON writes."""

from __future__ import annotations

import json
import os
import re

from src.scripts.util.dirs import defines_file

TITLE_TIERS = frozenset({"county", "duchy", "kingdom", "empire"})
CHILD_TIER = {
    "duchy": "county",
    "kingdom": "duchy",
    "empire": "kingdom",
}

_RGB_PATTERN = re.compile(r"^\d{1,3},\d{1,3},\d{1,3}$")


class TitleValidationError(ValueError):
    """Invalid title tier payload."""


def _load_child_tier(map_name: str, child_tier: str) -> dict:
    path = defines_file(map_name, f"{child_tier}.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TitleValidationError(f"Child tier file '{child_tier}.json' must be a JSON object")
    return data


def _validate_rgb(rgb: str, title_id: str) -> str:
    if not isinstance(rgb, str) or not _RGB_PATTERN.match(rgb.strip()):
        raise TitleValidationError(f"Title '{title_id}' has invalid rgb (use R,G,B with 0-255)")
    parts = [int(p) for p in rgb.strip().split(",")]
    if any(p < 0 or p > 255 for p in parts):
        raise TitleValidationError(f"Title '{title_id}' rgb values must be between 0 and 255")
    return rgb.strip()


def validate_title_tier(tier: str, body: dict, map_name: str) -> dict:
    """Validate and sanitize a full tier JSON object before write."""
    tier = (tier or "").strip().lower()
    if tier not in TITLE_TIERS:
        raise TitleValidationError(
            f"Unknown title tier '{tier}'. Expected one of: {', '.join(sorted(TITLE_TIERS))}"
        )

    if not isinstance(body, dict) or not body:
        raise TitleValidationError("Title data must be a non-empty JSON object")

    seen_rgb: set[str] = set()
    province_owner: dict[int, str] = {}
    child_owner: dict[str, str] = {}
    child_tier = CHILD_TIER.get(tier)
    child_data = _load_child_tier(map_name, child_tier) if child_tier else {}

    clean: dict[str, dict] = {}

    for raw_id, raw_entry in body.items():
        title_id = str(raw_id).strip()
        if not title_id:
            raise TitleValidationError("Title ids must be non-empty strings")

        if not isinstance(raw_entry, dict):
            raise TitleValidationError(f"Title '{title_id}' must be a JSON object")

        name = raw_entry.get("name")
        if not isinstance(name, str) or not name.strip():
            raise TitleValidationError(f"Title '{title_id}' requires a non-empty name")

        rgb = _validate_rgb(raw_entry.get("rgb", ""), title_id)
        if rgb in seen_rgb:
            raise TitleValidationError(f"Duplicate rgb '{rgb}' in tier '{tier}'")
        seen_rgb.add(rgb)

        entry: dict = {
            "name": name.strip(),
            "rgb": rgb,
        }

        if tier == "county":
            provinces = raw_entry.get("provinces")
            if not isinstance(provinces, list):
                raise TitleValidationError(f"County '{title_id}' requires a provinces array")
            province_ids: list[int] = []
            for item in provinces:
                if not isinstance(item, int):
                    raise TitleValidationError(
                        f"County '{title_id}' provinces must contain integers only"
                    )
                if item in province_owner:
                    other = province_owner[item]
                    raise TitleValidationError(
                        f"Province {item} is assigned to both '{other}' and '{title_id}'"
                    )
                province_owner[item] = title_id
                province_ids.append(item)
            entry["provinces"] = province_ids
        else:
            titles = raw_entry.get("titles")
            if not isinstance(titles, list):
                raise TitleValidationError(f"Title '{title_id}' requires a titles array")
            child_ids: list[str] = []
            for item in titles:
                child_id = str(item).strip()
                if not child_id:
                    raise TitleValidationError(f"Title '{title_id}' has an empty child id in titles")
                if child_id not in child_data:
                    raise TitleValidationError(
                        f"Title '{title_id}' references unknown {child_tier} '{child_id}'"
                    )
                if child_id in child_owner:
                    other = child_owner[child_id]
                    raise TitleValidationError(
                        f"{child_tier} '{child_id}' is assigned to both '{other}' and '{title_id}'"
                    )
                child_owner[child_id] = title_id
                child_ids.append(child_id)
            entry["titles"] = child_ids

        clean[title_id] = entry

    return clean
