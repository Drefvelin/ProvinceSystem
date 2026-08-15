# Step 47.07 — Docs & verify

**Repos:** Planning + `ProvinceSystem`  
**Depends on:** [02](./02-calavorn-terrain-fertility.md)–[06](./06-trade-labels.md)

## Goal

Close out Step 47 in hub docs and STAGING; operator checklist for Calavorn map modes and multi-mode labels.

## Docs to update

| File | Action |
|------|--------|
| [step-47/00-index.md](./00-index.md) | Status → **47.01–47.07 done** |
| [Planning/batches/README.md](../README.md) | Add step-47 row |
| [16-map-platform.md](../../16-map-platform.md) | Requirement 4: nation + title + trade labels |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | New **M3b** or extend M3 with Step 47 items |
| [01-current-state.md](../../01-current-state.md) | Calavorn province modes + title labels |
| [STAGING.md](../../../STAGING.md) | Step 47 operator checklist |
| [step-40/01-planning-lock.md](../step-40/01-planning-lock.md) | Cross-ref: title/trade labels moved to step 47 |

## STAGING operator checklist (preview)

### Calavorn province layers

- [ ] `output/main/maps/terrain_map.png` + `fertility_map.png` present
- [ ] `output/main/maps/trade_map.png` + `prosperity_map.png` present (spoof OK)
- [ ] `/map/main` toolbar: terrain, fertility, trade, prosperity selectable
- [ ] Terrain / fertility hover shows province meta
- [ ] Trade / prosperity hover works
- [ ] Note in STAGING: `input/main/province_data.json` is spoof until SF export

### Multi-mode labels (`/map/main`)

- [ ] Nation mode: unchanged from Step 40 (+ full-realm overview)
- [ ] Kingdom / duchy / county / empire: names on blobs
- [ ] Trade: guild names on blobs
- [ ] Terrain / fertility / prosperity: **no** labels
- [ ] Labels above hover wash; 1% hover scale
- [ ] Pick, nation drill, modal unchanged

### Tests

- [x] `npm test` (mapLabels + titleProvinces)
- [x] `npm run build`
- [ ] Python trade compile smoke if compile changed

## Verify

- [x] Batch docs 47.01–47.07 written
- [x] All implementation batches complete
- [x] Operator checklist copied to STAGING (human ticks on staging deploy)

## Status

**Done.**

## Next

[step-41 staff map access](../step-41/00-index.md) · [step-42 capitals](../step-42/00-index.md).
