import json
import os

from ..util.dirs import (
    defines_file,
    input_file,
    validate_map,
    zoc_image,
    zoc_overlays_file,
)
from ..util.zoc_paths import safe_fort_filename


def _empty_payload(map_name: str) -> dict:
    return {
        "map_id": map_name,
        "exported_at": None,
        "settlements": [],
        "installations": [],
        "forts": [],
    }


def load_raw_markers(map_name: str) -> dict:
    validate_map(map_name)
    path = input_file(map_name, "map_markers.json")
    if not os.path.exists(path):
        return _empty_payload(map_name)

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return _empty_payload(map_name)

    settlements = data.get("settlements")
    if not isinstance(settlements, list):
        settlements = []

    installations = data.get("installations")
    if not isinstance(installations, list):
        installations = []

    forts = data.get("forts")
    if not isinstance(forts, list):
        forts = []

    return {
        "map_id": data.get("map_id") or map_name,
        "exported_at": data.get("exported_at"),
        "settlement_large_population_threshold": data.get(
            "settlement_large_population_threshold"
        ),
        "settlements": settlements,
        "installations": installations,
        "forts": forts,
    }


def load_province_centroids(map_name: str) -> dict:
    validate_map(map_name)
    path = defines_file(map_name, "province_centroids.json")
    if not os.path.exists(path):
        return {}

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    return data if isinstance(data, dict) else {}


def _finite_int(value) -> int | None:
    if value is None:
        return None
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def world_coords_to_map_xy(center_x, center_z) -> tuple[int, int] | None:
    """Minecraft block X/Z map 1:1 to map pixel x/y (same as province lookup)."""
    x = _finite_int(center_x)
    z = _finite_int(center_z)
    if x is None or z is None:
        return None
    return x, z


def centroid_to_map_xy(centroid: dict) -> tuple[int, int] | None:
    if not isinstance(centroid, dict):
        return None
    x = _finite_int(centroid.get("x"))
    y = _finite_int(centroid.get("y"))
    if x is None or y is None:
        return None
    return x, y


def resolve_marker_map_xy(
    row: dict,
    centroids: dict,
) -> tuple[int, int] | None:
    world = world_coords_to_map_xy(row.get("center_x"), row.get("center_z"))
    if world is not None:
        return world

    province_id = row.get("province_id")
    if province_id is None:
        return None

    return centroid_to_map_xy(centroids.get(str(province_id), {}))


def resolve_settlement_map_xy(
    row: dict,
    centroids: dict,
) -> tuple[int, int] | None:
    return resolve_marker_map_xy(row, centroids)


def enrich_marker_rows(
    rows: list,
    centroids: dict,
) -> list[dict]:
    enriched: list[dict] = []
    for entry in rows:
        if not isinstance(entry, dict):
            continue

        row = dict(entry)
        map_xy = resolve_marker_map_xy(row, centroids)
        if map_xy is not None:
            row["map_x"], row["map_y"] = map_xy

        enriched.append(row)

    return enriched


def enrich_settlements(
    settlements: list,
    centroids: dict,
) -> list[dict]:
    return enrich_marker_rows(settlements, centroids)


def enrich_installations(
    installations: list,
    centroids: dict,
) -> list[dict]:
    return enrich_marker_rows(installations, centroids)


def load_zoc_overlays(map_name: str) -> dict:
    validate_map(map_name)
    path = zoc_overlays_file(map_name)
    if not os.path.exists(path):
        return {}

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    return data if isinstance(data, dict) else {}


def enrich_forts(
    forts: list,
    centroids: dict,
    overlays: dict,
    map_name: str,
) -> list[dict]:
    enriched: list[dict] = []
    for entry in forts:
        if not isinstance(entry, dict):
            continue

        row = dict(entry)
        fort_id = row.get("id")
        map_xy = resolve_marker_map_xy(row, centroids)
        if map_xy is not None:
            row["map_x"], row["map_y"] = map_xy

        if fort_id is not None:
            overlay_entry = overlays.get(str(fort_id))
            if isinstance(overlay_entry, dict) and isinstance(
                overlay_entry.get("overlay"), dict
            ):
                row["overlay"] = overlay_entry["overlay"]

            safe_id = safe_fort_filename(str(fort_id))
            if safe_id is not None and os.path.exists(zoc_image(map_name, safe_id)):
                row["zoc_url"] = f"/{map_name}/zoc/{safe_id}.png"

        enriched.append(row)

    return enriched


def build_markers_response(map_name: str) -> dict:
    raw = load_raw_markers(map_name)
    centroids = load_province_centroids(map_name)
    overlays = load_zoc_overlays(map_name)
    return {
        "map_id": raw["map_id"],
        "exported_at": raw["exported_at"],
        "settlement_large_population_threshold": raw.get(
            "settlement_large_population_threshold"
        ),
        "settlements": enrich_settlements(raw["settlements"], centroids),
        "installations": enrich_installations(raw["installations"], centroids),
        "forts": enrich_forts(raw["forts"], centroids, overlays, map_name),
    }
