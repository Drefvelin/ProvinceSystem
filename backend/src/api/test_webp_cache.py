"""WebP variant cache for large map images."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from PIL import Image

from src.api import webp_cache


def _make_png(path: Path, size: tuple[int, int] = (64, 64)) -> Path:
    Image.new("RGB", size, (120, 80, 40)).save(path, "PNG")
    return path


class AcceptHeaderTest(unittest.TestCase):
    def test_detects_webp_support(self) -> None:
        self.assertTrue(
            webp_cache.client_accepts_webp("image/avif,image/webp,image/png,*/*")
        )

    def test_rejects_client_without_webp(self) -> None:
        self.assertFalse(webp_cache.client_accepts_webp("image/png,*/*"))

    def test_rejects_missing_or_non_string_header(self) -> None:
        # Route functions called directly hand over FastAPI's unresolved Header
        # sentinel rather than a string; that must read as "no WebP".
        self.assertFalse(webp_cache.client_accepts_webp(None))
        self.assertFalse(webp_cache.client_accepts_webp(object()))


class WebpVariantTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.cache = self.tmp / "cache"
        patcher = patch.object(webp_cache, "_CACHE_DIR", self.cache)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self._tmp.cleanup)
        self.source = _make_png(self.tmp / "map.png")

    def test_returns_none_when_client_cannot_display_webp(self) -> None:
        self.assertIsNone(
            webp_cache.webp_variant(self.source, accept="image/png", background=False)
        )

    def test_cold_cache_serves_original_and_does_not_block(self) -> None:
        # background=True must return None immediately rather than encode inline.
        with patch.object(webp_cache, "_encode_in_background") as spawn:
            result = webp_cache.webp_variant(self.source, accept="image/webp")
        self.assertIsNone(result)
        spawn.assert_called_once()

    def test_encodes_and_returns_path_when_synchronous(self) -> None:
        result = webp_cache.webp_variant(
            self.source, accept="image/webp", background=False
        )
        self.assertIsNotNone(result)
        assert result is not None
        self.assertTrue(result.is_file())
        with Image.open(result) as image:
            self.assertEqual("WEBP", image.format)

    def test_reuses_existing_cache_entry(self) -> None:
        first = webp_cache.webp_variant(
            self.source, accept="image/webp", background=False
        )
        assert first is not None
        stamp = first.stat().st_mtime_ns

        second = webp_cache.webp_variant(self.source, accept="image/webp")
        self.assertEqual(first, second)
        self.assertEqual(stamp, second.stat().st_mtime_ns)

    def test_regenerated_source_invalidates_cache(self) -> None:
        cached = webp_cache.webp_variant(
            self.source, accept="image/webp", background=False
        )
        assert cached is not None

        # Simulate a map regen: rewrite the source with a newer mtime.
        _make_png(self.source)
        future = cached.stat().st_mtime + 10
        os.utime(self.source, (future, future))

        with patch.object(webp_cache, "_encode_in_background") as spawn:
            stale = webp_cache.webp_variant(self.source, accept="image/webp")
        self.assertIsNone(stale, "a stale copy must not be served")
        spawn.assert_called_once()

    def test_encode_leaves_no_temp_files(self) -> None:
        webp_cache.webp_variant(self.source, accept="image/webp", background=False)
        leftovers = [p.name for p in self.cache.iterdir() if p.name.endswith(".tmp")]
        self.assertEqual([], leftovers)

    def test_failed_encode_cleans_up_and_writes_no_cache_entry(self) -> None:
        target = webp_cache.cache_path_for(self.source)
        with patch.object(Image, "open", side_effect=OSError("broken image")):
            with self.assertRaises(OSError):
                webp_cache._encode(self.source, target)

        self.assertFalse(target.exists())
        self.assertEqual([], [p for p in self.cache.iterdir() if p.suffix == ".tmp"])

    def test_distinct_sources_get_distinct_cache_entries(self) -> None:
        other = _make_png(self.tmp / "parchment.png")
        self.assertNotEqual(
            webp_cache.cache_path_for(self.source), webp_cache.cache_path_for(other)
        )


class BaseMapNegotiationTest(unittest.TestCase):
    """`_base_map_response` picks the variant and labels the response."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.cache = self.tmp / "cache"
        patcher = patch.object(webp_cache, "_CACHE_DIR", self.cache)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self._tmp.cleanup)
        self.source = _make_png(self.tmp / "map.png")

    def _respond(self, accept, **kwargs):
        from src.api.map_routes import _base_map_response

        return _base_map_response(
            str(self.source), "original", accept, kwargs.get("inm"), None
        )

    def test_serves_png_while_cache_is_cold(self) -> None:
        with patch.object(webp_cache, "_encode_in_background"):
            response = self._respond("image/webp,*/*")
        self.assertEqual("image/png", response.media_type)

    def test_serves_webp_once_cached(self) -> None:
        webp_cache.webp_variant(self.source, accept="image/webp", background=False)
        response = self._respond("image/webp,*/*")
        self.assertEqual("image/webp", response.media_type)

    def test_never_serves_webp_to_a_client_that_cannot_display_it(self) -> None:
        webp_cache.webp_variant(self.source, accept="image/webp", background=False)
        response = self._respond("image/png")
        self.assertEqual("image/png", response.media_type)

    def test_varies_on_accept_so_caches_do_not_cross_wires(self) -> None:
        response = self._respond("image/png")
        self.assertEqual("Accept", response.headers["Vary"])
        self.assertEqual("original", response.headers["X-Map-Base"])


if __name__ == "__main__":
    unittest.main()
