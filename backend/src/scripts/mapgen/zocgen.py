"""Per-fort ZOC hatch overlay generation from map_markers forts[]."""

from __future__ import annotations

import argparse
import json
import os
import sys

import numpy as np
from PIL import Image

from ..loader.markers import load_raw_markers
from ..util.dirs import (
    validate_map,
    zoc_dir,
    zoc_hatch_asset,
    zoc_image,
    zoc_overlays_file,
)
from ..util.overlay_metadata import save_cropped
from ..util.zoc_paths import safe_fort_filename
from .geometry_cache import MapGeometryCache

_HATCH_SIZE = 80
_HATCH_LINE_WIDTH = 32
_HATCH_GAP = 48
_HATCH_COLOR = (210, 35, 45, 210)


def make_hatch_tile(size: int = _HATCH_SIZE) -> np.ndarray:
    """Tileable diagonal hatch BL→TR with transparent gaps."""
    tile = np.zeros((size, size, 4), dtype=np.uint8)
    period = _HATCH_LINE_WIDTH + _HATCH_GAP
    for y in range(size):
        for x in range(size):
            if (x + y) % period < _HATCH_LINE_WIDTH:
                tile[y, x] = _HATCH_COLOR
    return tile


def load_hatch_tile() -> np.ndarray:
    path = zoc_hatch_asset()
    if os.path.isfile(path):
        with Image.open(path) as img:
            rgba = np.array(img.convert("RGBA"), dtype=np.uint8)
        if rgba.ndim == 3 and rgba.shape[2] == 4:
            return rgba
    return make_hatch_tile()


def _parse_zoc_provinces(raw: object) -> list[int]:
    if not isinstance(raw, list):
        return []
    ids: list[int] = []
    for item in raw:
        try:
            ids.append(int(item))
        except (TypeError, ValueError):
            continue
    return ids


def build_zoc_overlay_image(
    cache: MapGeometryCache,
    zoc_province_ids: list[int],
    hatch_rgba: np.ndarray,
) -> Image.Image:
    height, width = cache.height, cache.width
    tile_h, tile_w = hatch_rgba.shape[:2]

    zoc_ids = np.asarray(zoc_province_ids, dtype=cache.province_id_map.dtype)
    mask = np.isin(cache.province_id_map, zoc_ids)

    y_idx, x_idx = np.indices((height, width))
    tiled = hatch_rgba[y_idx % tile_h, x_idx % tile_w]

    overlay = np.zeros((height, width, 4), dtype=np.uint8)
    overlay[mask] = tiled[mask]
    return Image.fromarray(overlay, mode="RGBA")


def _cleanup_stale_zoc_pngs(map_name: str, current_safe_ids: set[str]) -> None:
    out_dir = zoc_dir(map_name)
    if not os.path.isdir(out_dir):
        return
    for filename in os.listdir(out_dir):
        if not filename.endswith(".png"):
            continue
        stem = filename[:-4]
        if stem not in current_safe_ids:
            os.remove(os.path.join(out_dir, filename))


def generate_zoc_overlays(
    map_name: str,
    *,
    cache: MapGeometryCache | None = None,
) -> dict[str, dict]:
    validate_map(map_name)
    raw = load_raw_markers(map_name)
    forts = raw.get("forts") or []
    if not isinstance(forts, list):
        forts = []

    owns_cache = cache is None
    if owns_cache:
        cache = MapGeometryCache.load(map_name)

    hatch = load_hatch_tile()
    os.makedirs(zoc_dir(map_name), exist_ok=True)

    metadata: dict[str, dict] = {}
    current_safe_ids: set[str] = set()

    for entry in forts:
        if not isinstance(entry, dict):
            continue
        fort_id = entry.get("id")
        safe_id = safe_fort_filename(str(fort_id) if fort_id is not None else "")
        if safe_id is None:
            continue

        zoc_ids = _parse_zoc_provinces(entry.get("zoc_provinces"))
        if not zoc_ids:
            continue

        current_safe_ids.add(safe_id)
        overlay_img = build_zoc_overlay_image(cache, zoc_ids, hatch)
        png_path = zoc_image(map_name, safe_id)
        overlay_meta = save_cropped(overlay_img, png_path, pad=2)
        overlay_img.close()
        if overlay_meta is None:
            continue

        metadata[str(fort_id)] = {"overlay": overlay_meta}

    _cleanup_stale_zoc_pngs(map_name, current_safe_ids)

    overlays_path = zoc_overlays_file(map_name)
    os.makedirs(os.path.dirname(overlays_path), exist_ok=True)
    with open(overlays_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"ZOC overlays generated for {len(metadata)} fort(s) on '{map_name}'")
    return metadata


def _write_hatch_asset() -> None:
    path = zoc_hatch_asset()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tile = make_hatch_tile()
    Image.fromarray(tile, mode="RGBA").save(path, "PNG")
    print(f"Wrote hatch tile to {path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate per-fort ZOC hatch overlays")
    parser.add_argument("--map", required=True, help="Map name (e.g. main)")
    parser.add_argument(
        "--write-hatch-asset",
        action="store_true",
        help="Write procedural hatch tile to assets/map/zoc_hatch.png",
    )
    args = parser.parse_args(argv)

    if args.write_hatch_asset:
        _write_hatch_asset()

    generate_zoc_overlays(args.map)
    return 0


if __name__ == "__main__":
    sys.exit(main())
