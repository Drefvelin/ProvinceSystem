"""Finding 3: `map_chronicle_snapshots_archive` needs a (map_id, archived_at)
index — hot queries filter on that pair but the table's PK is
(map_id, day, archived_at), which cannot serve that filter without a scan.

`schema.sql` is applied via `conn.executescript()` inside `skins.db.migrate()`,
which the server calls on every startup (`backend/server.py`) and several
write paths call again on demand. Every statement in schema.sql is
`CREATE ... IF NOT EXISTS`, so re-running the whole script against a database
that already has the tables is a no-op except for whatever is newly added —
an existing DB gets the new index the same way a fresh one does, with no
separate migration list to maintain.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

_BACKEND_ROOT = Path(__file__).resolve().parents[3]
_BACKEND_SRC = _BACKEND_ROOT / "src"
if str(_BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(_BACKEND_ROOT))
if str(_BACKEND_SRC) not in sys.path:
    sys.path.insert(0, str(_BACKEND_SRC))

from src.skins import db as skins_db  # noqa: E402

_INDEX_NAME = "idx_map_chronicle_snapshots_archive_map"

# The archive table exactly as it existed before this fix, minus the new
# index — stands in for a database created by an older deployment.
_PRE_FIX_ARCHIVE_TABLE = """
CREATE TABLE IF NOT EXISTS map_chronicle_snapshots_archive (
    map_id      TEXT NOT NULL,
    day         TEXT NOT NULL,
    realm_id    TEXT NOT NULL DEFAULT 'main',
    captured_at INTEGER NOT NULL,
    bytes       INTEGER NOT NULL,
    geometry_version TEXT,
    manifest    TEXT NOT NULL,
    archived_at INTEGER NOT NULL,
    PRIMARY KEY (map_id, day, archived_at)
);
"""


def _index_names(conn) -> set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index'"
    ).fetchall()
    return {row["name"] for row in rows}


@pytest.fixture
def db_env(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    monkeypatch.setattr(skins_db, "DATA_DIR", data_dir)
    monkeypatch.setattr(skins_db, "DB_PATH", data_dir / "province.db")
    monkeypatch.setattr(skins_db, "SKINS_DIR", data_dir / "skins")
    monkeypatch.setattr(skins_db, "WARDROBE_DIR", data_dir / "wardrobe")
    monkeypatch.setattr(skins_db, "DRINKS_DIR", data_dir / "drinks")
    return tmp_path


def test_index_present_on_a_fresh_database(db_env):
    skins_db.migrate()
    with skins_db.connect() as conn:
        names = _index_names(conn)
    assert _INDEX_NAME in names


def test_index_backfilled_onto_a_database_created_from_the_old_schema(db_env):
    # Simulate a database that predates this fix: the archive table exists,
    # but not yet the index.
    with skins_db.connect() as conn:
        conn.executescript(_PRE_FIX_ARCHIVE_TABLE)
    with skins_db.connect() as conn:
        assert _INDEX_NAME not in _index_names(conn)

    # The normal startup path: migrate() re-applies schema.sql.
    skins_db.migrate()

    with skins_db.connect() as conn:
        assert _INDEX_NAME in _index_names(conn)


def test_index_covers_the_hot_query_columns(db_env):
    skins_db.migrate()
    with skins_db.connect() as conn:
        row = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='index' AND name = ?",
            (_INDEX_NAME,),
        ).fetchone()
    assert row is not None
    assert "map_id" in row["sql"]
    assert "archived_at" in row["sql"]


if __name__ == "__main__":
    sys.exit(pytest.main([os.path.abspath(__file__), "-q"]))
