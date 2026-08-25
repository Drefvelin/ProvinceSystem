"""Unit tests for pack_models builders."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

# Allow `python path/to/test_pack_models.py` from anywhere.
_BACKEND_SRC = Path(__file__).resolve().parents[2]
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from skins.pack_models.large_bow import build_large_bow_model  # noqa: E402
from skins.pack_models.large_handheld import (  # noqa: E402
    build_large_handheld_model,
    first_person_y,
)
from skins.pack_models.shield import build_shield_models  # noqa: E402
from skins.pack_models.textures import normalize_textures  # noqa: E402


class TextureNormalizeTests(unittest.TestCase):
    def test_rewrites_all_texture_strings(self) -> None:
        model = {
            "textures": {"0": "foo", "particle": "bar", "layer0": "baz"},
            "elements": [],
        }
        out = normalize_textures(model, "my_slug")
        for v in out["textures"].values():
            self.assertEqual(v, "tfmc_submissions:item/my_slug")

    def test_empty_textures_gets_defaults(self) -> None:
        out = normalize_textures({"elements": []}, "x")
        self.assertEqual(out["textures"]["0"], "tfmc_submissions:item/x")
        self.assertEqual(out["textures"]["particle"], "tfmc_submissions:item/x")


class ShieldBlockingTests(unittest.TestCase):
    def test_blue_like_idle_lands_on_classic_blocking(self) -> None:
        idle = {
            "textures": {"0": "placeholder"},
            "elements": [],
            "display": {
                "thirdperson_righthand": {
                    "rotation": [0, -90, 0],
                    "translation": [2, -2, 1],
                    "scale": [1.01, 1.01, 1.01],
                },
                "thirdperson_lefthand": {
                    "rotation": [0, -90, 0],
                    "translation": [2, -2, 2],
                    "scale": [1.01, 1.01, 1.01],
                },
                "firstperson_righthand": {
                    "translation": [-3, 0, 4],
                    "scale": [0.78, 0.78, 0.78],
                },
                "firstperson_lefthand": {
                    "translation": [-3, 0, 4],
                    "scale": [0.78, 0.78, 0.78],
                },
            },
        }
        idle_out, blocking = build_shield_models(idle, "blue_shield")
        self.assertEqual(
            idle_out["overrides"][0]["model"],
            "tfmc_submissions:item/blue_shield_blocking",
        )
        self.assertNotIn("overrides", blocking)
        rh = blocking["display"]["thirdperson_righthand"]
        self.assertEqual(rh["rotation"], [30.0, -35.0, 0.0])
        self.assertEqual(rh["translation"], [1.0, -1.0, -1.0])
        self.assertEqual(rh["scale"], [1.01, 1.01, 1.01])
        lh = blocking["display"]["thirdperson_lefthand"]
        self.assertEqual(lh["rotation"], [30.0, -35.0, 0.0])
        self.assertEqual(lh["translation"], [1.0, -1.0, -1.0])
        fp = blocking["display"]["firstperson_righthand"]
        self.assertEqual(fp["rotation"], [10.0, 0.0, 15.0])
        self.assertEqual(fp["translation"], [-3.0, 0.0, 1.0])

    def test_draganholt_yaw_accounts_for_kite_axis(self) -> None:
        idle = {
            "textures": {"0": "placeholder"},
            "elements": [],
            "display": {
                "thirdperson_righthand": {
                    "rotation": [0, 180, 0],
                    "translation": [1.25, -3, 2.75],
                    "scale": [1.3, 1.3, 1.3],
                },
                "thirdperson_lefthand": {
                    "translation": [0.75, -2.5, 2.25],
                    "scale": [1.3, 1.3, 1.3],
                },
            },
        }
        _, blocking = build_shield_models(idle, "draganholt_shield")
        rh = blocking["display"]["thirdperson_righthand"]
        self.assertEqual(rh["rotation"], [30.0, 235.0, 0.0])
        self.assertEqual(rh["scale"], [1.3, 1.3, 1.3])
        self.assertEqual(rh["translation"], [0.25, -2.0, 0.75])


class LargeHandheldTests(unittest.TestCase):
    def test_grip_4_golden(self) -> None:
        model = build_large_handheld_model("test_spear", 4.0)
        self.assertEqual(model["parent"], "minecraft:item/handheld")
        self.assertEqual(
            model["textures"]["layer0"], "tfmc_submissions:item/test_spear"
        )
        tp = model["display"]["thirdperson_righthand"]
        self.assertEqual(tp["rotation"], [0, -90, 55])
        self.assertEqual(tp["translation"], [0, 4.0, 0.5])
        self.assertEqual(tp["scale"], [1.5, 1.5, 1.5])
        fp_y = first_person_y(4.0)
        self.assertAlmostEqual(fp_y, 5.2, places=5)
        fp = model["display"]["firstperson_righthand"]
        self.assertEqual(fp["translation"][1], 5.2)


class LargeBowTests(unittest.TestCase):
    def test_locked_display_and_texture(self) -> None:
        model = build_large_bow_model("longbow", "pull_1")
        self.assertEqual(model["parent"], "minecraft:item/bow")
        self.assertEqual(
            model["textures"]["layer0"], "tfmc_submissions:item/longbow_1"
        )
        rh = model["display"]["thirdperson_righthand"]
        self.assertEqual(rh["scale"], [1.8, 1.8, 0.9])
        self.assertEqual(rh["translation"], [-1, -2, 5.8])


if __name__ == "__main__":
    unittest.main()
