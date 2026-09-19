"""Path parameters must never walk out of the directory their route serves.

Regression tests for an arbitrary file read: the map name was access-checked,
but the other path parameters were joined into filesystem paths unvalidated.
Starlette decodes `%5C` to `\\`, which Windows treats as a separator, so
`/main/data/..%5Cdev%5Cnation` read the staff-only `dev` map through the
public `main` map's gate. The `%5C` cases therefore only reproduce the leak on
Windows; the direct handler calls below use plain `..` and absolute paths,
which reproduce it on any OS.
"""

from __future__ import annotations

import importlib
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

os.environ.setdefault("SKINS_DEV", "1")

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.api import data_routes, file_routes  # noqa: E402
from src.api.map_registry import clear_map_registry_cache  # noqa: E402
from src.api.path_safety import (  # noqa: E402
    is_safe_filename,
    is_safe_segment,
    resolve_within,
)
from src.scripts.util import dirs  # noqa: E402

TEST_REGISTRY = """
maps:
  - id: main
    public: true
    display_name: Adavaar
    realm_id: main
  - id: dev
    public: false
    display_name: Adavaar
    realm_id: dev
    staff_permission: tfmc.map.staff
"""

SECRET = b"SECRET-DO-NOT-SERVE"


class _MapFixture:
    """Temp input/defines/output tree with a public `main` and staff `dev` map."""

    def _build_tree(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name).resolve()
        self.root = root

        registry = root / "maps.yml"
        registry.write_text(TEST_REGISTRY, encoding="utf-8")
        self._orig_registry = os.environ.get("MAP_REGISTRY_PATH")
        self._orig_ui_dev = os.environ.pop("CHARACTER_UI_DEV", None)
        os.environ["MAP_REGISTRY_PATH"] = str(registry)
        clear_map_registry_cache()
        self.addCleanup(self._restore_env)

        # Files outside every served root.
        (root / "config").mkdir()
        (root / "config" / "maps.yml").write_bytes(SECRET)
        (root / ".env").write_bytes(SECRET)
        (root / "secret.png").write_bytes(SECRET)
        (root / "secret.json").write_bytes(SECRET)

        self.input_dir = root / "input"
        self.defines_dir = root / "defines"
        self.output_dir = root / "output"

        (self.input_dir / "main").mkdir(parents=True)
        (self.input_dir / "main" / "provinces.png").write_bytes(b"provinces")

        (self.defines_dir / "main").mkdir(parents=True)
        (self.defines_dir / "main" / "nation.json").write_text(
            '{"public": true}', encoding="utf-8"
        )
        (self.defines_dir / "main" / "province_centroids.json").write_text(
            "{}", encoding="utf-8"
        )
        (self.defines_dir / "dev").mkdir(parents=True)
        (self.defines_dir / "dev" / "nation.json").write_bytes(SECRET)

        main_out = self.output_dir / "main"
        (main_out / "maps").mkdir(parents=True)
        (main_out / "maps" / "nation_map.png").write_bytes(b"nation-map")
        (main_out / "regions" / "nation").mkdir(parents=True)
        (main_out / "regions" / "nation" / "1_2_3.png").write_bytes(b"region")
        (main_out / "regions" / "nation" / "1_2_3_hover.png").write_bytes(b"hover")
        (main_out / "regions" / "stray.png").write_bytes(SECRET)
        banners = main_out / "banners" / "nation"
        banners.mkdir(parents=True)
        (banners / "109_62_19.png").write_bytes(b"banner")
        (banners / "notpng.json").write_bytes(SECRET)
        (banners / "noext").write_bytes(SECRET)
        (main_out / "zoc").mkdir()
        (main_out / "zoc" / "lanhold.png").write_bytes(b"zoc")

        (self.output_dir / "dev" / "maps").mkdir(parents=True)
        (self.output_dir / "dev" / "maps" / "nation_map.png").write_bytes(SECRET)

        self._orig_dirs = (dirs.INPUT_DIR, dirs.DEFINES_DIR, dirs.OUTPUT_DIR)
        self._orig_output_base = file_routes.OUTPUT_BASE
        dirs.INPUT_DIR = str(self.input_dir)
        dirs.DEFINES_DIR = str(self.defines_dir)
        dirs.OUTPUT_DIR = str(self.output_dir)
        file_routes.OUTPUT_BASE = self.output_dir
        self.addCleanup(self._restore_dirs)

        # Display overlays would otherwise start a real WebP encode.
        webp = patch.object(file_routes, "webp_variant", return_value=None)
        webp.start()
        self.addCleanup(webp.stop)

    def _restore_env(self) -> None:
        if self._orig_registry is None:
            os.environ.pop("MAP_REGISTRY_PATH", None)
        else:
            os.environ["MAP_REGISTRY_PATH"] = self._orig_registry
        if self._orig_ui_dev is not None:
            os.environ["CHARACTER_UI_DEV"] = self._orig_ui_dev
        clear_map_registry_cache()

    def _restore_dirs(self) -> None:
        dirs.INPUT_DIR, dirs.DEFINES_DIR, dirs.OUTPUT_DIR = self._orig_dirs
        file_routes.OUTPUT_BASE = self._orig_output_base


