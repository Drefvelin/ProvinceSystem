"""Route tests for staff-gated code inspect."""

from __future__ import annotations

import importlib
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

from fastapi.testclient import TestClient


def _sync_temp_db(root: Path, db_path: Path) -> object:
    import skins.db as db_mod

    db_mod.DATA_DIR = root
    db_mod.DB_PATH = db_path
    db_mod.SKINS_DIR = root / "skins"
    db_mod.DRINKS_DIR = root / "drinks"
    db_mod.WARDROBE_DIR = root / "wardrobe"
    sys.modules["src.skins.db"] = db_mod
    for name in ("skins.db", "src.skins.db"):
        mod = sys.modules.get(name)
        if mod is not None:
            mod.DATA_DIR = root
            mod.DB_PATH = db_path
            mod.SKINS_DIR = root / "skins"
            mod.DRINKS_DIR = root / "drinks"
            mod.WARDROBE_DIR = root / "wardrobe"
    for name in ("src.skins.codes", "src.api.map_access"):
        if name in sys.modules:
            importlib.reload(sys.modules[name])
    return db_mod


class CodesInspectStaffGateTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        root = Path(self.tmp.name)
        self.db_path = root / "province.db"

        db_mod = _sync_temp_db(root, self.db_path)
        self._db_mod = db_mod
        self._orig_db = db_mod.DB_PATH
        self._orig_data = db_mod.DATA_DIR
        self._orig_skins = db_mod.SKINS_DIR
        self._orig_drinks = db_mod.DRINKS_DIR
        self._orig_wardrobe = db_mod.WARDROBE_DIR
        db_mod.migrate()

        from server import app

        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()
        db_mod = self._db_mod
        db_mod.DB_PATH = self._orig_db
        db_mod.DATA_DIR = self._orig_data
        db_mod.SKINS_DIR = self._orig_skins
        db_mod.DRINKS_DIR = self._orig_drinks
        db_mod.WARDROBE_DIR = self._orig_wardrobe
        self.tmp.cleanup()

    def _link_player(self, uuid: str = "player-1") -> None:
        from skins.db import connect

        with connect() as conn:
            conn.execute(
                "DELETE FROM discord_links WHERE player_uuid = ?",
                (uuid,),
            )
            conn.execute(
                """
                INSERT INTO discord_links (
                    player_uuid, discord_user_id, minecraft_name,
                    discord_username, linked_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (uuid, "discord-1", "TestPlayer", "Tester", "2026-01-01T00:00:00Z"),
            )
            conn.commit()

    def test_inspect_no_auth(self) -> None:
        res = self.client.post(
            "/skins/codes/inspect",
            json={"code": "AAAA-BBBB-CCCC"},
        )
        self.assertEqual(401, res.status_code)

    def test_inspect_non_staff(self) -> None:
        from src.skins.codes import issue_code, redeem_profile_code

        self._link_player()
        issued = issue_code("player-1", "profile")
        session = redeem_profile_code(issued["code"])

        res = self.client.post(
            "/skins/codes/inspect",
            json={"code": issued["code"]},
            headers={
                "Authorization": f"Bearer {session['session_token']}",
            },
        )
        self.assertEqual(403, res.status_code)

    def test_inspect_staff(self) -> None:
        from characters.rpc_player_meta import upsert_rpc_player_meta
        from src.skins.codes import issue_code, redeem_profile_code

        self._link_player()
        upsert_rpc_player_meta(
            {
                "player_uuid": "player-1",
                "permission_flags": {"tfmc.map.staff": True},
            }
        )
        profile_issued = issue_code("player-1", "profile")
        profile_session = redeem_profile_code(profile_issued["code"])
        skin_issued = issue_code("player-1", "skin")

        res = self.client.post(
            "/skins/codes/inspect",
            json={"code": skin_issued["code"]},
            headers={
                "Authorization": f"Bearer {profile_session['session_token']}",
            },
        )
        self.assertEqual(200, res.status_code)
        body = res.json()
        self.assertTrue(body.get("valid"))


if __name__ == "__main__":
    unittest.main()
