import sqlite3
from pathlib import Path

_SKINS_PKG = Path(__file__).resolve().parent
DATA_DIR = _SKINS_PKG.parent / "data"
DB_PATH = DATA_DIR / "province.db"
SKINS_DIR = DATA_DIR / "skins"
SCHEMA_PATH = _SKINS_PKG / "schema.sql"


def connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _column_names(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row["name"] for row in rows}


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
        conn.commit()
