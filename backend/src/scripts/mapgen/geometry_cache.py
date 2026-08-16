"""Per-regeneration cache for province geometry arrays."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..loader.provinces import load_provinces, load_province_terrains
from ..util.dirs import input_file, validate_map
from .map_paint_numpy import _pack_key, load_provinces_array, pack_rgb

SKIP_TERRAINS = {"water", "sea", ""}


@dataclass
class MapGeometryCache:
    width: int
    height: int
    provinces_rgba: np.ndarray
    packed_rgb: np.ndarray
    province_id_map: np.ndarray
    land_mask: np.ndarray
    rgb_to_id: dict[tuple[int, int, int], int]

    @classmethod
    def load(cls, map_name: str) -> MapGeometryCache:
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

        terrains = load_province_terrains(map_name)
        land_mask = np.zeros_like(province_id_map, dtype=bool)
        for province_id, terrain in terrains.items():
            if terrain not in SKIP_TERRAINS:
                land_mask[province_id_map == province_id] = True

        return cls(
            width=width,
            height=height,
            provinces_rgba=provinces_rgba,
            packed_rgb=packed_rgb,
            province_id_map=province_id_map,
            land_mask=land_mask,
            rgb_to_id=rgb_to_id,
        )
