CREATE TABLE IF NOT EXISTS codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_hash TEXT NOT NULL UNIQUE,
    code_plaintext TEXT,
    player_uuid TEXT NOT NULL,
    scope TEXT NOT NULL DEFAULT 'skin',
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    redeemed_at TEXT,
    revoked INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS submissions (
    id TEXT PRIMARY KEY,
    player_uuid TEXT NOT NULL,
    code_id INTEGER NOT NULL,
    kind TEXT NOT NULL,
    slug TEXT NOT NULL,
    display_name TEXT NOT NULL,
    grip_preset TEXT,
    base_set TEXT,
    tiers TEXT,
    tier_aliases TEXT,
    add_name INTEGER NOT NULL DEFAULT 0,
    name_colours TEXT,
    name_styles TEXT,
    status TEXT NOT NULL,
    deny_reason TEXT,
    dir_path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    reviewed_at TEXT,
    applied_at TEXT,
    discord_message_id TEXT,
    discord_user_id TEXT,
    FOREIGN KEY (code_id) REFERENCES codes(id)
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token_hash TEXT NOT NULL UNIQUE,
    code_id INTEGER NOT NULL,
    player_uuid TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (code_id) REFERENCES codes(id)
);

CREATE TABLE IF NOT EXISTS discord_links (
    player_uuid TEXT PRIMARY KEY,
    discord_user_id TEXT NOT NULL UNIQUE,
    minecraft_name TEXT,
    discord_username TEXT,
    linked_at TEXT NOT NULL,
    left_guild_at TEXT,
    grace_until TEXT
);

CREATE TABLE IF NOT EXISTS discord_link_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_hash TEXT NOT NULL UNIQUE,
    player_uuid TEXT NOT NULL,
    minecraft_name TEXT,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    used_at TEXT
);

CREATE TABLE IF NOT EXISTS skin_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    submission_id TEXT NOT NULL,
    discord_user_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    delivered_at TEXT
);

CREATE TABLE IF NOT EXISTS plugin_notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    player_uuid TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    delivered_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_slug ON submissions(slug);
CREATE INDEX IF NOT EXISTS idx_codes_hash ON codes(code_hash);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token_hash);
CREATE INDEX IF NOT EXISTS idx_discord_links_discord ON discord_links(discord_user_id);
CREATE INDEX IF NOT EXISTS idx_discord_link_codes_hash ON discord_link_codes(code_hash);
CREATE INDEX IF NOT EXISTS idx_skin_notifications_undelivered
    ON skin_notifications(delivered_at, created_at);
CREATE INDEX IF NOT EXISTS idx_plugin_notices_undelivered
    ON plugin_notices(delivered_at, created_at);

CREATE TABLE IF NOT EXISTS player_warnings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_uuid TEXT NOT NULL,
    staff_uuid TEXT,
    staff_name TEXT,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS moderation_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    discord_user_id TEXT NOT NULL,
    player_uuid TEXT,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    delivered_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_player_warnings_uuid
    ON player_warnings(player_uuid, created_at);
CREATE INDEX IF NOT EXISTS idx_moderation_notifications_undelivered
    ON moderation_notifications(delivered_at, created_at);
