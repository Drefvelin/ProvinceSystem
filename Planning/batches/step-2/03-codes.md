# Batch 2.03 — Codes (issue, redeem, seed)

**Plan + build:** Plugin can mint a code; website session comes from redeem; seed script for local mock code.

## Plan

1. Code generation: random plaintext (e.g. readable groups); store **SHA-256** hash only.
2. `POST /skins/codes` — header `X-Plugin-Key`; body `{ "player_uuid": "…" }` → `{ "code", "expires_at" }`. Expiry default 48h (configurable).
3. `POST /skins/redeem` — body `{ "code": "…" }` → short-lived session token (signed or random token stored in DB/memory) bound to that code’s `player_uuid` + `code_id`. Mark `redeemed_at` on first successful redeem (or allow redeem until used for submission — pick **one**: recommend redeem marks redeemed and session lasts ~1h for upload).
4. Seed script: insert hash for plaintext `TEST-CODE-1` + fake UUID; printable instructions.
5. Register `skins_routes` router on app (codes + redeem only for now).

## Build

| File | Action |
|------|--------|
| `backend/src/skins/codes.py` | create |
| `backend/src/api/skins_routes.py` | create (partial) |
| `backend/server.py` | `include_router(skins_router)` |
| `backend/src/skins/seed_dev_code.py` or `scripts/seed_skins_code.py` | create |

**Session approach (locked for this batch):** opaque token stored in SQLite table `sessions` (`token_hash`, `code_id`, `player_uuid`, `expires_at`) **or** column on codes — prefer small `sessions` table added in this batch migration if not in 2.01 (alter migrate).

If 2.01 schema had no sessions, extend migrate here.

## Verify

```bash
# seed
python …seed…

# issue (plugin)
curl -X POST http://localhost:8000/skins/codes \
  -H "X-Plugin-Key: $PLUGIN_KEY" -H "Content-Type: application/json" \
  -d "{\"player_uuid\":\"00000000-0000-0000-0000-000000000001\"}"

# redeem mock
curl -X POST http://localhost:8000/skins/redeem \
  -H "Content-Type: application/json" \
  -d "{\"code\":\"TEST-CODE-1\"}"
```

- [ ] Issue returns plaintext once; DB has hash only  
- [ ] Redeem returns session token  
- [ ] Bad key / bad code → 401/400  

## Out of scope

Multipart uploads, approve/deny.
