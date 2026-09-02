"""Tests for cancelling pending web character creates."""

from __future__ import annotations

import gc
import importlib
import sys
import tempfile
import unittest
from pathlib import Path

_BACKEND_SRC = Path(__file__).resolve().parents[1]
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))
_BACKEND = Path(__file__).resolve().parents[2]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

NOW = "2026-01-01T00:00:00Z"
PNG = b"\x89PNG\r\n\x1a\n-not-a-real-png"
PLAYER = "11111111-1111-4111-8111-111111111111"
OTHER = "22222222-2222-4222-8222-222222222222"
CREATE_ID = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
REALM = "main"


class DeletePendingCreateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        root = Path(self.tmp.name)
        self.root = root

        db_mod = importlib.import_module("src.skins.db")
        self._db_mod = db_mod
        sys.modules["src.skins.db"] = db_mod
        self._orig_db = db_mod.DB_PATH
        self._orig_data = db_mod.DATA_DIR
        self._orig_drinks = db_mod.DRINKS_DIR
        self._orig_skins = db_mod.SKINS_DIR
        self._orig_wardrobe = db_mod.WARDROBE_DIR
        db_mod.DATA_DIR = root
        db_mod.DB_PATH = root / "province.db"
        db_mod.DRINKS_DIR = root / "drinks"
        db_mod.SKINS_DIR = root / "skins"
        db_mod.WARDROBE_DIR = root / "wardrobe"
        db_mod.migrate()

        wardrobe_mod = importlib.import_module("src.characters.wardrobe")
        self._wardrobe_mod = wardrobe_mod
        self._orig_w_data = wardrobe_mod.DATA_DIR
        self._orig_w_dir = wardrobe_mod.WARDROBE_DIR
        wardrobe_mod.DATA_DIR = root
        wardrobe_mod.WARDROBE_DIR = root / "wardrobe"

        self._seed_pending()

    def tearDown(self) -> None:
        db_mod = self._db_mod
        db_mod.DB_PATH = self._orig_db
        db_mod.DATA_DIR = self._orig_data
        db_mod.DRINKS_DIR = self._orig_drinks
        db_mod.SKINS_DIR = self._orig_skins
        db_mod.WARDROBE_DIR = self._orig_wardrobe
        self._wardrobe_mod.DATA_DIR = self._orig_w_data
        self._wardrobe_mod.WARDROBE_DIR = self._orig_w_dir
        gc.collect()
        self.tmp.cleanup()

    def _write_png(self, relpath: str) -> Path:
        path = self.root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(PNG)
        return path

    def _seed_pending(self, *, status: str = "pending", player_uuid: str = PLAYER) -> None:
        from src.skins.db import connect

        png_rel = f"wardrobe/pending/{CREATE_ID}/base.png"
        self._write_png(png_rel)
        with connect() as conn:
            conn.execute(
                """
                INSERT INTO character_creates (
                    id, player_uuid, payload, status, created_at, realm_id
                ) VALUES (?, ?, '{"name":"Test"}', ?, ?, ?)
                """,
                (CREATE_ID, player_uuid, status, NOW, REALM),
            )
            conn.execute(
                """
                INSERT INTO character_create_wardrobe (
                    create_id, slot, png_relpath, updated_at
                ) VALUES (?, 'base', ?, ?)
                """,
                (CREATE_ID, png_rel, NOW),
            )
            conn.execute(
                """
                INSERT INTO lore_item_customisations (
                    player_uuid, character_id, kit_key, updated_at, realm_id
                ) VALUES (?, ?, 'kit_a', ?, ?)
                """,
                (player_uuid, CREATE_ID, NOW, REALM),
            )
            conn.commit()

    def _count(self, table: str, **where: str) -> int:
        from src.skins.db import connect

        clauses = " AND ".join(f"{k} = ?" for k in where)
        sql = f"SELECT COUNT(*) AS n FROM {table}"
        if clauses:
            sql += f" WHERE {clauses}"
        with connect() as conn:
            row = conn.execute(sql, tuple(where.values())).fetchone()
        return int(row["n"])

    def test_delete_pending_create_cleans_all(self) -> None:
        from src.characters.creates import delete_pending_create

        png_rel = f"wardrobe/pending/{CREATE_ID}/base.png"
        self.assertTrue((self.root / png_rel).is_file())
        result = delete_pending_create(PLAYER, CREATE_ID)
        self.assertEqual(result, {"ok": True, "deleted": CREATE_ID})
        self.assertEqual(self._count("character_creates", id=CREATE_ID), 0)
        self.assertEqual(
            self._count("character_create_wardrobe", create_id=CREATE_ID), 0
        )
        self.assertEqual(
            self._count(
                "lore_item_customisations",
                player_uuid=PLAYER,
                character_id=CREATE_ID,
            ),
            0,
        )
        self.assertFalse((self.root / png_rel).is_file())

    def test_wrong_player_not_found(self) -> None:
        from src.characters.creates import CreateError, delete_pending_create

        with self.assertRaises(CreateError) as ctx:
            delete_pending_create(OTHER, CREATE_ID)
        self.assertEqual(ctx.exception.status_code, 404)

    def test_applied_create_conflict(self) -> None:
        from src.skins.db import connect

        with connect() as conn:
            conn.execute(
                "UPDATE character_creates SET status = 'applied' WHERE id = ?",
                (CREATE_ID,),
            )
            conn.commit()

        from src.characters.creates import CreateError, delete_pending_create

        with self.assertRaises(CreateError) as ctx:
            delete_pending_create(PLAYER, CREATE_ID)
        self.assertEqual(ctx.exception.status_code, 409)


if __name__ == "__main__":
    unittest.main()