class PathTraversalHttpTest(_MapFixture, unittest.TestCase):
    def setUp(self) -> None:
        self._build_tree()
        app = FastAPI()
        app.include_router(file_routes.file_router)
        app.include_router(data_routes.data_router)
        self.client = TestClient(app)
        self.addCleanup(self.client.close)

    def assertRejected(self, url: str) -> None:
        response = self.client.get(url)
        self.assertGreaterEqual(response.status_code, 400, url)
        self.assertLess(response.status_code, 500, url)
        self.assertNotIn(SECRET, response.content, url)

    # --- backslash (%5C) traversal -------------------------------------------

    def test_banner_backslash_traversal_to_config(self) -> None:
        self.assertRejected(
            "/main/banners/x/..%5C..%5C..%5C..%5Cconfig%5Cmaps.yml"
        )

    def test_banner_backslash_traversal_in_mode(self) -> None:
        self.assertRejected("/main/banners/..%5C..%5C..%5C..%5Cconfig/maps.yml")

    def test_data_backslash_traversal_into_staff_map(self) -> None:
        # The gate itself is intact for the staff map ...
        self.assertEqual(403, self.client.get("/dev/data/nation").status_code)
        # ... and must not be sidestepped through the public one.
        self.assertRejected("/main/data/..%5Cdev%5Cnation")

    def test_mapdata_backslash_traversal_into_staff_map(self) -> None:
        self.assertRejected("/main/mapdata/..%5C..%5Cdev%5Cmaps%5Cnation")

    def test_region_backslash_traversal_into_staff_map(self) -> None:
        self.assertRejected(
            "/main/regions/nation/..%5C..%5C..%5Cdev%5Cmaps%5Cnation_map"
        )
        self.assertRejected(
            "/main/regions/..%5C..%5C..%5Cdev%5Cmaps/nation_map"
        )

    def test_zoc_backslash_traversal(self) -> None:
        self.assertRejected("/main/zoc/..%5C..%5Cdev%5Cmaps%5Cnation_map.png")

    # --- dot-dot (encoded so the client does not collapse it) ---------------

    def test_encoded_dot_dot_segments(self) -> None:
        for url in (
            "/main/regions/%2E%2E/stray",
            "/main/regions/nation/%2E%2E",
            "/main/banners/%2E%2E/109_62_19.png",
            "/main/data/%2E%2E",
            "/main/mapdata/%2E%2E",
        ):
            self.assertRejected(url)

    # --- banner extension ----------------------------------------------------

    def test_banner_serves_only_png(self) -> None:
        self.assertRejected("/main/banners/nation/notpng.json")
        self.assertRejected("/main/banners/nation/noext")

    # --- legitimate requests keep working ------------------------------------

    def test_legitimate_requests_still_served(self) -> None:
        for url, body in (
            ("/main/banners/nation/109_62_19.png", b"banner"),
            ("/main/regions/nation/1_2_3", b"region"),
            ("/main/regions/nation/1_2_3_hover", b"hover"),
            ("/main/regions/nation/1_2_3.png", b"region"),
            ("/main/mapdata/nation", b"nation-map"),
            ("/main/mapdata/province", b"provinces"),
            ("/main/zoc/lanhold.png", b"zoc"),
            ("/main/data/nation", b'{"public": true}'),
            ("/main/data/province_centroids", b"{}"),
        ):
            response = self.client.get(url)
            self.assertEqual(200, response.status_code, url)
            self.assertEqual(body, response.content, url)

    def test_paths_use_normalised_map_id(self) -> None:
        # " MaIn" passes the gate as "main"; the files must be read from the
        # registry id's directory, not from a directory named after the segment.
        for url in (
            "/%20MaIn/mapdata/nation",
            "/%20MaIn/regions/nation/1_2_3",
            "/%20MaIn/banners/nation/109_62_19.png",
            "/%20MaIn/data/nation",
        ):
            self.assertEqual(200, self.client.get(url).status_code, url)

    def test_upload_mode_cannot_escape_map_dir(self) -> None:
        with patch.object(data_routes, "require_localhost"), patch(
            "src.scripts.chronicle.capture.capture_if_due"
        ):
            response = self.client.post(
                "/main/data/upload/..%5C..%5Cevil", json={"a": 1}
            )
        self.assertEqual(400, response.status_code)
        self.assertFalse((self.root / "evil.json").exists())


