# Precedent lookup (`/precedent`)

Staff-only Discord tool: log past moderation cases, then semantically search them so
similar incidents get similar rulings. Bot never decides punishments — it's advisory.

**See also:** [integrations/discord-bot.md](./discord-bot.md) (bot cog pattern), `tfmc_bot/precedent/` (cog source).

## Flow

1. Staff run `/case-log` after handling an incident (players, rule broken, evidence
   summary, ruling, punishment) → cog POSTs to ProvinceSystem → ProvinceSystem embeds
   the case text (Voyage AI) and stores it in Supabase Postgres (`pgvector`).
2. Staff run `/precedent <case info>` → cog POSTs the free-text query → ProvinceSystem
   embeds it, runs a pgvector cosine-similarity search for the 3 closest past cases,
   and asks Claude to synthesize what precedent suggests → cog posts an embed with the
   3 matches + the synthesis.

Helper role can run `/precedent` (read-only) but not `/case-log`, matching the
staff/helper split already used by `minecraftban` and `skinsreview`.

`/minecraftwarn` and `/minecraftnotify` (both in the `minecraftban` cog) also
auto-log a precedent case on every use — no separate `/case-log` needed for these.
`/minecraftnotify` is an existing anonymous-to-recipient staff DM (unrelated to
in-game warnings); its precedent record still keeps the real issuing staff member
as `logged_by` internally, for staff-side accountability, even though the
recipient never sees who sent it. Neither command's own behavior (DMs, log
channel embeds, params) was changed — the precedent log call is a pure addition
via `_log_precedent()` in `minecraftban.py`.

## API surface (staff, `X-Staff-Key`)

| Route | Body | Returns |
|-------|------|---------|
| `POST /precedent/staff/log` | `{logged_by, players[], summary, rule, ruling, punishment}` | `{id}` |
| `POST /precedent/staff/search` | `{query}` | `{matches: [{id, logged_by, players, summary, rule, ruling, punishment, created_at, distance}], synthesis}` |

Implementation: `backend/src/api/precedent_routes.py`, `backend/src/precedent/{db,embeddings,synthesis}.py`.

## Storage

Supabase Postgres, `pgvector` extension, single table `precedent_cases` (id, logged_by,
players, summary, rule, ruling, punishment, embedding `vector(1024)`, created_at).
Table + extension are created lazily on first request (`migrate()` in `precedent/db.py`).

This is separate infrastructure from the existing SQLite skins/drinks DB — ProvinceSystem
had no Postgres/Supabase usage before this feature.

## Configuration

| Env (ProvinceSystem `backend/.env`) | Purpose |
|--------------------------------------|---------|
| `SUPABASE_DB_URL` | Postgres connection string (Supabase project) |
| `VOYAGE_API_KEY` | Voyage AI embeddings |
| `ANTHROPIC_API_KEY` | Claude synthesis |

These secrets live only in ProvinceSystem's backend env — the bot never sees them,
same as `STAFF_KEY`-gated routes elsewhere.

| Env / config (tfmc_bot `precedent/config.yml`) | Purpose |
|-------------------------------------------------|---------|
| `api_base_url` / `API_BASE_URL` | ProvinceSystem API base |
| `staff_key` / `STAFF_KEY` | Matches backend `STAFF_KEY` |
| `staff_role_id` / `STAFF_ROLE_ID` | Can run `/case-log` and `/precedent` |
| `helper_role_id` / `HELPER_ROLE_ID` | Can run `/precedent` only |

## Out of scope (v1)

Web UI for browsing/editing logged cases, backfill from historical mod-log channel
messages, editing/deleting logged cases, cross-server precedent sharing.
