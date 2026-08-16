from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from scripts.loader.markers import (  # noqa: E402
    build_markers_response,
    enrich_settlements,
    load_raw_markers,
)


class MarkersLoaderTest(unittest.TestCase):
    def test_enrich_adds_map_coords_from_centroids(self) -> None:
        settlements = [
            {
                "id": "rivendell",
                "name": "Rivendell",
                "faction_id": "elves",
                "province_id": 42,
                "center_x": 1200,
                "center_z": -3400,
                "kind": "settlement",
                "provinces": [42, 43],
            }
        ]
        centroids = {
            "42": {"x": 3233.45, "y": 1961.12, "pixel_count": 100},
        }

        out = enrich_settlements(settlements, centroids)

        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["map_x"], 3233)
        self.assertEqual(out[0]["map_y"], 1961)
        self.assertEqual(out[0]["center_x"], 1200)
        self.assertEqual(out[0]["provinces"], [42, 43])

    def test_enrich_missing_centroid_omits_map_coords(self) -> None:
        settlements = [{"id": "ghost", "province_id": 99, "kind": "settlement"}]
        out = enrich_settlements(settlements, {})
        self.assertNotIn("map_x", out[0])
        self.assertNotIn("map_y", out[0])

    def test_enrich_skips_invalid_entries(self) -> None:
        out = enrich_settlements(["bad", {"province_id": 1}], {"1": {"x": 1, "y": 2}})
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["map_x"], 1)

    def test_load_raw_markers_missing_file_returns_empty_settlements(self) -> None:
        with mock.patch(
            "scripts.loader.markers.input_file",
            return_value=os.path.join(tempfile.gettempdir(), "missing_map_markers.json"),
        ):
            payload = load_raw_markers("main")

        self.assertEqual(payload["map_id"], "main")
        self.assertEqual(payload["settlements"], [])
        self.assertIsNone(payload["exported_at"])

    def test_build_markers_response_enriches_from_fixture_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            markers_path = os.path.join(tmp, "map_markers.json")
            centroids_path = os.path.join(tmp, "province_centroids.json")
            with open(markers_path, "w", encoding="utf-8") as f:
                f.write(
                    '{"map_id":"main","exported_at":"2026-08-15T20:00:00Z",'
                    '"settlements":[{"id":"a","province_id":1,"kind":"settlement"}]}'
                )
            with open(centroids_path, "w", encoding="utf-8") as f:
                f.write('{"1":{"x":10.4,"y":20.6}}')

            with mock.patch(
                "scripts.loader.markers.input_file",
                return_value=markers_path,
            ), mock.patch(
                "scripts.loader.markers.defines_file",
                return_value=centroids_path,
            ):
                payload = build_markers_response("main")

        self.assertEqual(payload["map_id"], "main")
        self.assertEqual(len(payload["settlements"]), 1)
        self.assertEqual(payload["settlements"][0]["map_x"], 10)
        self.assertEqual(payload["settlements"][0]["map_y"], 21)

    def test_load_raw_markers_passes_through_population_and_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            markers_path = os.path.join(tmp, "map_markers.json")
            with open(markers_path, "w", encoding="utf-8") as f:
                f.write(
                    '{"map_id":"main","settlement_large_population_threshold":8,'
                    '"settlements":[{"id":"a","population":12,"marker_size":"large"}]}'
                )
            with mock.patch(
                "scripts.loader.markers.input_file",
                return_value=markers_path,
            ):
                payload = load_raw_markers("main")

        self.assertEqual(payload["settlement_large_population_threshold"], 8)
        self.assertEqual(payload["settlements"][0]["population"], 12)
        self.assertEqual(payload["settlements"][0]["marker_size"], "large")

    def test_build_markers_response_preserves_marker_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            markers_path = os.path.join(tmp, "map_markers.json")
            centroids_path = os.path.join(tmp, "province_centroids.json")
            with open(markers_path, "w", encoding="utf-8") as f:
                f.write(
                    '{"map_id":"main","settlement_large_population_threshold":8,'
                    '"settlements":[{"id":"a","province_id":1,"population":9,'
                    '"marker_size":"large","kind":"faction_capital"}]}'
                )
            with open(centroids_path, "w", encoding="utf-8") as f:
                f.write('{"1":{"x":10,"y":20}}')

            with mock.patch(
                "scripts.loader.markers.input_file",
                return_value=markers_path,
            ), mock.patch(
                "scripts.loader.markers.defines_file",
                return_value=centroids_path,
            ):
                payload = build_markers_response("main")

        self.assertEqual(payload["settlement_large_population_threshold"], 8)
        settlement = payload["settlements"][0]
        self.assertEqual(settlement["population"], 9)
        self.assertEqual(settlement["marker_size"], "large")
        self.assertEqual(settlement["kind"], "faction_capital")
        self.assertEqual(settlement["map_x"], 10)
        self.assertEqual(settlement["map_y"], 20)


if __name__ == "__main__":
    unittest.main()
