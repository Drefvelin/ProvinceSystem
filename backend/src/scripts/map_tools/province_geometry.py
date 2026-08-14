"""Province neighbor graph and centroids from provinces.png (step 40.02)."""

from __future__ import annotations

import json
import os
import time
from collections import defaultdict

from PIL import Image

from ..loader.provinces import load_provinces
from ..util.dirs import defines_file, input_file, validate_map

BLACK = (0, 0, 0)
DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))


def scan_province_image(
    img: Image.Image,
    color_to_id: dict[tuple[int, int, int], int],
) -> tuple[dict[int, set[int]], dict[int, dict[str, float | int]]]:
    """Single-pass 4-connected neighbors + mean-pixel centroids."""
    rgb_img = img.convert("RGB")
    src = rgb_img.load()
    width, height = rgb_img.size

    neighbors: dict[int, set[int]] = defaultdict(set)
    accum: dict[int, list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])

    for y in range(height):
        for x in range(width):
            rgb = src[x, y]
            if rgb == BLACK:
                continue

            pid = color_to_id.get(rgb)
            if pid is None:
                continue

            bucket = accum[pid]
            bucket[0] += x
            bucket[1] += y
            bucket[2] += 1

            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= width or ny >= height:
                    continue
                nrgb = src[nx, ny]
                if nrgb == BLACK:
                    continue
                npid = color_to_id.get(nrgb)
                if npid is not None and npid != pid:
                    neighbors[pid].add(npid)

    centroids: dict[int, dict[str, float | int]] = {}
    for pid, (sum_x, sum_y, count) in accum.items():
        centroids[pid] = {
            "x": sum_x / count,
            "y": sum_y / count,
            "pixel_count": int(count),
        }

    return dict(neighbors), centroids


def validate_geometry(
    expected_ids: set[int],
    neighbors: dict[int, set[int]],
    centroids: dict[int, dict[str, float | int]],
) -> list[str]:
    """Return warning messages; raise ValueError on hard failures."""
    warnings: list[str] = []

    missing = expected_ids - set(centroids)
    if missing:
        raise ValueError(
            f"{len(missing)} provinces in provinces.txt missing from PNG centroids "
            f"(e.g. {sorted(missing)[:5]})"
        )

    extra = set(centroids) - expected_ids
    if extra:
        warnings.append(
            f"{len(extra)} province ids in PNG not listed in provinces.txt "
            f"(e.g. {sorted(extra)[:5]})"
        )

    for pid, nlist in neighbors.items():
        for other in nlist:
            if pid not in neighbors.get(other, set()):
                raise ValueError(
                    f"Asymmetric neighbor graph: {pid} -> {other} but not reverse"
                )

    return warnings


def serialize_neighbors(neighbors: dict[int, set[int]]) -> dict[str, list[int]]:
    return {str(pid): sorted(nlist) for pid, nlist in sorted(neighbors.items())}


def serialize_centroids(
    centroids: dict[int, dict[str, float | int]],
) -> dict[str, dict[str, float | int]]:
    return {str(pid): centroids[pid] for pid in sorted(centroids)}


def build_province_geometry(
    map_name: str,
) -> tuple[dict[int, set[int]], dict[int, dict[str, float | int]], list[str]]:
    validate_map(map_name)
    color_to_id = load_provinces(map_name)
    expected_ids = set(color_to_id.values())

    png_path = input_file(map_name, "provinces.png")
    if not os.path.exists(png_path):
        raise FileNotFoundError(f"provinces.png not found for map '{map_name}'")

    with Image.open(png_path) as img:
        neighbors, centroids = scan_province_image(img, color_to_id)

    warnings = validate_geometry(expected_ids, neighbors, centroids)
    return neighbors, centroids, warnings


def write_province_geometry(map_name: str) -> dict[str, int | float]:
    start = time.perf_counter()
    neighbors, centroids, warnings = build_province_geometry(map_name)

    for message in warnings:
        print(f"warning: {message}")

    neighbors_path = defines_file(map_name, "province_neighbors.json")
    centroids_path = defines_file(map_name, "province_centroids.json")
    os.makedirs(os.path.dirname(neighbors_path), exist_ok=True)

    with open(neighbors_path, "w", encoding="utf-8") as f:
        json.dump(serialize_neighbors(neighbors), f, indent=2)
        f.write("\n")

    with open(centroids_path, "w", encoding="utf-8") as f:
        json.dump(serialize_centroids(centroids), f, indent=2)
        f.write("\n")

    edge_count = sum(len(nlist) for nlist in neighbors.values()) // 2
    elapsed = time.perf_counter() - start

    print(f"Wrote {neighbors_path}")
    print(f"Wrote {centroids_path}")
    print(
        f"map={map_name} provinces={len(centroids)} "
        f"undirected_edges={edge_count} elapsed={elapsed:.2f}s"
    )

    return {
        "provinces": len(centroids),
        "edges": edge_count,
        "elapsed_s": elapsed,
    }
