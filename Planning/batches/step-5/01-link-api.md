# Batch 5.01 — Discord link API

**Plan + build:** Schema and endpoints so Minecraft can start a link and Discord can complete it. No submit gate or DMs yet.

**Repo:** ProvinceSystem  

## Plan

1. Tables:
   - `discord_links` — `player_uuid` unique, `discord_user_id` unique, `linked_at`, optional `minecraft_name`
   - `discord_link_codes` — `code_hash`, `player_uuid`, `expires_at`, `used_at` (TTL ~10–15 min)
2. `POST /skins/discord/link/start` — header `X-Plugin-Key`; body `{ "player_uuid", "minecraft_name?" }` → `{ "code", "expires_at" }` (plaintext code once).
3. `POST /skins/discord/link/complete` — header `X-Staff-Key`; body `{ "code", "discord_user_id" }` → upsert link for that UUID; consume code.
4. Relink rules: successful complete **replaces** prior row for the same UUID; if `discord_user_id` is already linked to a **different** UUID → **400** with clear message.
5. Helper `get_discord_id_for_uuid(uuid)` for later batches.
6. Small curl/script verify: start → complete → lookup.

## Build

| File | Action |
|------|--------|
| `backend/src/skins/schema.sql` (+ migrate if needed) | New tables |
| `backend/src/skins/discord_link.py` (or similar) | start / complete / get |
| `backend/src/api/skins_routes.py` | Two POST routes |

## Verify

```bash
# start (plugin key)
curl -X POST -H "X-Plugin-Key: $PLUGIN_KEY" -H "Content-Type: application/json" \
  -d '{"player_uuid":"00000000-0000-0000-0000-000000000001","minecraft_name":"Test"}' \
  http://localhost:8000/skins/discord/link/start

# complete (staff key) — use code from start
curl -X POST -H "X-Staff-Key: $STAFF_KEY" -H "Content-Type: application/json" \
  -d '{"code":"…","discord_user_id":"123456789012345678"}' \
  http://localhost:8000/skins/discord/link/complete
```

- [ ] Start returns code + expiry  
- [ ] Complete creates link row  
- [ ] Same UUID can relink (replace)  
- [ ] Same Discord id on another UUID → 400  
- [ ] Expired / reused code → 400  
- [ ] Wrong keys → 401  

## Out of scope

Submit require-link, notifications, cog, ArmourShop command.
