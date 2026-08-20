from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
from PIL import Image

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from scripts.mapgen.geometry_cache import MapGeometryCache  # noqa: E402
from scripts.mapgen.zocgen import (  # noqa: E402
    build_zoc_overlay_image,
    generate_zoc_overlays,
    make_hatch_tile,
)
from scripts.util.zoc_paths import safe_fort_filename  # noqa: E402


class ZocGenTest(unittest.TestCase):
    def test_safe_fort_filename_rejects_unsafe_ids(self) -> None:
        self.assertEqual(safe_fort_filename("lanhold"), "lanhold")
        self.assertEqual(safe_fort_filename("lan-hold_2"), "lan-hold_2")
        self.assertIsNone(safe_fort_filename("../escape"))
        self.assertIsNone(safe_fort_filename(""))

    def test_build_zoc_overlay_image_masks_only_target_provinces(self) -> None:
        province_id_map = np.array(
            [
                [1, 1, 2],
                [1, 3, 2],
                [4, 4, 2],
            ],
            dtype=np.int32,
        )
        cache = MapGeometryCache(
            width=3,
            height=3,
            provinces_rgba=np.zeros((3, 3, 4), dtype=np.uint8),
            packed_rgb=np.zeros((3, 3), dtype=np.uint32),
            province_id_map=province_id_map,
            land_mask=np.ones((3, 3), dtype=bool),
            rgb_to_id={},
        )
        hatch = make_hatch_tile(size=4)

        img = build_zoc_overlay_image(cache, [1, 3], hatch)
        alpha = np.array(img.getchannel("A"))
        mask = np.isin(province_id_map, [1, 3])

        self.assertGreater(np.count_nonzero(alpha[mask]), 0)
        self.assertEqual(np.count_nonzero(alpha[~mask]), 0)
        img.close()

    def test_generate_zoc_overlays_writes_png_sidecar_and_cleans_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            markers_path = os.path.join(tmp, "map_markers.json")
            overlays_path = os.path.join(tmp, "zoc_overlays.json")
            zoc_out = os.path.join(tmp, "zoc")
            os.makedirs(zoc_out, exist_ok=True)

            stale_png = os.path.join(zoc_out, "removed.png")
            Image.new("RGBA", (4, 4), (0, 0, 0, 0)).save(stale_png)

            with open(markers_path, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "map_id": "main",
                        "forts": [
                            {
                                "id": "lanhold",
                                "zoc_provinces": [1],
                            }
                        ],
                    },
                    f,
                )

            province_id_map = np.array([[1, 2], [2, 2]], dtype=np.int32)
            cache = MapGeometryCache(
                width=2,
                height=2,
                provinces_rgba=np.zeros((2, 2, 4), dtype=np.uint8),
                packed_rgb=np.zeros((2, 2), dtype=np.uint32),
                province_id_map=province_id_map,
                land_mask=np.ones((2, 2), dtype=bool),
                rgb_to_id={},
            )

            def fake_input_file(map_name: str, filename: str) -> str:
                if filename == "map_markers.json":
                    return markers_path
                raise FileNotFoundError(filename)

            def fake_zoc_dir(map_name: str) -> str:
                return zoc_out

            def fake_zoc_image(map_name: str, fort_id: str) -> str:
                return os.path.join(zoc_out, f"{fort_id}.png")

            def fake_zoc_overlays_file(map_name: str) -> str:
                return overlays_path

            with mock.patch(
                "scripts.mapgen.zocgen.load_raw_markers",
                return_value={
                    "forts": [
                        {"id": "lanhold", "zoc_provinces": [1]},
                    ]
                },
            ), mock.patch(
                "scripts.mapgen.zocgen.zoc_dir",
                side_effect=fake_zoc_dir,
            ), mock.patch(
                "scripts.mapgen.zocgen.zoc_image",
                side_effect=fake_zoc_image,
            ), mock.patch(
                "scripts.mapgen.zocgen.zoc_overlays_file",
                side_effect=fake_zoc_overlays_file,
            ):
                metadata = generate_zoc_overlays("main", cache=cache)

            self.assertIn("lanhold", metadata)
            self.assertIn("overlay", metadata["lanhold"])
            self.assertTrue(os.path.isfile(os.path.join(zoc_out, "lanhold.png")))
            self.assertFalse(os.path.exists(stale_png))

            with open(overlays_path, encoding="utf-8") as f:
                sidecar = json.load(f)
            self.assertIn("lanhold", sidecar)

    def test_generate_zoc_overlays_skips_empty_zoc_provinces(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            overlays_path = os.path.join(tmp, "zoc_overlays.json")
            zoc_out = os.path.join(tmp, "zoc")
            os.makedirs(zoc_out, exist_ok=True)

            province_id_map = np.array([[1]], dtype=np.int32)
            cache = MapGeometryCache(
                width=1,
                height=1,
                provinces_rgba=np.zeros((1, 1, 4), dtype=np.uint8),
                packed_rgb=np.zeros((1, 1), dtype=np.uint32),
                province_id_map=province_id_map,
                land_mask=np.ones((1, 1), dtype=bool),
                rgb_to_id={},
            )

            with mock.patch(
                "scripts.mapgen.zocgen.load_raw_markers",
                return_value={
                    "forts": [{"id": "empty", "zoc_provinces": []}],
                },
            ), mock.patch(
                "scripts.mapgen.zocgen.zoc_dir",
                return_value=zoc_out,
            ), mock.patch(
                "scripts.mapgen.zocgen.zoc_overlays_file",
                return_value=overlays_path,
            ):
                metadata = generate_zoc_overlays("main", cache=cache)

            self.assertEqual(metadata, {})
            self.assertFalse(os.path.exists(os.path.join(zoc_out, "empty.png")))
            with open(overlays_path, encoding="utf-8") as f:
                self.assertEqual(json.load(f), {})


if __name__ == "__main__":
    unittest.main()
