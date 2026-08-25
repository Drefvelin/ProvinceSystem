"""Tests for web creator tier gate."""

from __future__ import annotations

import unittest

from src.characters.web_creator_access import (
    gate_error_message,
    player_donator_tier,
    resolve_gate,
)


class WebCreatorAccessTests(unittest.TestCase):
    def test_open_when_min_tier_zero(self) -> None:
        catalog = {"web_creator_access": {"by_realm": {"main": {"min_tier": 0}}}}
        gate = resolve_gate(
            catalog,
            realm_id="main",
            entitlements={"donator_tier": 0},
        )
        self.assertTrue(gate["web_creator_allowed"])

    def test_noble_required_blocks_default(self) -> None:
        catalog = {
            "web_creator_access": {
                "by_realm": {"main": {"min_tier": 1, "min_group_id": "noble"}}
            },
            "slot_limits": {
                "groups": [{"id": "noble", "display_name": "Noble", "tier": 1}]
            },
        }
        gate = resolve_gate(
            catalog,
            realm_id="main",
            entitlements={"donator_tier": 0},
        )
        self.assertFalse(gate["web_creator_allowed"])
        self.assertIn("Noble", gate_error_message(gate))

    def test_noble_passes_for_tier_one(self) -> None:
        catalog = {
            "web_creator_access": {"by_realm": {"main": {"min_tier": 1}}}
        }
        gate = resolve_gate(
            catalog,
            realm_id="main",
            entitlements={"donator_tier": 1},
        )
        self.assertTrue(gate["web_creator_allowed"])
        self.assertEqual(1, player_donator_tier({"donator_tier": 1}))


if __name__ == "__main__":
    unittest.main()
