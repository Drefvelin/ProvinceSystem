import secrets
import sqlite3
import string
from pathlib import Path

_SKINS_PKG = Path(__file__).resolve().parent
DATA_DIR = _SKINS_PKG.parent / "data"
DB_PATH = DATA_DIR / "province.db"
SKINS_DIR = DATA_DIR / "skins"
SCHEMA_PATH = _SKINS_PKG / "schema.sql"

_PLAYER_KEY_ALPHABET = string.ascii_lowercase + string.digits
_PLAYER_KEY_FIRST = string.ascii_lowercase


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _column_names(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row["name"] for row in rows}


def _tables(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    return {row["name"] for row in rows}


def mint_player_key(conn: sqlite3.Connection, *, attempts: int = 32) -> str:
    """Allocate a unique 8-char player_key: [a-z][a-z0-9]{7}."""
    for _ in range(attempts):
        key = secrets.choice(_PLAYER_KEY_FIRST) + "".join(
            secrets.choice(_PLAYER_KEY_ALPHABET) for _ in range(7)
        )
        taken = conn.execute(
            "SELECT 1 FROM player_keys WHERE player_key = ? LIMIT 1",
            (key,),
        ).fetchone()
        if taken is not None:
            continue
        if "player_key" in _column_names(conn, "discord_links"):
            taken_link = conn.execute(
                "SELECT 1 FROM discord_links WHERE player_key = ? LIMIT 1",
                (key,),
            ).fetchone()
            if taken_link is not None:
                continue
        return key
    raise RuntimeError("could not mint unique player_key")


def get_or_create_player_key(conn: sqlite3.Connection, player_uuid: str) -> str:
    """Stable key for UUID; survives Discord unlink."""
    uuid = (player_uuid or "").strip()
    row = conn.execute(
        "SELECT player_key FROM player_keys WHERE player_uuid = ?",
        (uuid,),
    ).fetchone()
    if row is not None and str(row["player_key"] or "").strip():
        return str(row["player_key"]).strip()

    # Legacy: key only on discord_links
    if "player_key" in _column_names(conn, "discord_links"):
        legacy = conn.execute(
            "SELECT player_key FROM discord_links WHERE player_uuid = ?",
            (uuid,),
        ).fetchone()
        if legacy is not None and str(legacy["player_key"] or "").strip():
            key = str(legacy["player_key"]).strip()
            conn.execute(
                "INSERT OR REPLACE INTO player_keys (player_uuid, player_key) VALUES (?, ?)",
                (uuid, key),
            )
            return key

    key = mint_player_key(conn)
    conn.execute(
        "INSERT INTO player_keys (player_uuid, player_key) VALUES (?, ?)",
        (uuid, key),
    )
    return key


def backfill_player_keys(conn: sqlite3.Connection) -> int:
    """Ensure every discord_links row has player_key; sync into player_keys."""
    updated = 0
    if "player_key" not in _column_names(conn, "discord_links"):
        return 0
    rows = conn.execute("SELECT player_uuid, player_key FROM discord_links").fetchall()
    for row in rows:
        uuid = str(row["player_uuid"])
        existing = str(row["player_key"] or "").strip()
        if existing:
            conn.execute(
                "INSERT OR IGNORE INTO player_keys (player_uuid, player_key) VALUES (?, ?)",
                (uuid, existing),
            )
            continue
        key = get_or_create_player_key(conn, uuid)
        conn.execute(
            "UPDATE discord_links SET player_key = ? WHERE player_uuid = ?",
            (key, uuid),
        )
        updated += 1
    return updated


def migrate() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SKINS_DIR.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with connect() as conn:
        conn.executescript(schema)
        if "grip_preset" not in _column_names(conn, "submissions"):
            conn.execute(
                "ALTER TABLE submissions ADD COLUMN grip_preset TEXT"
            )
        if "base_set" not in _column_names(conn, "submissions"):
            conn.execute(
                "ALTER TABLE submissions ADD COLUMN base_set TEXT"
            )
        if "discord_user_id" not in _column_names(conn, "submissions"):
            conn.execute(
                "ALTER TABLE submissions ADD COLUMN discord_user_id TEXT"
            )
        if "code_plaintext" not in _column_names(conn, "codes"):
            conn.execute(
                "ALTER TABLE codes ADD COLUMN code_plaintext TEXT"
            )
        if "discord_username" not in _column_names(conn, "discord_links"):
            conn.execute(
                "ALTER TABLE discord_links ADD COLUMN discord_username TEXT"
            )
        if "player_key" not in _column_names(conn, "discord_links"):
            conn.execute(
                "ALTER TABLE discord_links ADD COLUMN player_key TEXT"
            )
        conn.execute(
            "CREATE UNIQUE INDEX IF NOT EXISTS idx_discord_links_player_key "
            "ON discord_links(player_key)"
        )
        if "add_name" not in _column_names(conn, "submissions"):
            conn.execute(
                "ALTER TABLE submissions ADD COLUMN add_name INTEGER NOT NULL DEFAULT 0"
            )
        if "name_colours" not in _column_names(conn, "submissions"):
            conn.execute(
                "ALTER TABLE submissions ADD COLUMN name_colours TEXT"
            )
        if "name_styles" not in _column_names(conn, "submissions"):
            conn.execute(
                "ALTER TABLE submissions ADD COLUMN name_styles TEXT"
            )
        if "player_keys" not in _tables(conn):
            conn.execute(
                """
                CREATE TABLE player_keys (
                    player_uuid TEXT PRIMARY KEY,
                    player_key TEXT NOT NULL UNIQUE
                )
                """
            )
        backfill_player_keys(conn)
        conn.commit()
