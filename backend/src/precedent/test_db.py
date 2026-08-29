"""Unit tests for precedent DB storage/search (psycopg2 fully mocked)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

_BACKEND_SRC = Path(__file__).resolve().parents[1]
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

import precedent.db as db  # noqa: E402


def _make_conn(cursor):
    conn = mock.MagicMock()
    conn.__enter__.return_value = conn
    conn.__exit__.return_value = False
    conn.cursor.return_value.__enter__.return_value = cursor
    conn.cursor.return_value.__exit__.return_value = False
    return conn


class MigrateTest(unittest.TestCase):
    def setUp(self) -> None:
        db._MIGRATED = False

    def tearDown(self) -> None:
        db._MIGRATED = False

    @mock.patch.dict("os.environ", {}, clear=True)
    @mock.patch("precedent.db.psycopg2.connect")
    def test_migrate_skips_without_dsn(self, mock_connect) -> None:
        db.migrate()
        mock_connect.assert_not_called()
        self.assertFalse(db._MIGRATED)

    @mock.patch.dict("os.environ", {"SUPABASE_DB_URL": "postgres://x"}, clear=True)
    @mock.patch("precedent.db.register_vector")
    @mock.patch("precedent.db.psycopg2.connect")
    def test_migrate_creates_extension_and_table_once(self, mock_connect, mock_register) -> None:
        cursor = mock.MagicMock()
        conn = _make_conn(cursor)
        mock_connect.return_value = conn

        db.migrate()

        sql_calls = [c.args[0] for c in cursor.execute.call_args_list]
        self.assertTrue(any("CREATE EXTENSION" in s for s in sql_calls))
        self.assertTrue(any("CREATE TABLE" in s for s in sql_calls))
        self.assertTrue(db._MIGRATED)
        conn.close.assert_called_once()

        db.migrate()
        mock_connect.assert_called_once()


class InsertCaseTest(unittest.TestCase):
    @mock.patch.dict("os.environ", {"SUPABASE_DB_URL": "postgres://x"}, clear=True)
    @mock.patch("precedent.db.register_vector")
    @mock.patch("precedent.db.psycopg2.connect")
    def test_insert_case_returns_id(self, mock_connect, mock_register) -> None:
        cursor = mock.MagicMock()
        cursor.fetchone.return_value = ("case-uuid-1",)
        conn = _make_conn(cursor)
        mock_connect.return_value = conn

        case_id = db.insert_case(
            logged_by="Staffer",
            players=["Alice"],
            summary="Did a thing",
            rule="1.1",
            ruling="Warned",
            punishment="warning",
            embedding=[0.1, 0.2],
        )

        self.assertEqual(case_id, "case-uuid-1")
        conn.close.assert_called_once()


class SearchSimilarTest(unittest.TestCase):
    @mock.patch.dict("os.environ", {"SUPABASE_DB_URL": "postgres://x"}, clear=True)
    @mock.patch("precedent.db.register_vector")
    @mock.patch("precedent.db.psycopg2.connect")
    def test_search_applies_relevance_cutoff(self, mock_connect, mock_register) -> None:
        cursor = mock.MagicMock()
        cursor.fetchall.return_value = [{"id": "1", "distance": 0.2}]
        conn = _make_conn(cursor)
        mock_connect.return_value = conn

        results = db.search_similar([0.1], limit=3)

        args = cursor.execute.call_args.args
        self.assertIn(db.MAX_RELEVANT_DISTANCE, args[1])
        self.assertEqual(results, [{"id": "1", "distance": 0.2}])
        conn.close.assert_called_once()

    @mock.patch.dict("os.environ", {"SUPABASE_DB_URL": "postgres://x"}, clear=True)
    @mock.patch("precedent.db.register_vector")
    @mock.patch("precedent.db.psycopg2.connect")
    def test_search_players_soft_boost_lowers_and_forwards_names(
        self, mock_connect, mock_register
    ) -> None:
        cursor = mock.MagicMock()
        cursor.fetchall.return_value = []
        conn = _make_conn(cursor)
        mock_connect.return_value = conn

        db.search_similar([0.1], limit=3, players=["  Alice ", "", "BOB"])

        args = cursor.execute.call_args.args
        self.assertIn(["alice", "bob"], args[1])

    @mock.patch.dict("os.environ", {"SUPABASE_DB_URL": "postgres://x"}, clear=True)
    @mock.patch("precedent.db.register_vector")
    @mock.patch("precedent.db.psycopg2.connect")
    def test_search_no_players_degrades_to_pure_distance(self, mock_connect, mock_register) -> None:
        cursor = mock.MagicMock()
        cursor.fetchall.return_value = []
        conn = _make_conn(cursor)
        mock_connect.return_value = conn

        db.search_similar([0.1], limit=3)

        args = cursor.execute.call_args.args
        self.assertIn([], args[1])

    @mock.patch.dict("os.environ", {"SUPABASE_DB_URL": "postgres://x"}, clear=True)
    @mock.patch("precedent.db.register_vector")
    @mock.patch("precedent.db.psycopg2.connect")
    def test_search_query_text_tokenized_for_lexical_boost(
        self, mock_connect, mock_register
    ) -> None:
        cursor = mock.MagicMock()
        cursor.fetchall.return_value = []
        conn = _make_conn(cursor)
        mock_connect.return_value = conn

        db.search_similar([0.1], limit=3, query_text="Player Xraying! a to")

        args = cursor.execute.call_args.args
        # "a"/"to" are too short (<=2 chars) to be useful tsquery terms and are dropped.
        self.assertIn(["Player", "Xraying"], args[1])


class DeleteCaseTest(unittest.TestCase):
    @mock.patch.dict("os.environ", {"SUPABASE_DB_URL": "postgres://x"}, clear=True)
    @mock.patch("precedent.db.register_vector")
    @mock.patch("precedent.db.psycopg2.connect")
    def test_delete_case_found(self, mock_connect, mock_register) -> None:
        cursor = mock.MagicMock()
        cursor.rowcount = 1
        conn = _make_conn(cursor)
        mock_connect.return_value = conn

        self.assertTrue(db.delete_case("some-id"))
        conn.close.assert_called_once()

    @mock.patch.dict("os.environ", {"SUPABASE_DB_URL": "postgres://x"}, clear=True)
    @mock.patch("precedent.db.register_vector")
    @mock.patch("precedent.db.psycopg2.connect")
    def test_delete_case_not_found(self, mock_connect, mock_register) -> None:
        cursor = mock.MagicMock()
        cursor.rowcount = 0
        conn = _make_conn(cursor)
        mock_connect.return_value = conn

        self.assertFalse(db.delete_case("missing-id"))


class GetCaseTest(unittest.TestCase):
    @mock.patch.dict("os.environ", {"SUPABASE_DB_URL": "postgres://x"}, clear=True)
    @mock.patch("precedent.db.register_vector")
    @mock.patch("precedent.db.psycopg2.connect")
    def test_get_case_found(self, mock_connect, mock_register) -> None:
        cursor = mock.MagicMock()
        cursor.fetchone.return_value = {"id": "1", "summary": "s"}
        conn = _make_conn(cursor)
        mock_connect.return_value = conn

        self.assertEqual(db.get_case("1"), {"id": "1", "summary": "s"})

    @mock.patch.dict("os.environ", {"SUPABASE_DB_URL": "postgres://x"}, clear=True)
    @mock.patch("precedent.db.register_vector")
    @mock.patch("precedent.db.psycopg2.connect")
    def test_get_case_not_found(self, mock_connect, mock_register) -> None:
        cursor = mock.MagicMock()
        cursor.fetchone.return_value = None
        conn = _make_conn(cursor)
        mock_connect.return_value = conn

        self.assertIsNone(db.get_case("missing"))


class PingDbTest(unittest.TestCase):
    @mock.patch.dict("os.environ", {"SUPABASE_DB_URL": "postgres://x"}, clear=True)
    @mock.patch("precedent.db.register_vector")
    @mock.patch("precedent.db.psycopg2.connect")
    def test_ping_db_runs_select_1(self, mock_connect, mock_register) -> None:
        cursor = mock.MagicMock()
        conn = _make_conn(cursor)
        mock_connect.return_value = conn

        db.ping_db()

        cursor.execute.assert_called_once_with("SELECT 1")
        conn.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
