"""Tests for the region overlay sidecar in `scripts/util/overlay_metadata.py`.

The crop boxes describe generated PNGs under output/, so they live beside those
PNGs rather than in the authored tier JSON under defines/. These cover the two
things that made the old defines-merge lossy: which regen replaces the file and
which one adds to it.
"""

from __future__ import annotations

import json
import os
import tempfile
import unittest
from unittest.mock import patch

from . import dirs
from .overlay_metadata import load_overlay_metadata, write_overlay_metadata

GREEN = {"overlay": {"x": 10, "y": 20, "w": 30, "h": 40}}
BLUE = {"overlay": {"x": 50, "y": 60, "w": 70, "h": 80}}
NESTED = {
    "overlay": {"x": 1, "y": 2, "w": 3, "h": 4},
    "overlay_nested": {"x": 5, "y": 6, "w": 7, "h": 8},
}


class OverlaySidecarTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        patcher = patch.object(dirs, "OUTPUT_DIR", os.path.join(self.tmp.name, "output"))
        patcher.start()
        self.addCleanup(patcher.stop)

    def sidecar_path(self) -> str:
        return dirs.region_overlay_file("fixture", "county")

    def read_sidecar(self) -> dict:
        with open(self.sidecar_path(), encoding="utf-8") as handle:
            return json.load(handle)

    def test_write_creates_the_sidecar_beside_the_pngs(self) -> None:
        write_overlay_metadata("fixture", "county", {"41,152,44": GREEN}, merge=False)

        self.assertEqual({"41,152,44": GREEN}, self.read_sidecar())
        self.assertEqual(
            os.path.join(
                self.tmp.name, "output", "fixture", "regions", "county", "overlays.json"
            ),
            self.sidecar_path(),
        )

    def test_full_regen_replaces_and_prunes_regions_that_no_longer_exist(self) -> None:
        """A full regen repaints everything, so what it omits is gone for good."""
        write_overlay_metadata("fixture", "county", {"41,152,44": GREEN}, merge=False)
        write_overlay_metadata("fixture", "county", {"56,171,52": BLUE}, merge=False)

        self.assertEqual({"56,171,52": BLUE}, self.read_sidecar())

    def test_queued_regen_keeps_the_boxes_it_did_not_repaint(self) -> None:
        """A queued regen only saves queued regions.

        Replacing the file here would blank every untouched region's overlay on
        the map, which is the whole reason `merge` follows `queued_regen`.
        """
        write_overlay_metadata("fixture", "county", {"41,152,44": GREEN}, merge=False)
        write_overlay_metadata("fixture", "county", {"56,171,52": BLUE}, merge=True)

        self.assertEqual({"41,152,44": GREEN, "56,171,52": BLUE}, self.read_sidecar())

    def test_queued_regen_overwrites_a_repainted_region(self) -> None:
        write_overlay_metadata("fixture", "county", {"41,152,44": GREEN}, merge=False)
        write_overlay_metadata("fixture", "county", {"41,152,44": BLUE}, merge=True)

        self.assertEqual({"41,152,44": BLUE}, self.read_sidecar())

    def test_nested_boxes_round_trip(self) -> None:
        write_overlay_metadata("fixture", "nation", {"229,60,112": NESTED}, merge=False)

        self.assertEqual(
            {"229,60,112": NESTED}, load_overlay_metadata("fixture", "nation")
        )

    def test_nothing_to_record_plants_no_empty_sidecar(self) -> None:
        write_overlay_metadata("fixture", "county", {}, merge=False)

        self.assertFalse(os.path.exists(self.sidecar_path()))

    def test_full_regen_that_paints_nothing_prunes_a_stale_sidecar(self) -> None:
        write_overlay_metadata("fixture", "county", {"41,152,44": GREEN}, merge=False)

        write_overlay_metadata("fixture", "county", {}, merge=False)

        self.assertEqual({}, self.read_sidecar())

    def test_load_is_empty_for_a_mode_that_was_never_generated(self) -> None:
        """The honest answer: no boxes, so the map positions no overlay."""
        self.assertEqual({}, load_overlay_metadata("fixture", "county"))

    def test_load_is_empty_for_an_unreadable_sidecar(self) -> None:
        os.makedirs(os.path.dirname(self.sidecar_path()), exist_ok=True)
        with open(self.sidecar_path(), "w", encoding="utf-8") as handle:
            handle.write("{ truncated")

        self.assertEqual({}, load_overlay_metadata("fixture", "county"))

    def test_load_ignores_entries_that_are_not_objects(self) -> None:
        os.makedirs(os.path.dirname(self.sidecar_path()), exist_ok=True)
        with open(self.sidecar_path(), "w", encoding="utf-8") as handle:
            json.dump({"41,152,44": GREEN, "56,171,52": "nonsense"}, handle)

        self.assertEqual({"41,152,44": GREEN}, load_overlay_metadata("fixture", "county"))

    def test_load_is_empty_when_the_sidecar_is_not_an_object(self) -> None:
        os.makedirs(os.path.dirname(self.sidecar_path()), exist_ok=True)
        with open(self.sidecar_path(), "w", encoding="utf-8") as handle:
            json.dump([GREEN], handle)

        self.assertEqual({}, load_overlay_metadata("fixture", "county"))


if __name__ == "__main__":
    unittest.main()
