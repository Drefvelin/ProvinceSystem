# Precedent lookup (`/precedent`)

Staff-only Discord tool: log past moderation cases, then semantically search them so
similar incidents get similar rulings. Bot never decides punishments — it's advisory.

**See also:** [integrations/discord-bot.md](./discord-bot.md) (bot cog pattern), `tfmc_bot/precedent/` (cog source).

## Flow

1. Staff run `/case-log` after handling an incident (players, rule broken, evidence
   summary, ruling, punishment) → cog POSTs to ProvinceSystem → ProvinceSystem embeds
   the case (Voyage AI) and stores it in Supabase Postgres (`pgvector`).

   **Only the summary is embedded** (`_case_text` in `precedent_routes.py`). A search
   query is always a description of what happened: staff cannot cite the rule number
   from memory, and the ruling and punishment are exactly what they are asking for.
   Indexing those fields put roughly half the stored vector beyond anything a query
   could match, which kept even exact-wording matches around 0.49 distance. Summary-only
   indexing moved `"xray"` against the logged `Xray` case from 0.493 to 0.390.
   Changing what gets embedded invalidates every stored vector — re-run
   `python -m src.scripts.backfill_precedent_embeddings` over the whole corpus rather
   than letting old and new rows coexist.
2. Staff run `/precedent <case info>` → cog POSTs the free-text query → ProvinceSystem
   embeds it, runs a pgvector cosine-similarity search for the 3 closest past cases
   (boosted, not filtered, by exact-word matches on the query and by any `players`
   given, so a short exact-wording case like a one-line "Xray" summary isn't crowded
   out by a longer only-thematically-related one), and asks Claude to synthesize what
   precedent suggests → cog posts an embed with the 3 matches + the synthesis.

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

## Web UI (`/precedent`, staff only)

Staff can browse and maintain the whole corpus at `/precedent` on the website — the
Discord commands only ever surface three matches at a time, so a bad or duplicate
entry was previously invisible and uncorrectable. The page lists every case, filters
them client-side as you type (no API call, no cost), and offers Log / Edit / Delete.
The semantic search sits in its own panel behind an explicit submit button, since each
run costs a Voyage embed plus a Claude call.

Gated on the same `tfmc.map.staff` permission flag as `/inspect` and the map editor,
via `useSiteStaffAccess` client-side and `require_site_staff` server-side.

**Editing re-embeds the case.** The stored vector is what search matches on, so saving
edited text against the old vector would leave the row unfindable by the wording it now
contains. `PUT /staff/case/{id}` always recomputes the embedding before writing.

Implementation: `frontend/app/precedent/page.tsx`,
`frontend/app/components/precedent/`, `frontend/lib/precedent/{api,filter}.ts`.

## API surface (staff)

Two clients, two credentials. The Discord bot and plugins send the shared
`X-Staff-Key`; the website must never ship that secret to a browser, so it sends
`Authorization: Bearer <session_token>` and the server checks the caller's
`tfmc.map.staff` flag. Every route below accepts either. A *wrong* `X-Staff-Key` is
rejected outright rather than falling through to the session path.

| Route | Body | Returns |
|-------|------|---------|
| `POST /precedent/staff/log` | `{logged_by, players[], summary, rule, ruling, punishment}` (all fields length-capped) | `{id}` |
| `POST /precedent/staff/search` | `{query, players[]?}` (`players` is an optional soft-boost ranking hint, not a filter) | `{matches: [{id, logged_by, players, summary, rule, ruling, punishment, created_at, distance}], synthesis, max_distance}` |
| `GET /precedent/staff/cases?limit=&offset=` | - | `{cases: [...], total}` — plain SELECT, newest first, no Voyage/Claude cost. `limit` clamps to 1000 |
| `GET /precedent/staff/case/{id}` | - | Full case (same shape as one `matches` entry) or 404 |
| `PUT /precedent/staff/case/{id}` | Same body as `/staff/log` | `{updated: true, id}` or 404. Re-embeds before writing |
| `DELETE /precedent/staff/case/{id}` | - | `{deleted: true, id}` or 404 |
| `GET /precedent/staff/ping` | - | `{ok: true}` (cheap reachability check, no Voyage/Claude cost) |

`max_distance` in the search response is the live relevance cutoff (`MAX_RELEVANT_DISTANCE`
in `backend/src/precedent/db.py`) so bot-side similarity-percentage math never drifts out of
sync with the backend.

`MAX_RELEVANT_DISTANCE` is 0.55, measured against the live corpus: realistic moderation
queries peak at 0.505 for their nearest match, off-topic ones bottom out at 0.602. It is
specific to the current indexing — re-measure after changing `_case_text` or the embedding
call.

