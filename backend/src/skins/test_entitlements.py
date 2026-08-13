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
    can_mint_skin_token,
    catalog_entitlement_defaults,
    resolve_skin_entitlements,
)
from skins.catalog import _normalize_entitlements  # noqa: E402


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
                        "skin_token_cooldown_days": -1,
                        "skin_kinds": [],
                        "allow_armor_3d_helmet": False,
                    }
                }
            }
        )
        self.assertEqual(d["max_3d_pair_bytes"], 30720)
        self.assertEqual(d["name_colour_stops"], 0)
        self.assertEqual(d["skin_token_cooldown_days"], -1)
        self.assertEqual(d["skin_kinds"], [])
        self.assertFalse(d["allow_armor_3d_helmet"])

    def test_normalize_allows_negative_cooldown(self) -> None:
        out = _normalize_entitlements(
            {
                "defaults": {
                    "name_colour_stops": 0,
                    "max_3d_pair_bytes": 30720,
                    "skin_token_cooldown_days": -1,
                    "skin_kinds": ["handheld"],
                    "allow_armor_3d_helmet": False,
                },
                "groups": [
                    {
                        "id": "noble",
                        "tier": 1,
                        "skin_token_cooldown_days": 28,
                        "skin_kinds": ["book", "bow"],
                    }
                ],
            }
        )
        self.assertEqual(out["defaults"]["skin_token_cooldown_days"], -1)
        self.assertEqual(out["groups"][0]["skin_kinds"], ["book", "bow"])

    def test_resolve_uses_meta(self) -> None:
        with mock.patch(
            "skins.entitlements.get_player_meta",
            return_value={
                "name_colour_stops": 2,
                "max_3d_pair_bytes": 40960,
                "skin_token_cooldown_days": 21,
                "skin_kinds": ["armor_set", "handheld"],
                "allow_armor_3d_helmet": False,
            },
        ), mock.patch(
            "skins.catalog.get_catalog",
            return_value={
                "entitlements": {
                    "defaults": {
                        "name_colour_stops": 0,
                        "max_3d_pair_bytes": 30720,
                        "skin_token_cooldown_days": -1,
                        "skin_kinds": [],
                        "allow_armor_3d_helmet": False,
                    }
                }
            },
        ):
            out = resolve_skin_entitlements("abc", staff=False)
        self.assertEqual(out["name_colour_stops"], 2)
        self.assertEqual(out["max_3d_pair_bytes"], 40960)
        self.assertEqual(out["skin_token_cooldown_days"], 21)
        self.assertEqual(out["skin_kinds"], ["armor_set", "handheld"])
        self.assertFalse(out["allow_armor_3d_helmet"])
        self.assertTrue(can_mint_skin_token(out))

    def test_resolve_staff_colour_cap_and_kinds(self) -> None:
        with mock.patch(
            "skins.entitlements.get_player_meta",
            return_value={
                "name_colour_stops": 1,
                "max_3d_pair_bytes": 30720,
                "skin_token_cooldown_days": 28,
                "skin_kinds": ["handheld"],
                "allow_armor_3d_helmet": False,
            },
        ), mock.patch(
            "skins.catalog.get_catalog",
            return_value={"entitlements": {"defaults": {}}},
        ):
            out = resolve_skin_entitlements("abc", staff=True)
        self.assertEqual(out["name_colour_stops"], 8)
        self.assertIn("gun", out["skin_kinds"])
        self.assertIn("armor_set", out["skin_kinds"])
        self.assertTrue(out["allow_armor_3d_helmet"])

    def test_resolve_emergency_pair(self) -> None:
        with mock.patch(
            "skins.entitlements.get_player_meta", return_value=None
        ), mock.patch(
            "skins.catalog.get_catalog",
            return_value={"entitlements": {"defaults": {"name_colour_stops": 0}}},
        ):
            out = resolve_skin_entitlements("abc", staff=False)
        self.assertEqual(out["max_3d_pair_bytes"], EMERGENCY_MAX_3D_PAIR_BYTES)
        self.assertFalse(can_mint_skin_token(out))


class MintCooldownTest(unittest.TestCase):
    """PS no longer enforces mint cooldown; TFMCWeb owns the shared clock."""

    def test_issue_skin_ignores_rank_disallow_meta(self) -> None:
        from skins.codes import issue_code

        with mock.patch(
            "skins.discord_link.get_identity_status",
            return_value={"eligible": True},
        ), mock.patch("skins.codes.connect") as connect_mock:
            conn = mock.MagicMock()
            connect_mock.return_value.__enter__.return_value = conn
            result = issue_code("player-1", "skin")
        self.assertEqual(result["scope"], "skin")
        self.assertIn("code", result)

    def test_staff_scope_still_issues(self) -> None:
        from skins.codes import issue_code

        with mock.patch(
            "skins.discord_link.get_identity_status",
            return_value={"eligible": True},
        ), mock.patch("skins.codes.connect") as connect_mock:
            conn = mock.MagicMock()
            connect_mock.return_value.__enter__.return_value = conn
            result = issue_code("player-1", "skin_staff")
        self.assertEqual(result["scope"], "skin_staff")
        self.assertIn("code", result)

    def test_issue_skin_ignores_days_gate(self) -> None:
        from skins.codes import issue_code

        with mock.patch(
            "skins.discord_link.get_identity_status",
            return_value={"eligible": True},
        ), mock.patch("skins.codes.connect") as connect_mock:
            conn = mock.MagicMock()
            connect_mock.return_value.__enter__.return_value = conn
            result = issue_code("player-1", "skin")
        self.assertEqual(result["scope"], "skin")
        self.assertIn("code", result)

    def test_issue_drink_scope(self) -> None:
        from skins.codes import issue_code

        with mock.patch(
            "skins.discord_link.get_identity_status",
            return_value={"eligible": True},
        ), mock.patch("skins.codes.connect") as connect_mock:
            conn = mock.MagicMock()
            connect_mock.return_value.__enter__.return_value = conn
            result = issue_code("player-1", "drink")
        self.assertEqual(result["scope"], "drink")
        self.assertIn("code", result)

    def test_cosmetic_mint_status_none(self) -> None:
        from skins.codes import get_cosmetic_mint_status

        with mock.patch("skins.codes.connect") as connect_mock:
            conn = mock.MagicMock()
            connect_mock.return_value.__enter__.return_value = conn
            conn.execute.return_value.fetchone.return_value = {"last_at": None}
            out = get_cosmetic_mint_status("player-1")
        self.assertIsNone(out["last_mint_at"])
        self.assertEqual(out["player_uuid"], "player-1")

    def test_cosmetic_mint_status_shared_max(self) -> None:
        from skins.codes import get_cosmetic_mint_status

        with mock.patch("skins.codes.connect") as connect_mock:
            conn = mock.MagicMock()
            connect_mock.return_value.__enter__.return_value = conn
            conn.execute.return_value.fetchone.return_value = {
                "last_at": "2026-01-15T12:00:00Z"
            }
            out = get_cosmetic_mint_status("player-1")
        self.assertEqual(out["last_mint_at"], "2026-01-15T12:00:00Z")
        sql = conn.execute.call_args[0][0]
        self.assertIn("skin", sql.lower())
        self.assertIn("drink", sql.lower())


if __name__ == "__main__":
    unittest.main()
