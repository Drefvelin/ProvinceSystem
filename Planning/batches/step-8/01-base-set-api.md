# Batch 8.01 — `base_set` API

**Plan + build:** Persist and validate player-picked BaseSet id; enforce kind↔`base_set` pairing; expose on staff + plugin payloads.

**Repos:** `ProvinceSystem/backend`

**Depends on:** [00-index](./00-index.md) · Step 7 harness green

## Plan

1. Add SQLite column `base_set` (TEXT, nullable for legacy rows; **required** on new submits for enabled kinds).
2. Enabled kinds: `armor_set`, `handheld`, `large_handheld`, `bow`, `large_bow`, `crossbow`. **Reject** `item` (disabled). Later kinds (`item_3d`, `shield`) stay out.
3. `POST /skins/submissions` multipart: accept `base_set`; validate against kind allowlists in [00-index](./00-index.md) (e.g. `swords` only with `handheld`; `shortbows` only with `bow`).
4. Persist in DB + `meta.json`; include in status, staff pending, Discord lists, and `GET /skins/plugin/approved`.
5. Reject: missing `base_set`; wrong allowlist for kind; unknown id; disabled kind.
6. Smoke: armor + handheld valid/invalid pairs; optional bow + `shortbows`.

## Build

| File | Action |
|------|--------|
| `skins/db.py` | migrate `base_set` column |
| `skins/submissions.py` | kind set + allowlists + store + list fields |
| `api/skins_routes.py` | Form field `base_set` |
| `scripts/skins_e2e_smoke.py` | assert allowlists / pairing |
| [05-skins-system.md](../../05-skins-system.md) | schema sync |

## Verify

```bash
cd ProvinceSystem/backend
python scripts/skins_e2e_smoke.py
```

- [x] armor_set + `iron` → 200; armor + `swords` → 400  
- [x] handheld + `swords` → 200; handheld + `spears` → 400  
- [x] large_handheld + `spears` + grip → 200  
- [x] kind=`item` → 400  
- [x] `GET /plugin/approved` includes `base_set`  

**Implemented:** `base_set` column + kind allowlists/pairing; bow kinds accepted with provisional sizes; smoke green.

## Out of scope

Frontend dropdowns (02); ArmourShop pull (03+); bow pack writers (07).