class PathTraversalHandlerTest(_MapFixture, unittest.IsolatedAsyncioTestCase):
    """Direct handler calls: `..` and absolute paths reach the handler as-is."""

    def setUp(self) -> None:
        self._build_tree()

    async def _status(self, coro) -> int:
        try:
            response = await coro
        except HTTPException as exc:
            return exc.status_code
        body = getattr(response, "body", b"") or b""
        self.assertNotIn(SECRET, body)
        return response.status_code

    def _headers(self) -> dict:
        return {"authorization": None, "if_none_match": None, "if_modified_since": None}

    def _image_headers(self) -> dict:
        return {**self._headers(), "accept": None}

    async def assertRejected(self, coro) -> None:
        status = await self._status(coro)
        self.assertGreaterEqual(status, 400)
        self.assertLess(status, 500)

    async def test_region_dot_dot(self) -> None:
        await self.assertRejected(
            file_routes.get_region_file("main", "..", "stray", **self._image_headers())
        )
        await self.assertRejected(
            file_routes.get_region_file(
                "main", "nation", "../../../dev/maps/nation_map", **self._image_headers()
            )
        )

    async def test_region_absolute_path(self) -> None:
        absolute = str(self.output_dir / "dev" / "maps" / "nation_map")
        await self.assertRejected(
            file_routes.get_region_file("main", "nation", absolute, **self._image_headers())
        )
        await self.assertRejected(
            file_routes.get_region_file("main", str(self.root), "secret", **self._image_headers())
        )

    async def test_banner_dot_dot_and_absolute(self) -> None:
        await self.assertRejected(
            file_routes.get_banner_file(
                "main", "..", "../../../secret.png", **self._image_headers()
            )
        )
        await self.assertRejected(
            file_routes.get_banner_file(
                "main", "nation", str(self.root / "secret.png"), **self._image_headers()
            )
        )
        await self.assertRejected(
            file_routes.get_banner_file(
                "main", "nation", str(self.root / "config" / "maps.yml"), **self._image_headers()
            )
        )

    async def test_mapdata_dot_dot_into_staff_map(self) -> None:
        await self.assertRejected(
            file_routes.get_map_file("main", "../../dev/maps/nation", **self._headers())
        )

    async def test_data_dot_dot_and_absolute_into_staff_map(self) -> None:
        await self.assertRejected(
            data_routes.get_map_name_data("main", "../dev/nation", **self._headers())
        )
        await self.assertRejected(
            data_routes.get_map_name_data(
                "main", str(self.defines_dir / "dev" / "nation"), **self._headers()
            )
        )
        await self.assertRejected(
            data_routes.get_map_name_data("main", str(self.root / "secret"), **self._headers())
        )


