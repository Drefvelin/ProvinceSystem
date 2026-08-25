"""Province neighbor graph and centroids from provinces.png (step 40.02)."""

from __future__ import annotations

import gzip
import json
import math
import os
import struct
import time
from collections import defaultdict, deque

from PIL import Image

from ..loader.provinces import load_provinces, load_province_terrains
from ..util.dirs import defines_file, input_file, validate_map

BLACK = (0, 0, 0)
DIRECTIONS = ((1, 0), (-1, 0), (0, 1), (0, -1))
LABEL_GRID_WIDTH = 512
LABEL_BRIDGE_MAX_PX = 50
WATER_TERRAINS = frozenset({"water", "sea"})


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


def _is_water_terrain(pid: int, id_to_terrain: dict[int, str]) -> bool:
    return id_to_terrain.get(pid, "") in WATER_TERRAINS


def _province_bboxes(
    grid: list[list[int]],
) -> dict[int, tuple[int, int, int, int]]:
    height = len(grid)
    width = len(grid[0]) if height else 0
    bboxes: dict[int, list[int]] = {}

    for y in range(height):
        for x in range(width):
            pid = grid[y][x]
            if pid <= 0:
                continue
            if pid not in bboxes:
                bboxes[pid] = [x, y, x, y]
            else:
                box = bboxes[pid]
                box[0] = min(box[0], x)
                box[1] = min(box[1], y)
                box[2] = max(box[2], x)
                box[3] = max(box[3], y)

    return {pid: (box[0], box[1], box[2], box[3]) for pid, box in bboxes.items()}


def _bbox_overlap(
    a: tuple[int, int, int, int],
    b: tuple[int, int, int, int],
) -> bool:
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def _expand_bbox(
    box: tuple[int, int, int, int],
    margin: int,
    width: int,
    height: int,
) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = box
    return (
        max(0, x0 - margin),
        max(0, y0 - margin),
        min(width - 1, x1 + margin),
        min(height - 1, y1 + margin),
    )


def _all_boundary_pixels(
    grid: list[list[int]],
) -> dict[int, list[tuple[int, int]]]:
    height = len(grid)
    width = len(grid[0]) if height else 0
    boundaries: dict[int, list[tuple[int, int]]] = defaultdict(list)

    for y in range(height):
        for x in range(width):
            pid = grid[y][x]
            if pid <= 0:
                continue
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= width or ny >= height:
                    boundaries[pid].append((x, y))
                    break
                if grid[ny][nx] != pid:
                    boundaries[pid].append((x, y))
                    break

    return dict(boundaries)


def _boundary_pixels_for_province(
    boundaries: dict[int, list[tuple[int, int]]],
    province_id: int,
) -> list[tuple[int, int]]:
    return boundaries.get(province_id, [])


def build_bridge_grid(
    img: Image.Image,
    color_to_id: dict[tuple[int, int, int], int],
    id_to_terrain: dict[int, str],
    grid_width: int = LABEL_GRID_WIDTH,
) -> tuple[list[list[int]], int]:
    """Downsample provinces.png for label-bridge search (0 = crossable sea/water)."""
    rgb_img = img.convert("RGB")
    map_width, map_height = rgb_img.size
    grid_height = max(1, round(map_height * grid_width / map_width))
    src = rgb_img.load()

    grid: list[list[int]] = [[0] * grid_width for _ in range(grid_height)]
    for gy in range(grid_height):
        y0 = int(gy * map_height / grid_height)
        y1 = int((gy + 1) * map_height / grid_height)
        if y1 <= y0:
            y1 = min(y0 + 1, map_height)
        for gx in range(grid_width):
            x0 = int(gx * map_width / grid_width)
            x1 = int((gx + 1) * map_width / grid_width)
            if x1 <= x0:
                x1 = min(x0 + 1, map_width)

            counts: dict[int, int] = defaultdict(int)
            for y in range(y0, y1):
                for x in range(x0, x1):
                    rgb = src[x, y]
                    if rgb == BLACK:
                        continue
                    pid = color_to_id.get(rgb)
                    if pid is None:
                        continue
                    if _is_water_terrain(pid, id_to_terrain):
                        continue
                    counts[pid] += 1

            if counts:
                grid[gy][gx] = max(counts, key=counts.get)

    max_steps = max(1, math.ceil(LABEL_BRIDGE_MAX_PX * grid_width / map_width))
    return grid, max_steps


