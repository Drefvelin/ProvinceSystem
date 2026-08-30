"""Cache-Control for live map file and JSON responses.

Map images must never go stale, but they are large and regenerate rarely, so
they revalidate (`no-cache` + ETag -> 304) instead of using `no-store`.
Live JSON stays on `no-store`.
"""

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

from src.api.http_headers import (
    add_no_cache,
    add_revalidate,
    conditional_file_response,
)


class HttpHeadersTest(unittest.TestCase):
    def test_add_no_cache_sets_no_store(self) -> None:
        response = add_no_cache(Response())
        self.assertIn("no-store", response.headers["Cache-Control"])
        self.assertEqual("no-cache", response.headers["Pragma"])
        self.assertEqual("0", response.headers["Expires"])


class RevalidateHeaderTest(unittest.TestCase):
    def test_add_revalidate_allows_storage_but_forces_recheck(self) -> None:
        response = add_revalidate(Response())
        cache_control = response.headers["Cache-Control"]
        self.assertIn("no-cache", cache_control)
        self.assertIn("private", cache_control)
        # no-store would defeat the point: the body could never be reused.
        self.assertNotIn("no-store", cache_control)


class ConditionalFileResponseTest(unittest.TestCase):
    def _png(self, tmp: str) -> Path:
        png = Path(tmp) / "map.png"
        png.write_bytes(b"fake-png-bytes")
        return png

    def test_serves_body_with_etag_when_client_has_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            response = conditional_file_response(
                self._png(tmp), media_type="image/png"
            )
            self.assertEqual(200, response.status_code)
            self.assertTrue(response.headers["etag"])
            self.assertIn("no-cache", response.headers["Cache-Control"])

    def test_returns_304_when_etag_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            png = self._png(tmp)
            first = conditional_file_response(png, media_type="image/png")
            second = conditional_file_response(
                png,
                media_type="image/png",
                if_none_match=first.headers["etag"],
            )
            self.assertEqual(304, second.status_code)
            self.assertEqual(b"", second.body)

    def test_returns_200_when_file_changed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            png = self._png(tmp)
            stale_etag = conditional_file_response(
                png, media_type="image/png"
            ).headers["etag"]
            png.write_bytes(b"fake-png-bytes-regenerated")

            response = conditional_file_response(
                png, media_type="image/png", if_none_match=stale_etag
            )
            self.assertEqual(200, response.status_code)

    def test_keeps_cors_open_on_both_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            png = self._png(tmp)
            full = conditional_file_response(png, media_type="image/png")
            not_modified = conditional_file_response(
                png, media_type="image/png", if_none_match=full.headers["etag"]
            )
            self.assertEqual("*", full.headers["Access-Control-Allow-Origin"])
            self.assertEqual("*", not_modified.headers["Access-Control-Allow-Origin"])


class MapdataRevalidateTest(unittest.IsolatedAsyncioTestCase):
    async def test_mapdata_nation_revalidates_instead_of_no_store(self) -> None:
        from src.api import file_routes

        with tempfile.TemporaryDirectory() as tmp:
            maps_dir = Path(tmp) / "main" / "maps"
            maps_dir.mkdir(parents=True)
            png = maps_dir / "nation_map.png"
            png.write_bytes(b"fake-png-bytes")

            with patch.object(file_routes, "OUTPUT_BASE", Path(tmp)):
                with patch("src.api.file_routes.ensure_map_access"):
                    response = await file_routes.get_map_file("main", "nation", None)

            self.assertIn("no-cache", response.headers["Cache-Control"])
            self.assertNotIn("no-store", response.headers["Cache-Control"])
            self.assertTrue(response.headers["etag"])
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
