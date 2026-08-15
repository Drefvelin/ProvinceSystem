# Step 48.04 — Docs & verify

**Repos:** Planning + `ProvinceSystem`  
**Depends on:** [02](./02-label-neighbor-geometry.md)–[03](./03-frontend-wiring.md)

## Goal

Close out Step 48 in hub docs and STAGING; operator checklist for regen and visual QA.

## Docs to update

| File | Action |
|------|--------|
| [step-48/00-index.md](./00-index.md) | Status → **48.01–48.04 done** |
| [Planning/batches/README.md](../README.md) | Add step-48 row |
| [16-map-platform.md](../../16-map-platform.md) | Requirement 4c: label neighbor graph |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | New **M3c** section |
| [01-current-state.md](../../01-current-state.md) | Label graph + regen note |
| [STAGING.md](../../../STAGING.md) | Step 48 operator checklist |
| [step-40/02-map-geometry.md](../step-40/02-map-geometry.md) | Cross-ref: label neighbors added in step 48 |
| [step-47/01-planning-lock.md](../step-47/01-planning-lock.md) | Cross-ref: geometry row mentions `province_label_neighbors` |

## STAGING operator checklist (preview)

### Geometry artifacts

- [ ] `defines/main/province_label_neighbors.json` present on staging
- [ ] `GET /main/data/province_label_neighbors` returns JSON (200)

### Regen (when `provinces.png` changes)

```bash
cd backend/src
python -m scripts.map_tools.build_province_geometry main
python -m scripts.map_tools.test_province_geometry
```

Commit all four geometry outputs: `province_neighbors`, `province_centroids`, `province_label_grid`, `province_label_neighbors`.

### Visual QA (`/map/main`)

- [ ] Southern island / channel nations: one label per water-connected blob (spot-check)
- [ ] Land exclaves: still multiple labels with same name where expected
- [ ] Nation drill, title modes, trade labels: no hover/pick regression
- [ ] Kingdom mode hover works (step 47 fix still good)

### Automated

- [ ] `python -m scripts.map_tools.test_province_geometry` passes
- [ ] `npm test` + `npm run build` pass

## Verify

- [x] All docs rows updated
- [x] STAGING Step 48 section added
- [x] Checkpoint in [00-index](./00-index.md) satisfied

## Status

**Done.**
