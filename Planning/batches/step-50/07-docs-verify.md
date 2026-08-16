# Step 50.07 — Docs verify + STAGING

**Repos:** Planning + `ProvinceSystem`  
**Depends on:** [02](./02-promote-dev-world.md)–[06](./06-sf-map-reference.md)

## Goal

Close step 50 in hub docs and STAGING; separate **repo prep** checks from **production cutover** checks.

## Docs to update

| File | Action |
|------|--------|
| [step-50/00-index.md](./00-index.md) | All batches **done** |
| [batches/README.md](../README.md) | step-50 row → done |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | S5 cutover; Calavorn → Adavaar on main |
| [01-current-state.md](../../01-current-state.md) | `/map/main` = Adavaar (after cutover) |
| [09-map-system.md](../../09-map-system.md) | `main` = live world; SF `dev` until 50.06 |
| [STAGING.md](../../../STAGING.md) | Step 50 operator checklist |
| Step 47 / STAGING "Calavorn" sections | Reword: province layers on **main** = Adavaar (S5) |

## Automated verify

**After 50.04 (repo prep):**

```bash
cd ProvinceSystem/backend/src
python -m scripts.map_tools.test_province_geometry
cd ../..
python -m unittest src.api.test_map_access -v
```

**Frontend (after 50.05):**

```bash
cd ProvinceSystem/frontend
npm test
npm run build
```

## STAGING — repo prep (50.02–50.04)

### World (50.02)

- [x] `defines/main/provinces.txt` is Adavaar (806 provinces; province 705 exists)
- [x] `input/main/map.png` + `provinces.png` present
- [x] Geometry artifacts committed for `main`
- [x] `test_province_geometry` passes

### Live data (50.03–50.04)

- [x] `input/main/nation.json` copied from live PS `input/dev/` (50.03)
- [x] `fullregen main` completed locally; `output/main/maps/*` present
- [x] `defines/main/nation.json` — Lantan; markers enrich with centroids (local loader)
- [ ] `GET /main/data/nation` returns S5 factions (local API — operator after deploy)

**Note:** SF still on `map-reference: dev` on live MC during repo prep.

## STAGING — production cutover (50.05–50.06)

### Website (after 50.05 deploy)

- [ ] `/map/main` title shows **Adavaar**
- [ ] `MAP_BOUNDS` correct (6400)
- [ ] Nations, labels, terrain/trade modes work
- [ ] Settlement pins when zoomed in (step 42)

### MC + SF (50.06 — operator)

- [ ] SF `map-reference: main` on live server
- [ ] TFMCWeb gateway configured
- [ ] Claim/regen on MC updates `/map/main` after regen

### Regression

- [ ] Staff `/map/r3b1rth` per 50.01 policy (A/B/C)
- [ ] Pan/zoom, modals, nation drill unchanged

## Status

**Planned.**

## Next

Resume [step-43 forts](../step-43/00-index.md) on the live Adavaar map.
