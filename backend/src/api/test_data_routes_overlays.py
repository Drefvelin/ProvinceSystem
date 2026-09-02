"""Tests for the region overlay join on `GET /{map}/data/{mode}`.

Crop boxes are generated output, so they live in a sidecar beside the region
PNGs and are joined onto the authored tier JSON here. These cover the wire shape
the map depends on, and the streaming fast path everything else still takes.

The app is assembled from `data_router` alone rather than imported from
`server`, so no DB migration or startup hook runs.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

os.environ.setdefault("SKINS_DEV", "1")

from fastapi import FastAPI  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.api.data_routes import data_router  # noqa: E402
from src.api.map_registry import clear_map_registry_cache  # noqa: E402
from src.scripts.util import dirs  # noqa: E402

TEST_REGISTRY = """
maps:
  - id: main
    public: true
    display_name: Adavaar
    realm_id: main
"""

COUNTIES = {
    "COUNTY_1": {"name": "COUNTY_1", "provinces": [1, 2], "rgb": "41,152,44"},
    "COUNTY_2": {"name": "COUNTY_2", "provinces": [3], "rgb": "56,171,52"},
}

GREEN_BOX = {"x": 1204, "y": 880, "w": 96, "h": 72}
BLUE_BOX = {"x": 10, "y": 20, "w": 30, "h": 40}
NESTED_BOX = {"x": 5, "y": 6, "w": 7, "h": 8}


class RegionOverlayJoinTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)

        registry = root / "maps.yml"
        registry.write_text(TEST_REGISTRY, encoding="utf-8")
        self._orig_registry = os.environ.get("MAP_REGISTRY_PATH")
        os.environ["MAP_REGISTRY_PATH"] = str(registry)
        clear_map_registry_cache()
        self.addCleanup(self._restore_registry)

        self.defines_dir = root / "defines" / "main"
        self.defines_dir.mkdir(parents=True)
        self._orig_defines = dirs.DEFINES_DIR
        self._orig_output = dirs.OUTPUT_DIR
        dirs.DEFINES_DIR = str(root / "defines")
        dirs.OUTPUT_DIR = str(root / "output")
        self.addCleanup(self._restore_dirs)

        self.write_defines("county", COUNTIES)

        app = FastAPI()
        app.include_router(data_router)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def _restore_registry(self) -> None:
        if self._orig_registry is None:
            os.environ.pop("MAP_REGISTRY_PATH", None)
        else:
            os.environ["MAP_REGISTRY_PATH"] = self._orig_registry
        clear_map_registry_cache()

    def _restore_dirs(self) -> None:
        dirs.DEFINES_DIR = self._orig_defines
        dirs.OUTPUT_DIR = self._orig_output

    def write_defines(self, name: str, payload: object) -> Path:
        path = self.defines_dir / f"{name}.json"
        # Bytes, not text: text mode would translate newlines on Windows and the
        # verbatim-body assertions below compare against what was streamed.
        path.write_bytes(json.dumps(payload, indent=4).encode("utf-8"))
        return path

    def defines_bytes(self, name: str) -> str:
        return (self.defines_dir / f"{name}.json").read_bytes().decode("utf-8")

    def write_sidecar(self, mode: str, payload: dict) -> None:
        path = Path(dirs.region_overlay_file("main", mode))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(json.dumps(payload).encode("utf-8"))

    def test_boxes_are_joined_onto_authored_data_by_rgb(self) -> None:
        self.write_sidecar(
            "county",
            {
                "41,152,44": {"overlay": GREEN_BOX},
                "56,171,52": {"overlay": BLUE_BOX, "overlay_nested": NESTED_BOX},
            },
        )

        body = self.client.get("/main/data/county").json()

        self.assertEqual(GREEN_BOX, body["COUNTY_1"]["overlay"])
        self.assertEqual(BLUE_BOX, body["COUNTY_2"]["overlay"])
        self.assertEqual(NESTED_BOX, body["COUNTY_2"]["overlay_nested"])
        # Authored fields are untouched, and the file on disk stays clean.
        self.assertEqual([1, 2], body["COUNTY_1"]["provinces"])
        on_disk = json.loads(
            (self.defines_dir / "county.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("overlay", on_disk["COUNTY_1"])

    def test_a_region_the_sidecar_has_no_box_for_gets_none(self) -> None:
        """A queued regen may have painted only some counties.

        The map hides an overlay with no box rather than mispositioning a PNG,
        so leaving the key off is the honest answer.
        """
        self.write_sidecar("county", {"41,152,44": {"overlay": GREEN_BOX}})

        body = self.client.get("/main/data/county").json()

        self.assertEqual(GREEN_BOX, body["COUNTY_1"]["overlay"])
        self.assertNotIn("overlay", body["COUNTY_2"])

    def test_no_sidecar_serves_the_file_verbatim(self) -> None:
        """Regions never generated: same bytes as before the join existed."""
        response = self.client.get("/main/data/county")

        self.assertEqual(200, response.status_code)
        self.assertEqual(self.defines_bytes("county"), response.text)
        self.assertIn("last-modified", response.headers)

    def test_joined_response_answers_304_for_a_current_client(self) -> None:
        self.write_sidecar("county", {"41,152,44": {"overlay": GREEN_BOX}})

        first = self.client.get("/main/data/county")
        etag = first.headers["etag"]

        second = self.client.get(
            "/main/data/county", headers={"If-None-Match": etag}
        )

        self.assertEqual(304, second.status_code)
        self.assertEqual(b"", second.content)

    def test_a_new_box_changes_the_etag(self) -> None:
        self.write_sidecar("county", {"41,152,44": {"overlay": GREEN_BOX}})
        first = self.client.get("/main/data/county")

        self.write_sidecar(
            "county",
            {"41,152,44": {"overlay": GREEN_BOX}, "56,171,52": {"overlay": BLUE_BOX}},
        )
        second = self.client.get(
            "/main/data/county", headers={"If-None-Match": first.headers["etag"]}
        )

        self.assertEqual(200, second.status_code)
        self.assertEqual(BLUE_BOX, second.json()["COUNTY_2"]["overlay"])

    def test_non_region_files_keep_the_streaming_path(self) -> None:
        """Geometry blobs are 60-80 KB and must keep 304ing on an mtime."""
        centroids = {"1": {"x": 5, "y": 6, "pixel_count": 700}}
        self.write_defines("province_centroids", centroids)
        self.write_sidecar("county", {"41,152,44": {"overlay": GREEN_BOX}})

        response = self.client.get("/main/data/province_centroids")

        self.assertEqual(self.defines_bytes("province_centroids"), response.text)
        self.assertIn("last-modified", response.headers)

    def test_a_defines_file_this_cannot_parse_is_still_served_verbatim(self) -> None:
        (self.defines_dir / "duchy.json").write_bytes(b"{ truncated")
        self.write_sidecar("duchy", {"41,152,44": {"overlay": GREEN_BOX}})

        response = self.client.get("/main/data/duchy")

        self.assertEqual(200, response.status_code)
        self.assertEqual("{ truncated", response.text)

    def test_entries_that_are_not_regions_are_left_alone(self) -> None:
        self.write_defines(
            "kingdom",
            {"KINGDOM_1": "nonsense", "KINGDOM_2": {"rgb": ["not", "a", "string"]}},
        )
        self.write_sidecar("kingdom", {"41,152,44": {"overlay": GREEN_BOX}})

        response = self.client.get("/main/data/kingdom")

        self.assertEqual(200, response.status_code)
        self.assertEqual("nonsense", response.json()["KINGDOM_1"])

    def test_missing_mode_is_still_a_404(self) -> None:
        self.assertEqual(404, self.client.get("/main/data/empire").status_code)


if __name__ == "__main__":
    unittest.main()
