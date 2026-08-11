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


def _tables(conn: sqlite3.Connection) -> set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
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
        if "discord_username" not in _column_names(conn, "discord_links"):
            conn.execute(
                "ALTER TABLE discord_links ADD COLUMN discord_username TEXT"
            )
        if "left_guild_at" not in _column_names(conn, "discord_links"):
            conn.execute(
                "ALTER TABLE discord_links ADD COLUMN left_guild_at TEXT"
            )
        if "grace_until" not in _column_names(conn, "discord_links"):
            conn.execute(
                "ALTER TABLE discord_links ADD COLUMN grace_until TEXT"
            )
        if "scope" not in _column_names(conn, "codes"):
            conn.execute(
                "ALTER TABLE codes ADD COLUMN scope TEXT NOT NULL DEFAULT 'skin'"
            )
        conn.execute(
            "UPDATE codes SET scope = 'skin' WHERE scope IS NULL OR TRIM(scope) = ''"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_discord_links_grace "
            "ON discord_links(grace_until)"
        )
        # Legacy player_key column may exist; leave unused (SQLite DROP COLUMN optional)
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
        if "tiers" not in _column_names(conn, "submissions"):
            conn.execute("ALTER TABLE submissions ADD COLUMN tiers TEXT")
        if "tier_aliases" not in _column_names(conn, "submissions"):
            conn.execute(
                "ALTER TABLE submissions ADD COLUMN tier_aliases TEXT"
            )
        if "helmet_3d_tiers" not in _column_names(conn, "submissions"):
            conn.execute(
                "ALTER TABLE submissions ADD COLUMN helmet_3d_tiers TEXT"
            )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS player_warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_uuid TEXT NOT NULL,
                staff_uuid TEXT,
                staff_name TEXT,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS moderation_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                discord_user_id TEXT NOT NULL,
                player_uuid TEXT,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL,
                delivered_at TEXT
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_player_warnings_uuid "
            "ON player_warnings(player_uuid, created_at)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_moderation_notifications_undelivered "
            "ON moderation_notifications(delivered_at, created_at)"
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS armourshop_catalog (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS creation_catalog (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS character_creates (
                id TEXT PRIMARY KEY,
                player_uuid TEXT NOT NULL,
                client_request_id TEXT,
                payload TEXT NOT NULL,
                status TEXT NOT NULL,
                character_id TEXT,
                error TEXT,
                created_at TEXT NOT NULL,
                applied_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_character_creates_client_req
            ON character_creates(player_uuid, client_request_id)
            WHERE client_request_id IS NOT NULL AND TRIM(client_request_id) != ''
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_character_creates_pending
            ON character_creates(status, created_at)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS character_roster (
                player_uuid TEXT NOT NULL,
                character_id TEXT NOT NULL,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                race TEXT,
                class TEXT,
                created_at TEXT,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (player_uuid, character_id)
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_character_roster_player
            ON character_roster(player_uuid)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS character_player_meta (
                player_uuid TEXT PRIMARY KEY,
                max_alive_characters INTEGER,
                eighteen INTEGER,
                real_age_set INTEGER NOT NULL DEFAULT 0,
                account_created_at_epoch INTEGER,
                name_colour_stops INTEGER,
                updated_at TEXT NOT NULL
            )
            """
        )
        meta_cols = _column_names(conn, "character_player_meta")
        if "eighteen" not in meta_cols:
            conn.execute(
                "ALTER TABLE character_player_meta ADD COLUMN eighteen INTEGER"
            )
        if "real_age_set" not in meta_cols:
            conn.execute(
                "ALTER TABLE character_player_meta ADD COLUMN real_age_set "
                "INTEGER NOT NULL DEFAULT 0"
            )
        if "account_created_at_epoch" not in meta_cols:
            conn.execute(
                "ALTER TABLE character_player_meta "
                "ADD COLUMN account_created_at_epoch INTEGER"
            )
        if "name_colour_stops" not in meta_cols:
            conn.execute(
                "ALTER TABLE character_player_meta "
                "ADD COLUMN name_colour_stops INTEGER"
            )
        meta_cols = _column_names(conn, "character_player_meta")
        if "kit_cooldown_seconds_remaining" not in meta_cols:
            conn.execute(
                "ALTER TABLE character_player_meta "
                "ADD COLUMN kit_cooldown_seconds_remaining INTEGER"
            )
        if "kit_cooldown_hours" not in meta_cols:
            conn.execute(
                "ALTER TABLE character_player_meta "
                "ADD COLUMN kit_cooldown_hours INTEGER"
            )
        meta_cols = _column_names(conn, "character_player_meta")
        if "kit_cooldowns_json" not in meta_cols:
            conn.execute(
                "ALTER TABLE character_player_meta "
                "ADD COLUMN kit_cooldowns_json TEXT"
            )
        roster_cols = _column_names(conn, "character_roster")
        if "kit_status" not in roster_cols:
            conn.execute(
                "ALTER TABLE character_roster ADD COLUMN kit_status TEXT"
            )
        roster_cols = _column_names(conn, "character_roster")
        if "kit_statuses_json" not in roster_cols:
            conn.execute(
                "ALTER TABLE character_roster ADD COLUMN kit_statuses_json TEXT"
            )
        # Legacy NOT NULL on max_alive_characters breaks age-only upserts.
        max_col = next(
            (
                row
                for row in conn.execute(
                    "PRAGMA table_info(character_player_meta)"
                ).fetchall()
                if row["name"] == "max_alive_characters"
            ),
            None,
        )
        if max_col is not None and int(max_col["notnull"] or 0) == 1:
            conn.execute(
                """
                CREATE TABLE character_player_meta_new (
                    player_uuid TEXT PRIMARY KEY,
                    max_alive_characters INTEGER,
                    eighteen INTEGER,
                    real_age_set INTEGER NOT NULL DEFAULT 0,
                    account_created_at_epoch INTEGER,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                INSERT INTO character_player_meta_new (
                    player_uuid, max_alive_characters, eighteen,
                    real_age_set, account_created_at_epoch, updated_at
                )
                SELECT
                    player_uuid,
                    max_alive_characters,
                    eighteen,
                    COALESCE(real_age_set, 0),
                    account_created_at_epoch,
                    updated_at
                FROM character_player_meta
                """
            )
            conn.execute("DROP TABLE character_player_meta")
            conn.execute(
                "ALTER TABLE character_player_meta_new "
                "RENAME TO character_player_meta"
            )
        if "staff" not in _column_names(conn, "submissions"):
            conn.execute(
                "ALTER TABLE submissions ADD COLUMN staff INTEGER NOT NULL DEFAULT 0"
            )
        if "category" not in _column_names(conn, "submissions"):
            conn.execute("ALTER TABLE submissions ADD COLUMN category TEXT")
        if "scroll" not in _column_names(conn, "submissions"):
            conn.execute("ALTER TABLE submissions ADD COLUMN scroll TEXT")
        if "tier_scrolls" not in _column_names(conn, "submissions"):
            conn.execute("ALTER TABLE submissions ADD COLUMN tier_scrolls TEXT")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS lore_item_customisations (
                player_uuid TEXT NOT NULL,
                character_id TEXT NOT NULL,
                kit_key TEXT NOT NULL,
                display_name TEXT NOT NULL DEFAULT '',
                lore_json TEXT NOT NULL DEFAULT '[]',
                existing_skin_id TEXT,
                submission_id TEXT,
                state TEXT NOT NULL DEFAULT 'draft',
                skin_slug TEXT,
                ready_at TEXT,
                applied_at TEXT,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (player_uuid, character_id, kit_key)
            )
            """
        )
        lore_cols = _column_names(conn, "lore_item_customisations")
        if "state" not in lore_cols:
            conn.execute(
                "ALTER TABLE lore_item_customisations "
                "ADD COLUMN state TEXT NOT NULL DEFAULT 'draft'"
            )
        if "skin_slug" not in lore_cols:
            conn.execute(
                "ALTER TABLE lore_item_customisations ADD COLUMN skin_slug TEXT"
            )
        if "ready_at" not in lore_cols:
            conn.execute(
                "ALTER TABLE lore_item_customisations ADD COLUMN ready_at TEXT"
            )
        if "applied_at" not in lore_cols:
            conn.execute(
                "ALTER TABLE lore_item_customisations ADD COLUMN applied_at TEXT"
            )
        lore_cols = _column_names(conn, "lore_item_customisations")
        if "kit_id" not in lore_cols:
            conn.execute(
                "ALTER TABLE lore_item_customisations ADD COLUMN kit_id TEXT"
            )
        # Discard player_keys system
        if "player_keys" in _tables(conn):
            conn.execute("DROP TABLE player_keys")
        conn.execute("DROP INDEX IF EXISTS idx_discord_links_player_key")
        conn.execute("DROP INDEX IF EXISTS idx_player_keys_key")
        conn.commit()
