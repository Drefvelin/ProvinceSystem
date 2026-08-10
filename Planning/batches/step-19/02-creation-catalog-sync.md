# Batch 19.02 — Creation catalog sync

**Plan + build:** RPCharacters pushes a full-replace **creation catalog** to ProvinceSystem (ArmourShop catalog pattern). Website wizard reads only this snapshot.

**Repos:** `Workspace/rpcharacters` · `ProvinceSystem/backend`

**Depends on:** [01-attribute-point-buy](./01-attribute-point-buy.md) (formula must be in the payload)

## Plan

1. **Payload** — stages (id, type, order, copy, min/max/points, keys, dependencies); races; traits by key; classes (from MMOCore at sync time); validation (name/age/description/clues); slot limits by group; **attribute point-buy** `{ pool: 12, max_rank: 2, cost_for_rank: [1, 2], attributes: [...] }`.
2. **Plugin** — build snapshot on enable/reload + `/rpcharacter catalog sync`; `PUT` with plugin key; fail-soft on enable.
3. **API** — store one SQLite/JSON snapshot; **session-gated** GET (`scope=character`).
4. **Empty catalog** — `require_synced_creation_catalog()` exported for later create API (create still out of scope).

## Verify

- [x] PUT fixture stores catalog (`scripts/creation_catalog_smoke.py`)
- [x] Attribute formula present: pool 12, max_rank 2, cost_for_rank `[1, 2]`
- [x] Web GET 401 without session / bad bearer
- [x] Web GET 200 with seeded character-scoped session *(production redeem waits on 19.03)*
- [ ] Operator: reload RPC on staging → catalog `updated_at` advances; trait/race/class lists non-empty

## Implemented

- Backend: `creation_catalog` table; `src/characters/creation_catalog.py`; `PUT /characters/plugin/creation-catalog`; `GET /characters/creation-catalog` (Bearer, `scope=character`)
- RPCharacters: `characters-api` config; `ProvinceSystemClient.pushCreationCatalog`; `CreationCatalogSyncService`; push on `loadConfigs`; `/rpcharacter catalog sync`
- Smoke: `backend/scripts/creation_catalog_smoke.py` (seeds character session until 19.03 redeem)

## Out of scope

Create/list characters; frontend wizard; character redeem (19.03).
