# Batch 19.04 — Character create/list + RPCharacters ingest

**Plan + build:** Characters API accepts a finished creation payload (validated against catalog + point-buy rules), lists alive/dead for the session UUID, and RPCharacters applies creates into real character data (same finish side effects as in-game).

**Repos:** `ProvinceSystem/backend` · `Workspace/rpcharacters`

**Depends on:** [02-creation-catalog-sync](./02-creation-catalog-sync.md) · [03-character-session-api](./03-character-session-api.md) · [01-attribute-point-buy](./01-attribute-point-buy.md)

## Plan

1. **API create** — `POST /characters` with stage answers + attribute ranks; server re-validates; soft slot check from roster mirror vs **per-player** `max_alive_characters` (from last online roster push) or catalog defaults ∩ hard_cap; plugin confirms on ingest.
2. **API list** — roster mirror + pending creates for session UUID; includes `max_alive_characters` and `alive_count` for Create enablement.
3. **Ingest** — RPC pulls pending on login/reload/`/rpcharacter pending sync`; writes character JSON; acks applied; pushes roster (when player online, includes LP-based `max_alive_characters`).
4. **Idempotency** — `client_request_id` unique per player; create id reused as character id.
5. **Dead** — roster includes `DEAD`/`MISSING`; create only when free alive slot (plugin wins on conflict).

## Verify

- [x] Web create with invalid attribute spend (≠12 or rank>2) → 400  
- [ ] Valid create → pending → RPC apply → appears in `characterdata` *(operator on staging)*  
- [x] List shows roster + pending; applied ack + roster push surfaces ALIVE  
- [x] Over soft slot limit → rejected  
- [x] Roster `max_alive_characters` → list + soft-check use player entitlement  
- [ ] In-game create still works with same attribute sheet *(unchanged path + roster push)*  

## Implemented

- Tables `character_creates`, `character_roster`, `character_player_meta`
- `src/characters/creates.py` + `roster.py`
- Routes: `POST/GET /characters`, `GET /characters/plugin/pending`, `POST /characters/plugin/applied`, `PUT /characters/plugin/roster` (optional `max_alive_characters`)
- RPCharacters: `CharacterIngestService`, `RosterSyncService` (online LP max), client methods, UUID load/save, join/reload/finish/permakill triggers, `/rpcharacter pending sync`
- Smoke: `backend/scripts/character_ingest_smoke.py`

## Out of scope

Kit grant; knife; skins; editing every persona field on the web (alias etc. can be later); frontend wizard (05).
