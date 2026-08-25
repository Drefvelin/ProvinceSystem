"""Province ID grid: build from provinces.png, serialize for SimpleFactions Input."""

from __future__ import annotations

import gzip
import os
import struct

import numpy as np

from .loader.provinces import load_provinces
from .mapgen.map_paint_numpy import _pack_key, load_provinces_array, pack_rgb
from .util.dirs import defines_file, input_file, validate_map

GRID_FILENAME = "province_id_grid.bin.gz"
HEADER_SIZE = 8  # width + height as int32 LE


def build_province_id_map(map_name: str) -> tuple[int, int, np.ndarray]:
    """
    Build uint16 province id grid from provinces.png + provinces.txt.

    Returns (width, height, ids) where ids.shape == (height, width).
    Pixel value 0 = no province (black or unknown RGB).
    """
    validate_map(map_name)

    provinces_path = input_file(map_name, "provinces.png")
    provinces_rgba = load_provinces_array(provinces_path)
    height, width = provinces_rgba.shape[:2]

    rgb_to_id = load_provinces(map_name)
    packed_rgb = pack_rgb(provinces_rgba[:, :, :3])

    id_lut = np.zeros(1 << 24, dtype=np.uint16)
    for rgb, province_id in rgb_to_id.items():
        id_lut[_pack_key(rgb)] = province_id
    province_id_map = id_lut[packed_rgb]

    return width, height, province_id_map


def serialize_province_id_grid(width: int, height: int, ids: np.ndarray) -> bytes:
    """Pack grid to bytes: header + row-major uint16 body."""
    if ids.shape != (height, width):
        raise ValueError(
            f"ids shape {ids.shape} does not match height={height}, width={width}"
        )
    header = struct.pack("<ii", width, height)
    body = ids.astype("<u2", copy=False).tobytes()
    return header + body


def deserialize_province_id_grid(data: bytes) -> tuple[int, int, np.ndarray]:
    """Unpack bytes written by serialize_province_id_grid."""
    if len(data) < HEADER_SIZE:
        raise ValueError("province id grid data too short for header")

    width, height = struct.unpack("<ii", data[:HEADER_SIZE])
    if width <= 0 or height <= 0:
        raise ValueError(f"invalid grid dimensions: {width}x{height}")

    expected_body = width * height * 2
    body = data[HEADER_SIZE:]
    if len(body) != expected_body:
        raise ValueError(
            f"body length {len(body)} != expected {expected_body} for {width}x{height}"
        )

    ids = np.frombuffer(body, dtype="<u2").reshape(height, width)
    return width, height, ids.copy()


def write_province_id_grid_file(map_name: str, dest: str | None = None) -> str:
    """Write defines/{map}/province_id_grid.bin.gz unless dest is set."""
    width, height, ids = build_province_id_map(map_name)
    out_path = dest or defines_file(map_name, GRID_FILENAME)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    payload = serialize_province_id_grid(width, height, ids)
    with gzip.open(out_path, "wb") as f:
        f.write(payload)

    return out_path


def read_province_id_grid_file(path: str) -> tuple[int, int, np.ndarray]:
    """Read a gzip province id grid file."""
    with gzip.open(path, "rb") as f:
        data = f.read()
    return deserialize_province_id_grid(data)


def lookup_at(ids: np.ndarray, width: int, x: int, z: int) -> int:
    """Bounds-safe lookup; (x, z) is Minecraft block coords (z = image row)."""
    if x < 0 or z < 0 or x >= width or z >= ids.shape[0]:
        return 0
    return int(ids[z, x])