def _find_water_bridges_for_province(
    grid: list[list[int]],
    source_id: int,
    boundary: list[tuple[int, int]],
    search_box: tuple[int, int, int, int],
    candidate_ids: set[int],
    max_steps: int,
) -> set[int]:
    x0, y0, x1, y1 = search_box
    if not boundary:
        return set()

    best: dict[tuple[int, int], int] = {}
    queue: deque[tuple[int, int]] = deque()

    for bx, by in boundary:
        if bx < x0 or bx > x1 or by < y0 or by > y1:
            continue
        key = (bx, by)
        best[key] = 0
        queue.append(key)

    if not queue:
        return set()

    found: set[int] = set()

    while queue:
        x, y = queue.popleft()
        steps = best[(x, y)]
        if steps >= max_steps:
            continue

        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if nx < x0 or nx > x1 or ny < y0 or ny > y1:
                continue

            neighbor_pid = grid[ny][nx]
            if neighbor_pid > 0 and neighbor_pid != source_id:
                if neighbor_pid in candidate_ids:
                    found.add(neighbor_pid)
                continue

            if neighbor_pid != 0:
                continue

            key = (nx, ny)
            next_steps = steps + 1
            if next_steps > max_steps:
                continue
            if next_steps >= best.get(key, max_steps + 1):
                continue

            best[key] = next_steps
            queue.append(key)

    return found


def build_label_neighbors(
    bridge_grid: list[list[int]],
    max_steps: int,
    strict_neighbors: dict[int, set[int]],
) -> dict[int, set[int]]:
    """Label-neighbor graph: strict adjacency plus water bridges on coarse grid."""
    label_neighbors: dict[int, set[int]] = {
        pid: set(nlist) for pid, nlist in strict_neighbors.items()
    }

    height = len(bridge_grid)
    width = len(bridge_grid[0]) if height else 0
    if width == 0 or height == 0:
        return label_neighbors

    bboxes = _province_bboxes(bridge_grid)
    boundaries = _all_boundary_pixels(bridge_grid)
    province_ids = sorted(bboxes)

    for source_id in province_ids:
        expanded = _expand_bbox(bboxes[source_id], max_steps, width, height)
        candidates = {
            other_id
            for other_id in province_ids
            if other_id != source_id
            and _bbox_overlap(expanded, bboxes[other_id])
            and other_id not in label_neighbors.get(source_id, set())
        }
        if not candidates:
            continue

        bridges = _find_water_bridges_for_province(
            bridge_grid,
            source_id,
            _boundary_pixels_for_province(boundaries, source_id),
            expanded,
            candidates,
            max_steps,
        )
        for other_id in bridges:
            label_neighbors.setdefault(source_id, set()).add(other_id)
            label_neighbors.setdefault(other_id, set()).add(source_id)

    for pid in province_ids:
        label_neighbors.setdefault(pid, set())

    return label_neighbors


def validate_label_neighbors(
    expected_ids: set[int],
    strict_neighbors: dict[int, set[int]],
    label_neighbors: dict[int, set[int]],
) -> list[str]:
    """Return warnings; raise ValueError on hard failures."""
    warnings: list[str] = []

    for pid, nlist in label_neighbors.items():
        if pid in nlist:
            raise ValueError(f"Label neighbor self-loop: {pid}")
        for other in nlist:
            if pid not in label_neighbors.get(other, set()):
                raise ValueError(
                    f"Asymmetric label neighbor graph: {pid} -> {other} but not reverse"
                )
            if other not in expected_ids:
                raise ValueError(
                    f"Label neighbor references unknown province id: {other}"
                )

    for pid, nlist in strict_neighbors.items():
        label_set = label_neighbors.get(pid, set())
        missing = nlist - label_set
        if missing:
            raise ValueError(
                f"Label neighbors missing strict edges for {pid}: {sorted(missing)[:5]}"
            )

    strict_edge_count = sum(len(nlist) for nlist in strict_neighbors.values()) // 2
    label_edge_count = sum(len(nlist) for nlist in label_neighbors.values()) // 2
    bridge_edges = label_edge_count - strict_edge_count
    if bridge_edges > 0:
        warnings.append(
            f"Added {bridge_edges} water-bridge label edges "
            f"({strict_edge_count} strict -> {label_edge_count} label)"
        )

    return warnings


def serialize_neighbors(neighbors: dict[int, set[int]]) -> dict[str, list[int]]:
    return {str(pid): sorted(nlist) for pid, nlist in sorted(neighbors.items())}


def serialize_centroids(
    centroids: dict[int, dict[str, float | int]],
) -> dict[str, dict[str, float | int]]:
    return {str(pid): centroids[pid] for pid in sorted(centroids)}


