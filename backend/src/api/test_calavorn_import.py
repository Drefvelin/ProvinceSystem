"""Fingerprint the committed Calavorn archive sources (not gitignored output)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from PIL import Image

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

ADAVAAR_PROVINCES_PNG_BYTES = 919_122

INPUT = _BACKEND_SRC / "input" / "calavorn"
DEFINES = _BACKEND_SRC / "defines" / "calavorn"


class CalavornImportTest(unittest.TestCase):
    def test_provinces_txt_is_calavorn(self) -> None:
        text = (DEFINES / "provinces.txt").read_text(encoding="utf-8")
        self.assertIn("Elvaris", text)

    def test_county_one_is_elvaris(self) -> None:
        county = json.loads((DEFINES / "county.json").read_text(encoding="utf-8"))
        self.assertEqual(county["COUNTY_1"]["name"], "Elvaris")

    def test_nation_json_has_rgb_and_provinces(self) -> None:
        nations = json.loads((INPUT / "nation.json").read_text(encoding="utf-8"))
        self.assertIsInstance(nations, dict)
        self.assertTrue(nations)
        for nation_id, data in nations.items():
            self.assertIsInstance(data, dict, nation_id)
            self.assertIsInstance(data.get("rgb"), str, nation_id)
            self.assertTrue(data["rgb"].strip(), nation_id)
            self.assertIsInstance(data.get("provinces"), list, nation_id)

    def test_province_and_map_pngs_match_and_are_not_adavaar(self) -> None:
        provinces_path = INPUT / "provinces.png"
        map_path = INPUT / "map.png"
        self.assertTrue(provinces_path.is_file())
        self.assertTrue(map_path.is_file())
        self.assertNotEqual(provinces_path.stat().st_size, ADAVAAR_PROVINCES_PNG_BYTES)
        with Image.open(provinces_path) as provinces, Image.open(map_path) as background:
            self.assertEqual(provinces.size, background.size)

    def test_geometry_json_exists(self) -> None:
        self.assertTrue((DEFINES / "province_neighbors.json").is_file())
        self.assertTrue((DEFINES / "province_centroids.json").is_file())
