import json
import os

from ..util.dirs import defines_file, input_file, validate_map


def _empty_payload(map_name: str) -> dict:
    return {
        "map_id": map_name,
        "exported_at": None,
        "settlements": [],
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

    return {
        "map_id": data.get("map_id") or map_name,
        "exported_at": data.get("exported_at"),
        "settlement_large_population_threshold": data.get(
            "settlement_large_population_threshold"
        ),
        "settlements": settlements,
    }


def load_province_centroids(map_name: str) -> dict:
    validate_map(map_name)
    path = defines_file(map_name, "province_centroids.json")
    if not os.path.exists(path):
        return {}

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    return data if isinstance(data, dict) else {}


def enrich_settlements(
    settlements: list,
    centroids: dict,
) -> list[dict]:
    enriched: list[dict] = []
    for entry in settlements:
        if not isinstance(entry, dict):
            continue

        row = dict(entry)
        province_id = row.get("province_id")
        if province_id is None:
            enriched.append(row)
            continue

        centroid = centroids.get(str(province_id))
        if isinstance(centroid, dict):
            if "x" in centroid:
                row["map_x"] = int(round(float(centroid["x"])))
            if "y" in centroid:
                row["map_y"] = int(round(float(centroid["y"])))

        enriched.append(row)

    return enriched


def build_markers_response(map_name: str) -> dict:
    raw = load_raw_markers(map_name)
    centroids = load_province_centroids(map_name)
    return {
        "map_id": raw["map_id"],
        "exported_at": raw["exported_at"],
        "settlement_large_population_threshold": raw.get(
            "settlement_large_population_threshold"
        ),
        "settlements": enrich_settlements(raw["settlements"], centroids),
    }
