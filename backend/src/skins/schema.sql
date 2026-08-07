CREATE TABLE IF NOT EXISTS codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_hash TEXT NOT NULL UNIQUE,
    player_uuid TEXT NOT NULL,
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
    status TEXT NOT NULL,
    deny_reason TEXT,
    dir_path TEXT NOT NULL,
    created_at TEXT NOT NULL,
    reviewed_at TEXT,
    applied_at TEXT,
    discord_message_id TEXT,
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

CREATE INDEX IF NOT EXISTS idx_submissions_status ON submissions(status);
CREATE INDEX IF NOT EXISTS idx_submissions_slug ON submissions(slug);
CREATE INDEX IF NOT EXISTS idx_codes_hash ON codes(code_hash);
CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token_hash);
