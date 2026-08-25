"""Unit tests for site staff access helper."""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path
from unittest import mock

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

os.environ.setdefault("SKINS_DEV", "1")

from fastapi import HTTPException

from src.api.map_access import (
    STAFF_MAP_PERMISSION_DETAIL,
    UI_DEV_SESSION_TOKEN,
    require_site_staff,
)


class SiteStaffAccessTest(unittest.TestCase):
    def test_require_site_staff_no_auth(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            require_site_staff(None)
        self.assertEqual(401, ctx.exception.status_code)

    def test_require_site_staff_non_staff(self) -> None:
        session = {
            "scope": "profile",
            "player_uuid": "player-1",
            "realm_id": "main",
        }
        with mock.patch(
            "src.api.map_access.get_feature_session",
            return_value=session,
        ), mock.patch(
            "src.api.map_access.has_map_staff_access",
            return_value=False,
        ):
            with self.assertRaises(HTTPException) as ctx:
                require_site_staff("Bearer profile-token")
        self.assertEqual(403, ctx.exception.status_code)
        self.assertEqual(STAFF_MAP_PERMISSION_DETAIL, ctx.exception.detail)

    def test_require_site_staff_ok(self) -> None:
        session = {
            "scope": "profile",
            "player_uuid": "staff-1",
            "realm_id": "main",
        }
        with mock.patch(
            "src.api.map_access.get_feature_session",
            return_value=session,
        ), mock.patch(
            "src.api.map_access.has_map_staff_access",
            return_value=True,
        ) as check:
            out = require_site_staff("Bearer staff-token")
        self.assertEqual(session, out)
        check.assert_called_once_with("staff-1", "main", "tfmc.map.staff")

    def test_ui_dev_bypass(self) -> None:
        auth = f"Bearer {UI_DEV_SESSION_TOKEN}"
        with mock.patch(
            "src.api.map_access.is_character_ui_dev",
            return_value=True,
        ):
            out = require_site_staff(auth)
        self.assertEqual("ui-dev-player", out["player_uuid"])


if __name__ == "__main__":
    unittest.main()
