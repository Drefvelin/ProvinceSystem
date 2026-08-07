# Batch 2.01 — Data foundation

**Plan + build:** SQLite, directories, docker volume, gitignore. No HTTP skins routes yet.

## Plan

1. Add runtime data root: `backend/src/data/` with `skins/` subfolder (`.gitkeep` under `data/` or `data/skins/` only; DB file stays gitignored).
2. Add `schema.sql` for `codes` and `submissions` (columns per [05](../../05-skins-system.md)).
3. Add `db.py`: path to `province.db`, `connect()`, `migrate()` creating tables if missing.
4. Call `migrate()` on FastAPI startup in [`server.py`](../../../backend/server.py).
5. Compose: mount `./backend/src/data:/app/src/data` on backend.
6. Ensure `*.db` / `backend/src/data/skins/**` (except `.gitkeep`) are gitignored as needed.

## Build

| File / change | Action |
|---------------|--------|
| `backend/src/data/skins/.gitkeep` | create |
| `backend/src/skins/schema.sql` | create |
| `backend/src/skins/db.py` | create |
| `backend/server.py` | startup migrate |
| `docker-compose.yml` | data volume |
| `.gitignore` | confirm db + uploaded skins ignored |

## Verify

- [ ] Start uvicorn; no error; `province.db` appears under `data/`
- [ ] Tables `codes` and `submissions` exist (sqlite3 `.tables`)
- [ ] `data/skins/` exists

## Out of scope

Slug helpers, routes, seed script.