**Embeddings are symmetric.** `embed_batch` sends no `input_type`. Voyage recommends
`query`/`document` for asymmetric retrieval (short query, long document), but precedent
search compares a short incident description against a short case summary. Measured here,
the asymmetric prefixes added a near-constant 0.32–0.44 cosine penalty to *every*
comparison regardless of match quality: byte-identical text scored 0.319–0.442 apart as
query-vs-document, and 0.000 apart embedded the same way. Dropping it improved nearest-match
distance for every test query (`"xray"` against the logged `Xray` case went 0.390 → 0.103)
and widened the relevant/off-topic separation from 0.061 to 0.097.

Because identical text now scores 0, the website's similarity percentage maps
`[0, MAX_RELEVANT_DISTANCE]` to `[100%, 0%]` with a `^0.5` curve — 100% means genuinely
exact, with no floor subtracted. The Discord cog still applies its own `^0.3` curve, so the
two surfaces report different percentages for the same case. `/staff/search` is rate-limited to 10 requests/60s per client IP
(same in-process limiter pattern as the `/skins/codes/inspect` route).

Implementation: `backend/src/api/precedent_routes.py`, `backend/src/precedent/{db,embeddings,synthesis}.py`.

## Audit trail

Every write to `precedent_cases` appends a row to `precedent_audit` in the same Supabase
database. There is **no API route to read it** — inspecting it requires direct Supabase
access, so staff cannot review or erase their own trail from the website.

| Column | Meaning |
|--------|---------|
| `case_id` | The case affected. Not a foreign key, so it survives the case being deleted |
| `action` | `create`, `update` or `delete` |
| `source` | `web` (site-staff Bearer session) or `bot` (shared `X-Staff-Key`) |
| `actor` / `actor_uuid` | Verified player for `web`; caller-supplied and unverified for `bot` |
| `before` / `after` | JSONB snapshots of the case content, embedding excluded |

Two properties are deliberate:

- **The audit row is written inside the same transaction as the change**, so a case cannot be
  modified without a record of it — both commit or neither does.
- **`delete` keeps a full `before` snapshot.** Once the case row is gone, the audit entry is
  the only surviving copy of what it said, which is what makes a bad deletion recoverable.

Only `source='web'` proves who acted. The bot authenticates with a shared key, so its `actor`
is whatever the caller sent — treat it as a hint, not evidence.

### Restoring deleted cases

A `delete` snapshot holds everything needed to rebuild the case — original id, `created_at`,
and all content — so deletions through the API are reversible, including a mass one:

```bash
# What could be restored, writes nothing
python -m src.scripts.restore_precedent_cases --dry-run

# Restore everything deleted since a point in time
python -m src.scripts.restore_precedent_cases --since "2026-08-29"

# Restore a single case
python -m src.scripts.restore_precedent_cases --case-id <uuid>
```

Cases come back under their original id and timestamp, so links and ordering survive.
Embeddings are recomputed from the summary (a couple of batched Voyage calls for the whole
corpus). Ids that already exist are skipped rather than overwritten, so the script is safe to
re-run and safe to use while the corpus is only partly damaged. Restores are themselves
audited, as `action='restore'`, `source='script'`.

**This only covers deletions made through the API.** Direct SQL against Supabase bypasses the
audit trail entirely — Supabase's own backups are the recovery path for that.

Useful queries:

```sql
-- Recent website activity
SELECT created_at, action, actor, before->>'summary', after->>'summary'
FROM precedent_audit WHERE source = 'web' ORDER BY created_at DESC LIMIT 50;

-- Everything that ever happened to one case, including its deletion
SELECT * FROM precedent_audit WHERE case_id = '<uuid>' ORDER BY id;

-- Recover a deleted case's content
SELECT before FROM precedent_audit WHERE action = 'delete' AND case_id = '<uuid>';
```

## Storage

Supabase Postgres, `pgvector` extension. Two tables: `precedent_cases` (id, logged_by,
players, summary, rule, ruling, punishment, embedding `vector(1024)`, created_at) and
`precedent_audit` (see above). Tables + extension are created lazily on first request
(`migrate()` in `precedent/db.py`).

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
  gap specific to this feature. **Web callers are exempt:** a session-authenticated
  request has a known player behind it, so the server overrides `logged_by` with
  that player's linked Minecraft name (`get_linked_minecraft_name` in
  `backend/src/skins/codes.py`), falling back to their UUID. A signed-in staff
  member therefore cannot attribute a case to someone else.
- `/staff/search` rate-limiting buckets web callers by `player_uuid` rather than
  client IP. Behind a reverse proxy every browser shares one IP and would
  otherwise contend for a single 10/60s budget.

## Out of scope (v1)

Backfill from historical mod-log channel messages, editing cases from Discord (the
website handles it), bulk edit/delete, per-case audit history, cross-server precedent
sharing.