class SubmissionFileTraversalTest(unittest.TestCase):
    """Staff/plugin submission file routes join the submission id into a path."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        (self.root / "secret.txt").write_bytes(SECRET)

    def test_drink_file_routes_reject_traversal_in_submission_id(self) -> None:
        routes = importlib.import_module("src.api.drinks_routes")
        drinks_dir = self.root / "drinks"
        sub = drinks_dir / "submissions" / "abc_drink"
        sub.mkdir(parents=True)
        (sub / "texture.png").write_bytes(b"texture")

        resolver_globals = routes.resolve_drink_submission_file.__globals__
        with patch.dict(
            resolver_globals, {"db": SimpleNamespace(DRINKS_DIR=drinks_dir)}
        ), patch.object(
            routes, "skins_db", SimpleNamespace(DRINKS_DIR=drinks_dir), create=True
        ), patch.object(routes, "_require_staff"), patch.object(
            routes, "_require_plugin"
        ):
            for handler in (routes.staff_file, routes.plugin_file):
                for sid, name in (
                    ("../..", "secret.txt"),
                    ("..", "../secret.txt"),
                    ("..\\..", "secret.txt"),
                    (str(self.root), "secret.txt"),
                ):
                    with self.assertRaises(HTTPException) as ctx:
                        handler(sid, name, None)
                    self.assertEqual(404, ctx.exception.status_code)

                response = handler("abc_drink", "texture.png", None)
                self.assertEqual(200, response.status_code)

    def test_skin_file_routes_reject_traversal_in_submission_id(self) -> None:
        routes = importlib.import_module("src.api.skins_routes")
        skins_dir = self.root / "skins"
        sub = skins_dir / "abc_skin"
        sub.mkdir(parents=True)
        (sub / "abc_skin.png").write_bytes(b"texture")

        # Stand-in for the library resolver (which also regenerates pack
        # models): a plain join, so only the route's own guards stand between
        # the parameters and the filesystem.
        def naive_resolver(submission_id: str, filename: str):
            path = skins_dir / submission_id / filename
            return path if path.is_file() else None

        with patch.dict(
            routes.staff_file.__globals__, {"resolve_submission_file": naive_resolver}
        ), patch.object(
            routes, "skins_db", SimpleNamespace(SKINS_DIR=skins_dir), create=True
        ), patch.object(routes, "_require_staff"), patch.object(
            routes, "_require_plugin"
        ):
            for handler in (routes.staff_file, routes.plugin_file):
                for sid, name in (
                    ("..", "secret.txt"),
                    ("..\\..", "secret.txt"),
                    (str(self.root), "secret.txt"),
                    ("abc_skin", "..\\..\\secret.txt"),
                ):
                    with self.assertRaises(HTTPException) as ctx:
                        handler(sid, name, None)
                    self.assertEqual(404, ctx.exception.status_code)

                response = handler("abc_skin", "abc_skin.png", None)
                self.assertEqual(200, response.status_code)


class PathSafetyHelperTest(unittest.TestCase):
    def test_segment_pattern(self) -> None:
        for ok in ("nation", "1_2_3_hover", "province-centroids", "County2"):
            self.assertTrue(is_safe_segment(ok), ok)
        for bad in (
            "", ".", "..", "a/b", "a\\b", "..\\dev", "C:", "x.png", "a b",
            "nation\n", "/etc/passwd", "%2e%2e", None, 5,
        ):
            self.assertFalse(is_safe_segment(bad), bad)

    def test_filename_pattern(self) -> None:
        for ok in ("x.png", "review_sheet.png", "abc_skin.json", "noext"):
            self.assertTrue(is_safe_filename(ok), ok)
        for bad in (".", "..", ".env", "a..png", "a/b.png", "a\\b.png", "x.", "x.png\n"):
            self.assertFalse(is_safe_filename(bad), bad)

    def test_resolve_within(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "root"
            root.mkdir()
            self.assertEqual(
                (root / "a" / "b.png").resolve(),
                resolve_within(root, root / "a" / "b.png"),
            )
            self.assertIsNone(resolve_within(root, root / ".." / "b.png"))
            self.assertIsNone(resolve_within(root, root))
            self.assertIsNone(resolve_within(root, Path(tmp) / "rootx" / "b.png"))


if __name__ == "__main__":
    unittest.main()
