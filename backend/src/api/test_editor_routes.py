"""Tests for map title editor API and validation."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest import mock

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

os.environ.setdefault("SKINS_DEV", "1")

from api.editor_validation import TitleValidationError, validate_title_tier
from api.map_access import (
    EDITOR_STAFF_PERMISSION,
    STAFF_MAP_FORBIDDEN_DETAIL,
    ensure_map_staff_write,
)
from api.map_registry import clear_map_registry_cache
from fastapi import HTTPException
from fastapi.testclient import TestClient
from server import app

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


def _staff_session(player: str) -> dict:
    return {
        "scope": "character",
        "player_uuid": player,
        "realm_id": "main",
    }


class TitleValidationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.defines_root = Path(self.tmp.name) / "defines"
        self.map_dir = self.defines_root / "main"
        self.map_dir.mkdir(parents=True)
        self._orig_defines = os.environ.get("DEFINES_DIR_OVERRIDE")
        # Patch defines_file via DEFINES_DIR on dirs module
        from src.scripts.util import dirs as dirs_module

        self._orig_defines_dir = dirs_module.DEFINES_DIR
        dirs_module.DEFINES_DIR = str(self.defines_root)

    def tearDown(self) -> None:
        from src.scripts.util import dirs as dirs_module

        dirs_module.DEFINES_DIR = self._orig_defines_dir
        self.tmp.cleanup()

    def test_valid_county(self) -> None:
        body = {
            "COUNTY_1": {
                "name": "Elvaris",
                "provinces": [1, 2, 3],
                "rgb": "180,80,80",
                "overlay": {"x": 0, "y": 0, "w": 10, "h": 10},
            }
        }
        clean = validate_title_tier("county", body, "main")
        self.assertNotIn("overlay", clean["COUNTY_1"])
        self.assertEqual(clean["COUNTY_1"]["provinces"], [1, 2, 3])

    def test_duplicate_province_rejected(self) -> None:
        body = {
            "COUNTY_1": {"name": "A", "provinces": [1], "rgb": "10,20,30"},
            "COUNTY_2": {"name": "B", "provinces": [1], "rgb": "40,50,60"},
        }
        with self.assertRaises(TitleValidationError) as ctx:
            validate_title_tier("county", body, "main")
        self.assertIn("Province 1", str(ctx.exception))

    def test_invalid_rgb_rejected(self) -> None:
        body = {"COUNTY_1": {"name": "A", "provinces": [1], "rgb": "bad"}}
        with self.assertRaises(TitleValidationError):
            validate_title_tier("county", body, "main")

    def test_duchy_requires_existing_county(self) -> None:
        (self.map_dir / "county.json").write_text(
            json.dumps({"COUNTY_1": {"name": "A", "provinces": [1], "rgb": "1,2,3"}}),
            encoding="utf-8",
        )
        body = {
            "DUCHY_1": {
                "name": "Valoris",
                "titles": ["COUNTY_MISSING"],
                "rgb": "100,100,100",
            }
        }
        with self.assertRaises(TitleValidationError) as ctx:
            validate_title_tier("duchy", body, "main")
        self.assertIn("COUNTY_MISSING", str(ctx.exception))

    def test_duchy_valid_with_child(self) -> None:
        (self.map_dir / "county.json").write_text(
            json.dumps(
                {
                    "COUNTY_1": {"name": "A", "provinces": [1], "rgb": "1,2,3"},
                    "COUNTY_2": {"name": "B", "provinces": [2], "rgb": "4,5,6"},
                }
            ),
            encoding="utf-8",
        )
        body = {
            "DUCHY_1": {
                "name": "Valoris",
                "titles": ["COUNTY_1", "COUNTY_2"],
                "rgb": "100,100,100",
            }
        }
        clean = validate_title_tier("duchy", body, "main")
        self.assertEqual(clean["DUCHY_1"]["titles"], ["COUNTY_1", "COUNTY_2"])


class MapStaffWriteTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.registry_path = Path(self.tmp.name) / "maps.yml"
        self.registry_path.write_text(TEST_REGISTRY, encoding="utf-8")
        self._orig_path = os.environ.get("MAP_REGISTRY_PATH")
        os.environ["MAP_REGISTRY_PATH"] = str(self.registry_path)
        clear_map_registry_cache()

    def tearDown(self) -> None:
        if self._orig_path is None:
            os.environ.pop("MAP_REGISTRY_PATH", None)
        else:
            os.environ["MAP_REGISTRY_PATH"] = self._orig_path
        clear_map_registry_cache()
        self.tmp.cleanup()

    def test_public_map_requires_staff_session(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            ensure_map_staff_write("main", None)
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertEqual(ctx.exception.detail, STAFF_MAP_FORBIDDEN_DETAIL)

    def test_public_map_allows_staff(self) -> None:
        player = "00000000-0000-4000-8000-000000000099"
        with mock.patch(
            "api.map_access.get_character_session",
            return_value=_staff_session(player),
        ), mock.patch(
            "api.map_access.has_map_staff_access",
            return_value=True,
        ) as check:
            entry = ensure_map_staff_write("main", "Bearer token")
        self.assertEqual(entry.id, "main")
        check.assert_called_once_with(player, "main", EDITOR_STAFF_PERMISSION)


class EditorRoutesApiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.registry_path = root / "maps.yml"
        self.registry_path.write_text(TEST_REGISTRY, encoding="utf-8")
        self.defines_root = root / "defines"
        self.input_root = root / "input"
        self.map_dir = self.defines_root / "main"
        self.input_map_dir = self.input_root / "main"
        self.map_dir.mkdir(parents=True)
        self.input_map_dir.mkdir(parents=True)

        (self.map_dir / "provinces.txt").write_text(
            "1 = 58,132,60;plains;78\n2 = 40,123,42;plains;85\n",
            encoding="utf-8",
        )

        self._orig_registry = os.environ.get("MAP_REGISTRY_PATH")
        os.environ["MAP_REGISTRY_PATH"] = str(self.registry_path)
        clear_map_registry_cache()

        from src.scripts.util import dirs as dirs_module

        self._orig_defines_dir = dirs_module.DEFINES_DIR
        self._orig_input_dir = dirs_module.INPUT_DIR
        dirs_module.DEFINES_DIR = str(self.defines_root)
        dirs_module.INPUT_DIR = str(self.input_root)

        self._write_test_provinces_png()
        from src.scripts.province_id_grid import write_province_id_grid_file

        write_province_id_grid_file("main")

        self.player = f"00000000-0000-4000-8000-{uuid.uuid4().hex[:12]}"
        self.auth = "Bearer staff-token"
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()
        from src.scripts.util import dirs as dirs_module

        dirs_module.DEFINES_DIR = self._orig_defines_dir
        dirs_module.INPUT_DIR = self._orig_input_dir
        if self._orig_registry is None:
            os.environ.pop("MAP_REGISTRY_PATH", None)
        else:
            os.environ["MAP_REGISTRY_PATH"] = self._orig_registry
        clear_map_registry_cache()
        self.tmp.cleanup()

    def _write_test_provinces_png(self) -> None:
        from PIL import Image

        png_path = self.input_map_dir / "provinces.png"
        img = Image.new("RGBA", (2, 2))
        pixels = [
            (58, 132, 60, 255),
            (40, 123, 42, 255),
            (58, 132, 60, 255),
            (40, 123, 42, 255),
        ]
        for i, rgba in enumerate(pixels):
            img.putpixel((i % 2, i // 2), rgba)
        img.save(png_path)

    def _staff_patches(self):
        return (
            mock.patch(
                "src.api.map_access.get_character_session",
                return_value=_staff_session(self.player),
            ),
            mock.patch(
                "src.api.map_access.has_map_staff_access",
                return_value=True,
            ),
        )

    def test_post_titles_county_no_auth_403(self) -> None:
        r = self.client.post(
            "/main/editor/titles/county",
            json={"COUNTY_1": {"name": "A", "provinces": [1], "rgb": "1,2,3"}},
        )
        self.assertEqual(r.status_code, 403)

    def test_post_titles_county_staff_writes_file(self) -> None:
        payload = {
            "COUNTY_1": {
                "name": "Elvaris",
                "provinces": [1, 2],
                "rgb": "180,80,80",
            }
        }
        staff_session_patch, staff_access_patch = self._staff_patches()
        with staff_session_patch, staff_access_patch:
            r = self.client.post(
                "/main/editor/titles/county",
                json=payload,
                headers={"Authorization": self.auth},
            )
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data["ok"])
        self.assertEqual(data["count"], 1)

        written = json.loads((self.map_dir / "county.json").read_text(encoding="utf-8"))
        self.assertEqual(written["COUNTY_1"]["name"], "Elvaris")
        self.assertNotIn("overlay", written["COUNTY_1"])

    def test_post_titles_duplicate_province_400(self) -> None:
        payload = {
            "COUNTY_1": {"name": "A", "provinces": [1], "rgb": "10,20,30"},
            "COUNTY_2": {"name": "B", "provinces": [1], "rgb": "40,50,60"},
        }
        staff_session_patch, staff_access_patch = self._staff_patches()
        with staff_session_patch, staff_access_patch:
            r = self.client.post(
                "/main/editor/titles/county",
                json=payload,
                headers={"Authorization": self.auth},
            )
        self.assertEqual(r.status_code, 400)

    def test_upload_county_no_auth_403(self) -> None:
        r = self.client.post(
            "/main/data/upload/county",
            json={"COUNTY_1": {"name": "A", "provinces": [1], "rgb": "1,2,3"}},
        )
        self.assertEqual(r.status_code, 403)

    def test_get_editor_provinces_staff(self) -> None:
        staff_session_patch, staff_access_patch = self._staff_patches()
        with staff_session_patch, staff_access_patch:
            r = self.client.get(
                "/main/editor/provinces",
                headers={"Authorization": self.auth},
            )
        self.assertEqual(r.status_code, 200)
        provinces = r.json()["provinces"]
        self.assertEqual(len(provinces), 2)
        self.assertEqual(provinces[0]["id"], 1)
        self.assertEqual(provinces[0]["rgb"], "58,132,60")
        self.assertEqual(provinces[0]["terrain"], "plains")
        self.assertEqual(provinces[0]["fertility"], 78)

    def test_get_editor_province_pick_no_auth_403(self) -> None:
        r = self.client.get("/main/editor/pick/provinces")
        self.assertEqual(r.status_code, 403)

    def test_get_editor_province_pick_staff(self) -> None:
        staff_session_patch, staff_access_patch = self._staff_patches()
        with staff_session_patch, staff_access_patch:
            r = self.client.get(
                "/main/editor/pick/provinces",
                headers={"Authorization": self.auth},
            )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.headers.get("content-type"), "image/png")
        self.assertTrue(len(r.content) > 0)

    def test_get_editor_province_index_no_auth_403(self) -> None:
        r = self.client.get("/main/editor/province-index")
        self.assertEqual(r.status_code, 403)

    def test_get_editor_province_index_staff(self) -> None:
        staff_session_patch, staff_access_patch = self._staff_patches()
        with staff_session_patch, staff_access_patch:
            r = self.client.get(
                "/main/editor/province-index",
                headers={"Authorization": self.auth},
            )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(
            r.headers.get("content-type"), "application/octet-stream"
        )
        self.assertTrue(len(r.content) > 8)
        import gzip
        import struct

        payload = gzip.decompress(r.content)
        width, height = struct.unpack("<ii", payload[:8])
        self.assertEqual(width, 2)
        self.assertEqual(height, 2)
        self.assertEqual(len(payload), 8 + width * height * 2)

    def test_get_editor_province_index_missing_grid_404(self) -> None:
        from src.scripts.province_id_grid import GRID_FILENAME
        from src.scripts.util.dirs import defines_file

        grid_path = defines_file("main", GRID_FILENAME)
        if os.path.isfile(grid_path):
            os.remove(grid_path)

        staff_session_patch, staff_access_patch = self._staff_patches()
        with staff_session_patch, staff_access_patch:
            r = self.client.get(
                "/main/editor/province-index",
                headers={"Authorization": self.auth},
            )
        self.assertEqual(r.status_code, 404)
        detail = r.json().get("detail", "")
        self.assertIn("build_province_id_grid", detail)

    def test_editor_regen_staff_starts_background(self) -> None:
        staff_session_patch, staff_access_patch = self._staff_patches()
        with staff_session_patch, staff_access_patch, mock.patch(
            "src.api.editor_routes.run_regeneration",
            new_callable=mock.AsyncMock,
        ):
            r = self.client.post(
                "/main/editor/regen/fullregen:county",
                headers={"Authorization": self.auth},
            )
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.json()["ok"])


if __name__ == "__main__":
    unittest.main()
