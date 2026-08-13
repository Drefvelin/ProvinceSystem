CREATE TABLE IF NOT EXISTS codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_hash TEXT NOT NULL UNIQUE,
    code_plaintext TEXT,
    player_uuid TEXT NOT NULL,
    scope TEXT NOT NULL DEFAULT 'skin',
    realm_id TEXT NOT NULL DEFAULT 'main',
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
    staff INTEGER NOT NULL DEFAULT 0,
    category TEXT,
    scroll TEXT,
    tier_scrolls TEXT,
    realm_id TEXT NOT NULL DEFAULT 'main',
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

CREATE TABLE IF NOT EXISTS armourshop_catalog (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    payload TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS armourshop_player_meta (
    player_uuid TEXT PRIMARY KEY,
    name_colour_stops INTEGER NOT NULL DEFAULT 0,
    max_3d_pair_bytes INTEGER NOT NULL DEFAULT 0,
    skin_token_cooldown_days INTEGER NOT NULL DEFAULT -1,
    skin_kinds_json TEXT NOT NULL DEFAULT '[]',
    allow_armor_3d_helmet INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);

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
    deny_reason TEXT,
    updated_at TEXT NOT NULL,
    realm_id TEXT NOT NULL DEFAULT 'main',
    PRIMARY KEY (player_uuid, character_id, kit_key)
);

CREATE INDEX IF NOT EXISTS idx_lore_item_customisations_realm_state
ON lore_item_customisations(realm_id, state);

CREATE TABLE IF NOT EXISTS character_wardrobe_slots (
    player_uuid TEXT NOT NULL,
    character_id TEXT NOT NULL,
    slot TEXT NOT NULL,
    png_relpath TEXT,
    texture_value TEXT,
    texture_signature TEXT,
    model TEXT,
    display_name TEXT,
    apply_pending INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (player_uuid, character_id, slot)
);

CREATE TABLE IF NOT EXISTS character_create_wardrobe (
    create_id TEXT NOT NULL,
    slot TEXT NOT NULL,
    png_relpath TEXT,
    texture_value TEXT,
    texture_signature TEXT,
    model TEXT,
    display_name TEXT,
    updated_at TEXT NOT NULL,
    PRIMARY KEY (create_id, slot)
);

CREATE TABLE IF NOT EXISTS drink_submissions (
    id TEXT PRIMARY KEY,
    player_uuid TEXT NOT NULL,
    code_id INTEGER NOT NULL,
    slug TEXT NOT NULL,
    display_name TEXT NOT NULL,
    recipe_json TEXT NOT NULL,
    status TEXT NOT NULL,
    deny_reason TEXT,
    texture_id TEXT,
    new_texture INTEGER NOT NULL DEFAULT 0,
    dir_path TEXT NOT NULL,
    discord_user_id TEXT,
    created_at TEXT NOT NULL,
    reviewed_at TEXT,
    applied_at TEXT,
    realm_id TEXT NOT NULL DEFAULT 'main',
    FOREIGN KEY (code_id) REFERENCES codes(id)
);

CREATE TABLE IF NOT EXISTS drink_textures (
    id TEXT PRIMARY KEY,
    owner_uuid TEXT NOT NULL,
    cmd INTEGER,
    ia_item_id TEXT,
    png_path TEXT NOT NULL,
    refcount INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS drink_catalog (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    payload TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS drink_player_meta (
    player_uuid TEXT PRIMARY KEY,
    allow_drink_texture INTEGER NOT NULL DEFAULT 0,
    name_colour_stops INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS rpc_player_meta (
    player_uuid TEXT NOT NULL,
    realm_id TEXT NOT NULL DEFAULT 'main',
    name_colour_stops INTEGER NOT NULL DEFAULT 0,
    allow_drink_texture INTEGER NOT NULL DEFAULT 0,
    max_alive_characters INTEGER,
    wardrobe_skin_slots INTEGER NOT NULL DEFAULT 1,
    max_3d_pair_bytes INTEGER NOT NULL DEFAULT 0,
    skin_token_cooldown_days INTEGER NOT NULL DEFAULT -1,
    skin_kinds_json TEXT NOT NULL DEFAULT '[]',
    allow_armor_3d_helmet INTEGER NOT NULL DEFAULT 0,
    permission_flags_json TEXT NOT NULL DEFAULT '{}',
    updated_at TEXT NOT NULL,
    PRIMARY KEY (player_uuid, realm_id)
);

CREATE TABLE IF NOT EXISTS drink_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    submission_id TEXT NOT NULL,
    discord_user_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL,
    delivered_at TEXT
);

CREATE TABLE IF NOT EXISTS cosmetic_mint_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_uuid TEXT NOT NULL,
    reset_at TEXT NOT NULL,
    staff_uuid TEXT
);

CREATE INDEX IF NOT EXISTS idx_drink_submissions_status
    ON drink_submissions(status);
CREATE INDEX IF NOT EXISTS idx_drink_submissions_slug
    ON drink_submissions(slug);
CREATE INDEX IF NOT EXISTS idx_drink_textures_owner
    ON drink_textures(owner_uuid);
CREATE INDEX IF NOT EXISTS idx_drink_notifications_undelivered
    ON drink_notifications(delivered_at, created_at);
CREATE INDEX IF NOT EXISTS idx_cosmetic_mint_resets_player
    ON cosmetic_mint_resets(player_uuid);
