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

Helper role can run `/precedent` and `/case-view` (read-only) but not `/case-log`
or `/case-delete`, matching the staff/helper split already used by
`minecraftban` and `skinsreview`.

Staff can also view a logged case's untruncated details with `/case-view <id>`
(case ids are shown next to each match in `/precedent` results), and permanently
remove a bad entry with `/case-delete <id>` (staff only, asks for confirmation
before deleting). `/precedent` optionally takes a comma-separated `players`
argument, which ranks cases involving those players higher without excluding
other matches (a typo'd name never zero-results the search).

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
| `POST /precedent/staff/log` | `{logged_by, players[], summary, rule, ruling, punishment}` (all fields length-capped) | `{id}` |
| `POST /precedent/staff/search` | `{query, players[]?}` (`players` is an optional soft-boost ranking hint, not a filter) | `{matches: [{id, logged_by, players, summary, rule, ruling, punishment, created_at, distance}], synthesis, max_distance}` |
| `GET /precedent/staff/case/{id}` | - | Full case (same shape as one `matches` entry) or 404 |
| `DELETE /precedent/staff/case/{id}` | - | `{deleted: true, id}` or 404 |
| `GET /precedent/staff/ping` | - | `{ok: true}` (cheap reachability check, no Voyage/Claude cost) |

`max_distance` in the search response is the live relevance cutoff (`MAX_RELEVANT_DISTANCE`
in `backend/src/precedent/db.py`) so bot-side similarity-percentage math never drifts out of
sync with the backend. `/staff/search` is rate-limited to 10 requests/60s per client IP
(same in-process limiter pattern as the `/skins/codes/inspect` route).

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

## Operational notes

- `migrate()` gates schema setup on a module-global flag, assuming a single-worker
  deploy (confirmed: no multi-worker launch config exists for this backend). Both
  the `CREATE EXTENSION`/`CREATE TABLE` statements are idempotent, so even under a
  future multi-worker deploy the only risk is duplicate cold-start work, not data
  corruption.
- `logged_by` is caller-supplied and trusted once the shared `X-Staff-Key` has
  authenticated the request, the same trust model as every other `X-Staff-Key`
  route in this codebase (e.g. `staff_name` fields in the skins routes). Not a
  gap specific to this feature.

## Out of scope (v1)

Web UI for browsing/editing logged cases, backfill from historical mod-log channel
messages, editing logged cases, cross-server precedent sharing.
