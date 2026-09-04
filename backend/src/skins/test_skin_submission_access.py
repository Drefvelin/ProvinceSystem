"""Skin submission access control (scope + one active submission per code)."""

from __future__ import annotations

import importlib
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_BACKEND_SRC = Path(__file__).resolve().parents[1]
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))
_BACKEND = Path(__file__).resolve().parents[2]
if str(_BACKEND) not in sys.path:
    sys.path.insert(0, str(_BACKEND))

TINY_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82"
)


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
    for name in (
        "skins.codes",
        "src.skins.codes",
        "skins.submissions",
        "src.skins.submissions",
    ):
        if name in sys.modules:
            importlib.reload(sys.modules[name])
    return db_mod


class SkinSubmissionAccessTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        root = Path(self.tmp.name)
        self.db_path = root / "province.db"
        self.skins_dir = root / "skins"
        self.skins_dir.mkdir(parents=True, exist_ok=True)

        db_mod = _sync_temp_db(root, self.db_path)
        db_mod.SKINS_DIR = self.skins_dir
        self._db_mod = db_mod
        self._orig_db = db_mod.DB_PATH
        self._orig_drinks = db_mod.DRINKS_DIR
        self._orig_data = db_mod.DATA_DIR
        self._orig_skins = db_mod.SKINS_DIR
        self._orig_wardrobe = db_mod.WARDROBE_DIR
        db_mod.migrate()

    def tearDown(self) -> None:
        db_mod = self._db_mod
        db_mod.DB_PATH = self._orig_db
        db_mod.DRINKS_DIR = self._orig_drinks
        db_mod.DATA_DIR = self._orig_data
        db_mod.SKINS_DIR = self._orig_skins
        db_mod.WARDROBE_DIR = self._orig_wardrobe
        self.tmp.cleanup()

    def _link_player(self, uuid: str = "player-1", name: str = "TestPlayer") -> None:
        from skins.db import connect

        with connect() as conn:
            conn.execute(
                "DELETE FROM discord_links WHERE player_uuid = ? OR discord_user_id = ?",
                (uuid, "discord-1"),
            )
            conn.execute(
                """
                INSERT INTO discord_links (
                    player_uuid, discord_user_id, minecraft_name,
                    discord_username, linked_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (uuid, "discord-1", name, "Tester", "2026-01-01T00:00:00Z"),
            )
            conn.commit()

    def _seed_entitlements(self, uuid: str = "player-1") -> None:
        from characters.rpc_player_meta import upsert_rpc_player_meta

        upsert_rpc_player_meta(
            {
                "player_uuid": uuid,
                "skin_kinds": ["handheld"],
                "name_colour_stops": 2,
                "max_3d_pair_bytes": 30720,
            }
        )

    def _skin_session(self, uuid: str = "player-1"):
        from skins.codes import get_session, issue_code, redeem_code

        issued = issue_code(uuid, "skin")
        redeemed = redeem_code(issued["code"])
        return get_session(redeemed["session_token"])

    def _submit_handheld(self, session_row, display_name: str = "Test Sword"):
        from skins.submissions import create_submission

        with mock.patch("skins.submissions.write_submission_files"):
            return create_submission(
                session_row,
                "handheld",
                display_name,
                {"texture": TINY_PNG},
                base_set="swords",
            )

    def test_assert_no_active_submission_blocks_pending(self) -> None:
        from skins.submissions import SubmissionError, _assert_no_active_submission_for_code

        self._link_player()
        session = self._skin_session()
        code_id = session["code_id"]
        from skins.db import connect

        with connect() as conn:
            conn.execute(
                """
                INSERT INTO submissions (
                    id, player_uuid, code_id, kind, slug, display_name,
                    status, dir_path, created_at, discord_user_id, staff, realm_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "testplayer-testsword",
                    "player-1",
                    code_id,
                    "handheld",
                    "testplayer-testsword",
                    "Test Sword",
                    "pending",
                    "skins/test",
                    "2026-01-01T00:00:00Z",
                    "discord-1",
                    0,
                    "main",
                ),
            )
            conn.commit()

        with self.assertRaises(SubmissionError) as ctx:
            _assert_no_active_submission_for_code(code_id)
        self.assertIn("active submission", str(ctx.exception).lower())

    def test_second_upload_blocked_while_pending(self) -> None:
        from skins.submissions import SubmissionError

        self._link_player()
        self._seed_entitlements()
        session = self._skin_session()
        self._submit_handheld(session, "First Sword")

        with self.assertRaises(SubmissionError) as ctx:
            self._submit_handheld(session, "Second Sword")
        self.assertIn("active submission", str(ctx.exception).lower())

    def test_deny_allows_resubmit(self) -> None:
        from skins.submissions import deny_submission

        self._link_player()
        self._seed_entitlements()
        session = self._skin_session()
        first = self._submit_handheld(session, "Denied Sword")
        deny_submission(first["id"], "Needs changes")
        second = self._submit_handheld(session, "Fixed Sword")
        self.assertEqual("pending", second["status"])
        self.assertNotEqual(first["id"], second["id"])

    def test_rollback_clears_redeemed_at(self) -> None:
        from skins.db import connect
        from skins.submissions import deny_submission

        self._link_player()
        self._seed_entitlements()
        session = self._skin_session()
        created = self._submit_handheld(session, "Redeem Sword")
        code_id = session["code_id"]

        with connect() as conn:
            row = conn.execute(
                "SELECT redeemed_at FROM codes WHERE id = ?",
                (code_id,),
            ).fetchone()
        self.assertIsNotNone(row["redeemed_at"])

        deny_submission(created["id"], "Try again")

        with connect() as conn:
            row = conn.execute(
                "SELECT redeemed_at FROM codes WHERE id = ?",
                (code_id,),
            ).fetchone()
        self.assertIsNone(row["redeemed_at"])

    def test_profile_session_can_still_create_via_lore_path(self) -> None:
        """Scope is enforced on HTTP routes only, not create_submission()."""
        from skins.codes import get_session, issue_code, redeem_profile_code

        self._link_player()
        self._seed_entitlements()
        issued = issue_code("player-1", "profile")
        redeemed = redeem_profile_code(issued["code"])
        session = get_session(redeemed["session_token"])
        self.assertEqual(session["scope"], "profile")

        out = self._submit_handheld(session, "Lore Sword")
        self.assertEqual("pending", out["status"])

    def test_rollback_pending_if_unreferenced(self) -> None:
        from skins.db import connect
        from skins.submissions import rollback_pending_submission_if_unreferenced

        self._link_player()
        self._seed_entitlements()
        session = self._skin_session()
        created = self._submit_handheld(session, "Orphan Sword")
        sid = created["id"]
        code_id = session["code_id"]

        with connect() as conn:
            row = conn.execute(
                "SELECT redeemed_at FROM codes WHERE id = ?",
                (code_id,),
            ).fetchone()
        self.assertIsNotNone(row["redeemed_at"])

        self.assertTrue(
            rollback_pending_submission_if_unreferenced(
                sid, player_uuid="player-1"
            )
        )
        with connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM submissions WHERE id = ?",
                (sid,),
            ).fetchone()
            code_row = conn.execute(
                "SELECT redeemed_at FROM codes WHERE id = ?",
                (code_id,),
            ).fetchone()
        self.assertIsNone(row)
        self.assertIsNone(code_row["redeemed_at"])

    def test_rollback_skips_when_lore_row_still_references(self) -> None:
        from skins.db import connect
        from skins.submissions import rollback_pending_submission_if_unreferenced

        self._link_player()
        self._seed_entitlements()
        session = self._skin_session()
        created = self._submit_handheld(session, "Referenced Sword")
        sid = created["id"]

        with connect() as conn:
            conn.execute(
                """
                INSERT INTO lore_item_customisations (
                    player_uuid, character_id, kit_key, submission_id,
                    state, updated_at, realm_id
                ) VALUES (?, ?, 'kit_a', ?, 'pending_skin', ?, 'main')
                """,
                ("player-1", "char-1", sid, "2026-01-01T00:00:00Z"),
            )
            conn.commit()

        self.assertFalse(
            rollback_pending_submission_if_unreferenced(
                sid, player_uuid="player-1"
            )
        )
        with connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM submissions WHERE id = ?",
                (sid,),
            ).fetchone()
        self.assertIsNotNone(row)

    def test_rollback_batch_dedupes_ids(self) -> None:
        from skins.submissions import rollback_pending_submissions_if_unreferenced

        self._link_player()
        self._seed_entitlements()
        session = self._skin_session()
        created = self._submit_handheld(session, "Batch Orphan")
        sid = created["id"]

        count = rollback_pending_submissions_if_unreferenced(
            [sid, sid, ""],
            player_uuid="player-1",
        )
        self.assertEqual(1, count)


if __name__ == "__main__":
    unittest.main()
