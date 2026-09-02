"""Province mapdata serves input/{map}/provinces.png rather than a generated map."""

from __future__ import annotations

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

from src.api.file_routes import file_router  # noqa: E402
from src.api import file_routes  # noqa: E402
from src.api.map_registry import clear_map_registry_cache  # noqa: E402
from src.scripts.util import dirs  # noqa: E402

TEST_REGISTRY = """
maps:
  - id: main
    public: true
    display_name: Adavaar
    realm_id: main
"""


class ProvinceMapdataTest(unittest.TestCase):
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

        self.input_dir = root / "input"
        (self.input_dir / "main").mkdir(parents=True)
        self.output_dir = root / "output"
        self.output_dir.mkdir()

        self._orig_input = dirs.INPUT_DIR
        self._orig_output_base = file_routes.OUTPUT_BASE
        dirs.INPUT_DIR = str(self.input_dir)
        file_routes.OUTPUT_BASE = self.output_dir
        self.addCleanup(self._restore_dirs)

        app = FastAPI()
        app.include_router(file_router)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def _restore_registry(self) -> None:
        if self._orig_registry is None:
            os.environ.pop("MAP_REGISTRY_PATH", None)
        else:
            os.environ["MAP_REGISTRY_PATH"] = self._orig_registry
        clear_map_registry_cache()

    def _restore_dirs(self) -> None:
        dirs.INPUT_DIR = self._orig_input
        file_routes.OUTPUT_BASE = self._orig_output_base

    def test_serves_input_provinces_png(self) -> None:
        png = self.input_dir / "main" / "provinces.png"
        png.write_bytes(b"province-png-bytes")

        response = self.client.get("/main/mapdata/province")
        self.assertEqual(200, response.status_code)
        self.assertEqual("image/png", response.headers["content-type"].split(";")[0])
        self.assertEqual(b"province-png-bytes", response.content)

    def test_404_when_provinces_png_missing(self) -> None:
        response = self.client.get("/main/mapdata/province")
        self.assertEqual(404, response.status_code)

    def test_unknown_mode_still_404s(self) -> None:
        response = self.client.get("/main/mapdata/not_a_mode")
        self.assertEqual(404, response.status_code)

    def test_terrain_still_reads_output_maps(self) -> None:
        maps = self.output_dir / "main" / "maps"
        maps.mkdir(parents=True)
        (maps / "terrain_map.png").write_bytes(b"terrain-png")
        (self.input_dir / "main" / "provinces.png").write_bytes(b"province-png-bytes")

        response = self.client.get("/main/mapdata/terrain")
        self.assertEqual(200, response.status_code)
        self.assertEqual(b"terrain-png", response.content)
