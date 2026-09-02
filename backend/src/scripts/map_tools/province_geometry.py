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
CROSSABLE_WATER_TERRAINS = frozenset({"water"})


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


def _is_crossable_water_terrain(pid: int, id_to_terrain: dict[int, str]) -> bool:
    return id_to_terrain.get(pid, "") in CROSSABLE_WATER_TERRAINS


def _bridge_cell_traversable(pid: int, id_to_terrain: dict[int, str]) -> bool:
    if pid == 0:
        return True
    return _is_crossable_water_terrain(pid, id_to_terrain)


def _is_land_bridge_cell(pid: int, id_to_terrain: dict[int, str]) -> bool:
    return pid > 0 and not _is_crossable_water_terrain(pid, id_to_terrain)


def build_bridge_grid(
    img: Image.Image,
    color_to_id: dict[tuple[int, int, int], int],
    id_to_terrain: dict[int, str],
    grid_width: int = LABEL_GRID_WIDTH,
) -> list[list[int]]:
    """Downsample provinces.png for label-bridge search.

    Land (incl. sea) keeps its province id; pure-water cells store the dominant
    water province id; black-only cells stay 0. Traversable regions for label
    bridging are 0 and inland water provinces.
    """
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

            land_counts: dict[int, int] = defaultdict(int)
            water_counts: dict[int, int] = defaultdict(int)
            for y in range(y0, y1):
                for x in range(x0, x1):
                    rgb = src[x, y]
                    if rgb == BLACK:
                        continue
                    pid = color_to_id.get(rgb)
                    if pid is None:
                        continue
                    if _is_crossable_water_terrain(pid, id_to_terrain):
                        water_counts[pid] += 1
                    else:
                        land_counts[pid] += 1

            if land_counts:
                grid[gy][gx] = max(land_counts, key=land_counts.get)
            elif water_counts:
                grid[gy][gx] = max(water_counts, key=water_counts.get)

    return grid


def _flood_traversable_regions(
    grid: list[list[int]],
    id_to_terrain: dict[int, str],
) -> list[list[int]]:
    height = len(grid)
    width = len(grid[0]) if height else 0
    regions = [[-1] * width for _ in range(height)]
    next_region = 0

    for y in range(height):
        for x in range(width):
            if regions[y][x] != -1:
                continue
            pid = grid[y][x]
            if not _bridge_cell_traversable(pid, id_to_terrain):
                continue

            region_id = next_region
            next_region += 1
            queue: deque[tuple[int, int]] = deque([(x, y)])
            regions[y][x] = region_id

            while queue:
                cx, cy = queue.popleft()
                for dx, dy in DIRECTIONS:
                    nx, ny = cx + dx, cy + dy
                    if nx < 0 or ny < 0 or nx >= width or ny >= height:
                        continue
                    if regions[ny][nx] != -1:
                        continue
                    npid = grid[ny][nx]
                    if not _bridge_cell_traversable(npid, id_to_terrain):
                        continue
                    regions[ny][nx] = region_id
                    queue.append((nx, ny))

    return regions


def _add_traversable_region_bridges(
    bridge_grid: list[list[int]],
    id_to_terrain: dict[int, str],
    label_neighbors: dict[int, set[int]],
) -> None:
    height = len(bridge_grid)
    width = len(bridge_grid[0]) if height else 0
    if width == 0 or height == 0:
        return

    regions = _flood_traversable_regions(bridge_grid, id_to_terrain)
    province_regions: dict[int, set[int]] = defaultdict(set)

    for y in range(height):
        for x in range(width):
            pid = bridge_grid[y][x]
            if not _is_land_bridge_cell(pid, id_to_terrain):
                continue
            for dx, dy in DIRECTIONS:
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= width or ny >= height:
                    continue
                region_id = regions[ny][nx]
                if region_id < 0:
                    continue
                province_regions[pid].add(region_id)

    region_provinces: dict[int, set[int]] = defaultdict(set)
    for pid, region_ids in province_regions.items():
        for region_id in region_ids:
            region_provinces[region_id].add(pid)

    for pids in region_provinces.values():
        sorted_pids = sorted(pids)
        for i, source_id in enumerate(sorted_pids):
            for other_id in sorted_pids[i + 1 :]:
                label_neighbors.setdefault(source_id, set()).add(other_id)
                label_neighbors.setdefault(other_id, set()).add(source_id)


def build_label_neighbors(
    bridge_grid: list[list[int]],
    id_to_terrain: dict[int, str],
    strict_neighbors: dict[int, set[int]],
) -> dict[int, set[int]]:
    """Label-neighbor graph: strict adjacency plus bridges across inland water and black gaps."""
    label_neighbors: dict[int, set[int]] = {
        pid: set(nlist) for pid, nlist in strict_neighbors.items()
    }

    _add_traversable_region_bridges(bridge_grid, id_to_terrain, label_neighbors)

    for pid in strict_neighbors:
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
            f"Added {bridge_edges} traversable-bridge label edges "
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
    """Downsample provinces.png to dominant province id per cell (0 = inland water / black gaps)."""
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
                    if id_to_terrain and _is_crossable_water_terrain(pid, id_to_terrain):
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
        bridge_grid = build_bridge_grid(img, color_to_id, id_to_terrain)
        label_neighbors = build_label_neighbors(bridge_grid, id_to_terrain, neighbors)
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
