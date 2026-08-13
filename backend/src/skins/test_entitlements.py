"""Unit tests for 3D pair budgets and entitlement resolution."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

_BACKEND_SRC = Path(__file__).resolve().parents[1]
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from skins.size_limits import SizeLimitError, assert_3d_pair_budgets  # noqa: E402
from skins.entitlements import (  # noqa: E402
    EMERGENCY_MAX_3D_PAIR_BYTES,
    catalog_entitlement_defaults,
    resolve_skin_entitlements,
)


class SizeLimitsTest(unittest.TestCase):
    def test_item_3d_ok(self) -> None:
        assert_3d_pair_budgets(
            "item_3d",
            {"texture": b"x" * 100, "model": b"y" * 100},
            30720,
        )

    def test_item_3d_over(self) -> None:
        with self.assertRaises(SizeLimitError) as ctx:
            assert_3d_pair_budgets(
                "item_3d",
                {"texture": b"x" * 20000, "model": b"y" * 20000},
                30720,
            )
        self.assertIn("40000", str(ctx.exception))
        self.assertIn("30720", str(ctx.exception))

    def test_gun_checks_each_model(self) -> None:
        tex = b"t" * 10000
        ok = b"m" * 1000
        over = b"m" * 25000
        with self.assertRaises(SizeLimitError) as ctx:
            assert_3d_pair_budgets(
                "gun",
                {
                    "texture": tex,
                    "carry_model": ok,
                    "reload_model": over,
                    "aim_model": ok,
                },
                30720,
            )
        self.assertIn("gun/reload_model", str(ctx.exception))

    def test_armor_helmet_tiers(self) -> None:
        with self.assertRaises(SizeLimitError):
            assert_3d_pair_budgets(
                "armor_set",
                {
                    "iron_helmet_texture": b"x" * 20000,
                    "iron_helmet_model": b"y" * 20000,
                },
                30720,
                helmet_3d_tiers=["iron"],
            )

    def test_handheld_noop(self) -> None:
        assert_3d_pair_budgets("handheld", {"texture": b"x" * 99999}, 1)


class EntitlementsTest(unittest.TestCase):
    def test_catalog_defaults(self) -> None:
        d = catalog_entitlement_defaults(
            {
                "entitlements": {
                    "defaults": {
                        "name_colour_stops": 0,
                        "max_3d_pair_bytes": 30720,
                    }
                }
            }
        )
        self.assertEqual(d["max_3d_pair_bytes"], 30720)
        self.assertEqual(d["name_colour_stops"], 0)

    def test_resolve_uses_meta(self) -> None:
        with mock.patch(
            "skins.entitlements.get_player_meta",
            return_value={"name_colour_stops": 2, "max_3d_pair_bytes": 40960},
        ), mock.patch(
            "skins.catalog.get_catalog",
            return_value={
                "entitlements": {
                    "defaults": {
                        "name_colour_stops": 0,
                        "max_3d_pair_bytes": 30720,
                    }
                }
            },
        ):
            out = resolve_skin_entitlements("abc", staff=False)
        self.assertEqual(out["name_colour_stops"], 2)
        self.assertEqual(out["max_3d_pair_bytes"], 40960)

    def test_resolve_staff_colour_cap(self) -> None:
        with mock.patch(
            "skins.entitlements.get_player_meta",
            return_value={"name_colour_stops": 1, "max_3d_pair_bytes": 30720},
        ), mock.patch(
            "skins.catalog.get_catalog",
            return_value={"entitlements": {"defaults": {}}},
        ):
            out = resolve_skin_entitlements("abc", staff=True)
        self.assertEqual(out["name_colour_stops"], 8)

    def test_resolve_emergency_pair(self) -> None:
        with mock.patch(
            "skins.entitlements.get_player_meta", return_value=None
        ), mock.patch(
            "skins.catalog.get_catalog",
            return_value={"entitlements": {"defaults": {"name_colour_stops": 0}}},
        ):
            out = resolve_skin_entitlements("abc", staff=False)
        self.assertEqual(out["max_3d_pair_bytes"], EMERGENCY_MAX_3D_PAIR_BYTES)


if __name__ == "__main__":
    unittest.main()
