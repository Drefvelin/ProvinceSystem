"""Tests for regen type parsing."""

from __future__ import annotations

import unittest

from .regen_types import parse_regen_type, region_regen_queued


class TestRegenTypes(unittest.TestCase):
    def test_fullregen_all_modes(self) -> None:
        spec = parse_regen_type("fullregen")
        self.assertIsNone(spec.modes)
        self.assertTrue(spec.full_regions)

    def test_fullregen_single_mode(self) -> None:
        spec = parse_regen_type("fullregen:nation")
        self.assertEqual(spec.modes, ["nation"])
        self.assertTrue(spec.full_regions)

    def test_queued_all_modes(self) -> None:
        spec = parse_regen_type("queued")
        self.assertIsNone(spec.modes)
        self.assertFalse(spec.full_regions)

    def test_queued_single_mode(self) -> None:
        spec = parse_regen_type("queued:nation")
        self.assertEqual(spec.modes, ["nation"])
        self.assertFalse(spec.full_regions)

    def test_mode_shorthand(self) -> None:
        spec = parse_regen_type("nation")
        self.assertEqual(spec.modes, ["nation"])
        self.assertFalse(spec.full_regions)

    def test_region_regen_queued(self) -> None:
        full = parse_regen_type("fullregen:nation")
        queued = parse_regen_type("queued:nation")
        self.assertFalse(region_regen_queued(full, "nation"))
        self.assertTrue(region_regen_queued(queued, "nation"))
        self.assertFalse(region_regen_queued(queued, "trade"))


if __name__ == "__main__":
    unittest.main()
