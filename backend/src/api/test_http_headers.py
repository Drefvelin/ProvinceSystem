"""Cache-Control for live map file and JSON responses."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi import Response

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from src.api.http_headers import add_no_cache


class HttpHeadersTest(unittest.TestCase):
    def test_add_no_cache_sets_no_store(self) -> None:
        response = add_no_cache(Response())
        self.assertIn("no-store", response.headers["Cache-Control"])
        self.assertEqual("no-cache", response.headers["Pragma"])
        self.assertEqual("0", response.headers["Expires"])


class MapdataNoCacheTest(unittest.IsolatedAsyncioTestCase):
    async def test_mapdata_nation_sends_no_store(self) -> None:
        from src.api import file_routes

        with tempfile.TemporaryDirectory() as tmp:
            maps_dir = Path(tmp) / "main" / "maps"
            maps_dir.mkdir(parents=True)
            png = maps_dir / "nation_map.png"
            png.write_bytes(b"\x89PNG\r\n\x1a\n")

            with patch.object(file_routes, "OUTPUT_BASE", Path(tmp)):
                with patch("src.api.file_routes.ensure_map_access"):
                    response = await file_routes.get_map_file("main", "nation", None)

            self.assertIn("no-store", response.headers["Cache-Control"])
            self.assertEqual("*", response.headers["Access-Control-Allow-Origin"])


class MapDataJsonNoCacheTest(unittest.IsolatedAsyncioTestCase):
    async def test_nation_json_sends_no_store(self) -> None:
        from src.api import data_routes

        with tempfile.TemporaryDirectory() as tmp:
            nation_path = os.path.join(tmp, "nation.json")
            with open(nation_path, "w", encoding="utf-8") as handle:
                handle.write('{"Lantan": {"id": "Lantan", "rgb": "51,200,210"}}')

            with patch("src.api.data_routes.ensure_map_access"):
                with patch("src.api.data_routes.defines_file", return_value=nation_path):
                    response = await data_routes.get_map_name_data(
                        "main", "nation", None
                    )

            self.assertIn("no-store", response.headers["Cache-Control"])


if __name__ == "__main__":
    unittest.main()
