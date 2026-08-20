from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from scripts.loader.markers import (  # noqa: E402
    build_markers_response,
    enrich_settlements,
    load_raw_markers,
    resolve_settlement_map_xy,
    world_coords_to_map_xy,
)


class MarkersLoaderTest(unittest.TestCase):
    def test_world_coords_to_map_xy_maps_block_xz_to_pixels(self) -> None:
        self.assertEqual(world_coords_to_map_xy(1748, 2739), (1748, 2739))
        self.assertIsNone(world_coords_to_map_xy(None, 1))
        self.assertIsNone(world_coords_to_map_xy("bad", 1))

    def test_enrich_prefers_world_coords_over_centroids(self) -> None:
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
        self.assertEqual(out[0]["map_x"], 1200)
        self.assertEqual(out[0]["map_y"], -3400)
        self.assertEqual(out[0]["center_x"], 1200)
        self.assertEqual(out[0]["provinces"], [42, 43])

    def test_enrich_falls_back_to_centroid_without_world_coords(self) -> None:
        settlements = [{"id": "ghost", "province_id": 42, "kind": "settlement"}]
        centroids = {"42": {"x": 3233.45, "y": 1961.12}}
        out = enrich_settlements(settlements, centroids)
        self.assertEqual(out[0]["map_x"], 3233)
        self.assertEqual(out[0]["map_y"], 1961)

    def test_enrich_missing_centroid_omits_map_coords(self) -> None:
        settlements = [{"id": "ghost", "province_id": 99, "kind": "settlement"}]
        out = enrich_settlements(settlements, {})
        self.assertNotIn("map_x", out[0])
        self.assertNotIn("map_y", out[0])

    def test_enrich_skips_invalid_entries(self) -> None:
        out = enrich_settlements(["bad", {"province_id": 1}], {"1": {"x": 1, "y": 2}})
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["map_x"], 1)

    def test_resolve_settlement_map_xy_prefers_world_coords(self) -> None:
        row = {"center_x": 5, "center_z": 6, "province_id": 1}
        centroids = {"1": {"x": 100, "y": 200}}
        self.assertEqual(resolve_settlement_map_xy(row, centroids), (5, 6))

    def test_load_raw_markers_missing_file_returns_empty_settlements(self) -> None:
        with mock.patch(
            "scripts.loader.markers.input_file",
            return_value=os.path.join(tempfile.gettempdir(), "missing_map_markers.json"),
        ):
            payload = load_raw_markers("main")

        self.assertEqual(payload["map_id"], "main")
        self.assertEqual(payload["settlements"], [])
        self.assertEqual(payload["installations"], [])
        self.assertEqual(payload["forts"], [])
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

    def test_load_raw_markers_passes_through_installations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            markers_path = os.path.join(tmp, "map_markers.json")
            with open(markers_path, "w", encoding="utf-8") as f:
                f.write(
                    '{"map_id":"main","installations":['
                    '{"id":"lanhold","name":"Lanhold","kind":"fort","province_id":705,'
                    '"faction_id":"Lantan","center_x":1748,"center_z":2739}]}'
                )
            with mock.patch(
                "scripts.loader.markers.input_file",
                return_value=markers_path,
            ):
                payload = load_raw_markers("main")

        self.assertEqual(len(payload["installations"]), 1)
        self.assertEqual(payload["installations"][0]["kind"], "fort")

    def test_build_markers_response_enriches_installations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            markers_path = os.path.join(tmp, "map_markers.json")
            centroids_path = os.path.join(tmp, "province_centroids.json")
            with open(markers_path, "w", encoding="utf-8") as f:
                f.write(
                    '{"map_id":"main","settlements":[],"installations":['
                    '{"id":"lanhold","name":"Lanhold","kind":"fort","province_id":705,'
                    '"faction_id":"Lantan","center_x":1748,"center_z":2739}]}'
                )
            with open(centroids_path, "w", encoding="utf-8") as f:
                f.write('{"705":{"x":100,"y":200}}')

            with mock.patch(
                "scripts.loader.markers.input_file",
                return_value=markers_path,
            ), mock.patch(
                "scripts.loader.markers.defines_file",
                return_value=centroids_path,
            ):
                payload = build_markers_response("main")

        installation = payload["installations"][0]
        self.assertEqual(installation["map_x"], 1748)
        self.assertEqual(installation["map_y"], 2739)

    def test_build_markers_response_installation_centroid_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            markers_path = os.path.join(tmp, "map_markers.json")
            centroids_path = os.path.join(tmp, "province_centroids.json")
            with open(markers_path, "w", encoding="utf-8") as f:
                f.write(
                    '{"map_id":"main","installations":['
                    '{"id":"harbor","name":"Harbor","kind":"port","province_id":42}]}'
                )
            with open(centroids_path, "w", encoding="utf-8") as f:
                f.write('{"42":{"x":50.4,"y":60.6}}')

            with mock.patch(
                "scripts.loader.markers.input_file",
                return_value=markers_path,
            ), mock.patch(
                "scripts.loader.markers.defines_file",
                return_value=centroids_path,
            ):
                payload = build_markers_response("main")

        installation = payload["installations"][0]
        self.assertEqual(installation["map_x"], 50)
        self.assertEqual(installation["map_y"], 61)

    def test_build_markers_response_installation_missing_centroid_omits_map_coords(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            markers_path = os.path.join(tmp, "map_markers.json")
            centroids_path = os.path.join(tmp, "province_centroids.json")
            with open(markers_path, "w", encoding="utf-8") as f:
                f.write(
                    '{"map_id":"main","installations":['
                    '{"id":"ghost","name":"Ghost","kind":"airport","province_id":99}]}'
                )
            with open(centroids_path, "w", encoding="utf-8") as f:
                f.write("{}")

            with mock.patch(
                "scripts.loader.markers.input_file",
                return_value=markers_path,
            ), mock.patch(
                "scripts.loader.markers.defines_file",
                return_value=centroids_path,
            ):
                payload = build_markers_response("main")

        installation = payload["installations"][0]
        self.assertNotIn("map_x", installation)
        self.assertNotIn("map_y", installation)

    def test_load_raw_markers_passes_through_forts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            markers_path = os.path.join(tmp, "map_markers.json")
            with open(markers_path, "w", encoding="utf-8") as f:
                f.write(
                    '{"map_id":"main","forts":['
                    '{"id":"lanhold","name":"Lanhold","province_id":705,'
                    '"faction_id":"Lantan","center_x":1748,"center_z":2739,'
                    '"zoc_provinces":[705,706]}]}'
                )
            with mock.patch(
                "scripts.loader.markers.input_file",
                return_value=markers_path,
            ):
                payload = load_raw_markers("main")

        self.assertEqual(len(payload["forts"]), 1)
        self.assertEqual(payload["forts"][0]["zoc_provinces"], [705, 706])

    def test_build_markers_response_enriches_forts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            markers_path = os.path.join(tmp, "map_markers.json")
            centroids_path = os.path.join(tmp, "province_centroids.json")
            overlays_path = os.path.join(tmp, "zoc_overlays.json")
            zoc_png = os.path.join(tmp, "lanhold.png")
            Image.new("RGBA", (4, 4), (0, 0, 0, 0)).save(zoc_png)

            with open(markers_path, "w", encoding="utf-8") as f:
                f.write(
                    '{"map_id":"main","forts":['
                    '{"id":"lanhold","province_id":705,"center_x":1748,"center_z":2739,'
                    '"zoc_provinces":[705]}]}'
                )
            with open(centroids_path, "w", encoding="utf-8") as f:
                f.write('{"705":{"x":100,"y":200}}')
            with open(overlays_path, "w", encoding="utf-8") as f:
                f.write(
                    '{"lanhold":{"overlay":{"x":10,"y":20,"w":30,"h":40}}}'
                )

            def fake_defines_file(map_name: str, filename: str) -> str:
                if filename == "province_centroids.json":
                    return centroids_path
                raise FileNotFoundError(filename)

            with mock.patch(
                "scripts.loader.markers.input_file",
                return_value=markers_path,
            ), mock.patch(
                "scripts.loader.markers.defines_file",
                side_effect=fake_defines_file,
            ), mock.patch(
                "scripts.loader.markers.zoc_overlays_file",
                return_value=overlays_path,
            ), mock.patch(
                "scripts.loader.markers.zoc_image",
                return_value=zoc_png,
            ):
                payload = build_markers_response("main")

        fort = payload["forts"][0]
        self.assertEqual(fort["map_x"], 1748)
        self.assertEqual(fort["map_y"], 2739)
        self.assertEqual(fort["overlay"], {"x": 10, "y": 20, "w": 30, "h": 40})
        self.assertEqual(fort["zoc_url"], "/main/zoc/lanhold.png")

    def test_build_markers_response_fort_centroid_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            markers_path = os.path.join(tmp, "map_markers.json")
            centroids_path = os.path.join(tmp, "province_centroids.json")
            with open(markers_path, "w", encoding="utf-8") as f:
                f.write(
                    '{"map_id":"main","forts":['
                    '{"id":"keep","province_id":42,"zoc_provinces":[42]}]}'
                )
            with open(centroids_path, "w", encoding="utf-8") as f:
                f.write('{"42":{"x":50.4,"y":60.6}}')

            with mock.patch(
                "scripts.loader.markers.input_file",
                return_value=markers_path,
            ), mock.patch(
                "scripts.loader.markers.defines_file",
                return_value=centroids_path,
            ):
                payload = build_markers_response("main")

        fort = payload["forts"][0]
        self.assertEqual(fort["map_x"], 50)
        self.assertEqual(fort["map_y"], 61)
        self.assertNotIn("zoc_url", fort)


if __name__ == "__main__":
    unittest.main()
