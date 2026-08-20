# Step 43.05 — Docs verify + STAGING

**Repos:** Planning + `ProvinceSystem` + `Workspace/simplefactions`  
**Depends on:** [01](./01-planning-lock.md)–[04](./04-frontend-zoc-hover.md)

## Goal

Close step 43 in hub docs and STAGING; operator checklist for fort ZOC hatch overlay on staging deploy.

## Docs updated

| File | Action |
|------|--------|
| [step-43/00-index.md](./00-index.md) | Status → **43.01–43.05 done**; next → step 44 |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | M6 done; 43.01–43.05 checked; next → step 44 |
| [16-map-platform.md](../../16-map-platform.md) | Req 9 done; build order step 43 done |
| [01-current-state.md](../../01-current-state.md) | Step 43 shipped; next → step 44 |
| [03-roadmap.md](../../03-roadmap.md) | Track H6 done; next → step 44 |
| [batches/README.md](../README.md) | step-43 row → **done** |
| [Installations.md](../../../../simplefactions/Documentation/Installations.md) | ZOC complete; PS + FE pipeline |
| [STAGING.md](../../../STAGING.md) | Step 43 operator checklist |

## Automated tests

**Backend** (`ProvinceSystem/backend/src`):

```bash
python -m unittest discover -s scripts/mapgen -p "test_zocgen.py" -v
python -m unittest discover -s scripts/loader -p "test_markers.py" -v
```

From `ProvinceSystem/backend`:

```bash
python -m unittest src.api.test_map_access -v
```

- [x] 4 tests pass (`test_zocgen.py`)
- [x] 17 tests pass (`test_markers.py` incl. fort enrichment)
- [x] 20 tests pass (`test_map_access` incl. ZOC 404 + upload trigger)

**Frontend** (`ProvinceSystem/frontend`):

```bash
npm test
npm run build
```

- [x] 113 tests pass (11 files incl. `fortZoc.test.ts`)
- [x] `npm run build` passes (`/map/main`, `/map/r3b1rth`)

**SF:**

```bash
mvn -q package -DskipTests
```

- [x] `mvn -q package -DskipTests` (simplefactions)

## STAGING operator checklist

See [STAGING.md](../../../STAGING.md) **Step 43**. Summary:

### SF export + regen

- [ ] Operational fort exists (construction completed — step 55)
- [ ] Pending fort **not** in `forts[]` until operational
- [ ] After SF regen: `map_markers.json` contains `forts[]` with `zoc_provinces`, `center_x`/`center_z`
- [ ] `mvn -q package -DskipTests` (simplefactions)

### PS backend

- [ ] `output/main/zoc/{fort_id}.png` exists after regen
- [ ] `GET /main/data/markers` → `forts[]` entry has `overlay` + `zoc_url`
- [ ] `GET /main/zoc/{fort_id}.png` returns PNG (200)
- [ ] Stale ZOC PNG removed when fort deconstructed

### Frontend (`/map/main`)

- [ ] Political mode (`nation`): hover **fort** pin → diagonal hatch over ZOC provinces
- [ ] Hover **port** / **airport** → no hatch
- [ ] Hover nation territory (not pin) → nation fill overlay; no ZOC
- [ ] `terrain` mode → no installation markers; no ZOC
- [ ] Nation drill stack + labels still work (regression)

### Staff map (`/map/r3b1rth`)

- [ ] Fort fixture on `dev` map: ZOC PNG loads with Bearer auth

## Verify

- [x] Batch docs 43.01–43.05 written
- [x] All implementation batches complete
- [x] Operator checklist in STAGING (human ticks on staging deploy)
- [x] Hub "next build" → step-44
- [x] Backend + frontend + SF automated tests pass

## Status

**Done** (2026-08-19).

## Next

[step-44 war layer](../step-44/00-index.md) — blocked on SF war rework.
