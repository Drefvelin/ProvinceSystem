# Step 50.05 — Registry + frontend labels

**Repos:** `ProvinceSystem`  
**Depends on:** [04-regen-main](./04-regen-main.md)

## Goal

Rename public map display from Calavorn → Adavaar and fix Adavaar viewport bounds in the frontend.

## Build

| File | Change |
|------|--------|
| [`backend/src/config/maps.yml`](../../../backend/src/config/maps.yml) | `main.display_name: Adavaar` |
| [`frontend/app/components/map/types.ts`](../../../frontend/app/components/map/types.ts) | `MAP_DISPLAY_NAMES.main: "Adavaar"`; `MAP_BOUNDS.main: 6400` |
| [`frontend/app/lib/map/api.test.ts`](../../../frontend/app/lib/map/api.test.ts) | Update fixture display name |
| [`backend/src/api/test_map_access.py`](../../../backend/src/api/test_map_access.py) | Registry fixture `Calavorn` → `Adavaar` if hardcoded |

### `dev` registry (per 50.01 lock)

| Policy | `maps.yml` change |
|--------|-------------------|
| **A — Staging mirror** | `dev.display_name: "Adavaar (staging)"`; keep staff gate |
| **B — Calavorn archive** | `dev.display_name: Calavorn`; staff browses S4 |
| **C — Retire** | Remove `dev` entry or keep hidden |

### Nav / routes

- `/map/main` — unchanged; now Adavaar
- `/map/r3b1rth` — still `mapId=dev` per [STAFF_MAP_PAGE_ROUTES](../../../frontend/lib/map/api.ts); label text may update in shell nav if it says "Adavaar" for staff link

Search repo for hardcoded **Calavorn** on `main` and update docs in batch 50.07 (not all in this batch).

## Verify

- [x] `npm test` + `npm run build`
- [ ] `/map/main` page title / toolbar shows Adavaar
- [ ] Map renders at correct scale (no clipped edges — bounds 6400)
- [ ] `python -m unittest src.api.test_map_access -v`

## Status

**Planned.**

## Next

[06-sf-map-reference](./06-sf-map-reference.md).