def build_label_grid(
    img: Image.Image,
    color_to_id: dict[tuple[int, int, int], int],
    id_to_terrain: dict[int, str] | None = None,
    grid_width: int = LABEL_GRID_WIDTH,
) -> tuple[list[int], dict[str, int]]:
    """Downsample provinces.png to dominant province id per cell (0 = sea/water)."""
    rgb_img = img.convert("RGB")
    map_width, map_height = rgb_img.size
    grid_height = max(1, round(map_height * grid_width / map_width))
    src = rgb_img.load()

    cells: list[int] = []
    for gy in range(grid_height):
        y0 = int(gy * map_height / grid_height)
        y1 = int((gy + 1) * map_height / grid_height)
        if y1 <= y0:
            y1 = min(y0 + 1, map_height)
        for gx in range(grid_width):
            x0 = int(gx * map_width / grid_width)
            x1 = int((gx + 1) * map_width / grid_width)
            if x1 <= x0:
                x1 = min(x0 + 1, map_width)

            counts: dict[int, int] = defaultdict(int)
            for y in range(y0, y1):
                for x in range(x0, x1):
                    rgb = src[x, y]
                    if rgb == BLACK:
                        continue
                    pid = color_to_id.get(rgb)
                    if pid is None:
                        continue
                    if id_to_terrain and _is_water_terrain(pid, id_to_terrain):
                        continue
                    counts[pid] += 1

            if not counts:
                cells.append(0)
            else:
                cells.append(max(counts, key=counts.get))

    meta = {
        "mapWidth": map_width,
        "mapHeight": map_height,
        "gridWidth": grid_width,
        "gridHeight": grid_height,
    }
    return cells, meta


def write_label_grid_files(
    map_name: str,
    cells: list[int],
    meta: dict[str, int],
) -> None:
    grid_path = defines_file(map_name, "province_label_grid.bin.gz")
    meta_path = defines_file(map_name, "province_label_grid.json")
    os.makedirs(os.path.dirname(grid_path), exist_ok=True)

    packed = struct.pack(f"<{len(cells)}H", *cells)
    with gzip.open(grid_path, "wb") as f:
        f.write(packed)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")


def build_province_geometry(
    map_name: str,
) -> tuple[
    dict[int, set[int]],
    dict[int, set[int]],
    dict[int, dict[str, float | int]],
    list[str],
    list[int],
    dict[str, int],
]:
    validate_map(map_name)
    color_to_id = load_provinces(map_name)
    id_to_terrain = load_province_terrains(map_name)
    expected_ids = set(color_to_id.values())

    png_path = input_file(map_name, "provinces.png")
    if not os.path.exists(png_path):
        raise FileNotFoundError(f"provinces.png not found for map '{map_name}'")

    with Image.open(png_path) as img:
        neighbors, centroids = scan_province_image(img, color_to_id)
        bridge_grid, max_steps = build_bridge_grid(img, color_to_id, id_to_terrain)
        label_neighbors = build_label_neighbors(bridge_grid, max_steps, neighbors)
        grid_cells, grid_meta = build_label_grid(img, color_to_id, id_to_terrain)

    warnings = validate_geometry(expected_ids, neighbors, centroids)
    warnings.extend(
        validate_label_neighbors(expected_ids, neighbors, label_neighbors)
    )
    return neighbors, label_neighbors, centroids, warnings, grid_cells, grid_meta


def write_province_geometry(map_name: str) -> dict[str, int | float]:
    start = time.perf_counter()
    neighbors, label_neighbors, centroids, warnings, grid_cells, grid_meta = (
        build_province_geometry(map_name)
    )

    for message in warnings:
        print(f"warning: {message}")

    neighbors_path = defines_file(map_name, "province_neighbors.json")
    label_neighbors_path = defines_file(map_name, "province_label_neighbors.json")
    centroids_path = defines_file(map_name, "province_centroids.json")
    os.makedirs(os.path.dirname(neighbors_path), exist_ok=True)

    with open(neighbors_path, "w", encoding="utf-8") as f:
        json.dump(serialize_neighbors(neighbors), f, indent=2)
        f.write("\n")

    with open(label_neighbors_path, "w", encoding="utf-8") as f:
        json.dump(serialize_neighbors(label_neighbors), f, indent=2)
        f.write("\n")

    with open(centroids_path, "w", encoding="utf-8") as f:
        json.dump(serialize_centroids(centroids), f, indent=2)
        f.write("\n")

    write_label_grid_files(map_name, grid_cells, grid_meta)
    grid_path = defines_file(map_name, "province_label_grid.bin.gz")
    meta_path = defines_file(map_name, "province_label_grid.json")

    edge_count = sum(len(nlist) for nlist in neighbors.values()) // 2
    label_edge_count = sum(len(nlist) for nlist in label_neighbors.values()) // 2
    elapsed = time.perf_counter() - start

    print(f"Wrote {neighbors_path}")
    print(f"Wrote {label_neighbors_path}")
    print(f"Wrote {centroids_path}")
    print(f"Wrote {meta_path}")
    print(f"Wrote {grid_path}")
    print(
        f"map={map_name} provinces={len(centroids)} "
        f"grid={grid_meta['gridWidth']}x{grid_meta['gridHeight']} "
        f"strict_edges={edge_count} label_edges={label_edge_count} "
        f"elapsed={elapsed:.2f}s"
    )

    return {
        "provinces": len(centroids),
        "edges": edge_count,
        "label_edges": label_edge_count,
        "grid_cells": len(grid_cells),
        "elapsed_s": elapsed,
    }
