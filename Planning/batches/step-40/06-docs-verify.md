# Step 40.06 — Docs verify

**Repos:** Planning + STAGING  
**Depends on:** [02-map-geometry](./02-map-geometry.md) · [03-layout-lib](./03-layout-lib.md) · [04-frontend-layer](./04-frontend-layer.md) · [05-label-polish](./05-label-polish.md)

## Goal

Close Step 40 in hubs; add STAGING operator checklist; point next build to Step 41 (staff map access).

## Plan

1. Mark batches 01–06 done in [00-index](./00-index.md) when code ships.
2. Update [08-implementation-checklist.md](../../08-implementation-checklist.md) — M3 labels **done**; M4 staff maps → step-41 **next**.
3. Update [03-roadmap.md](../../03-roadmap.md) Track H — step 40 nation labels done; next step 41.
4. Update [16-map-platform.md](../../16-map-platform.md) — req 4 done (frontend SVG straight text); build order insert 40.
5. Update [01-current-state.md](../../01-current-state.md) — nation labels shipped; next build step-41.
6. Update [12-end-to-end-flows.md](../../12-end-to-end-flows.md) · [13-tfmcweb.md](../../13-tfmcweb.md) · [batches/README.md](../README.md).
7. Add **STAGING Step 40** operator checklist (human verify on staging).
8. Update [step-39/00-index.md](../step-39/00-index.md) footer — step 40 nation labels shipped; next build step-41.
9. Add chronicle cross-ref in [step-45/00-index.md](../step-45/00-index.md) — political state JSON + `LabelLayer` reuse.

## STAGING operator checklist (draft)

- [ ] `defines/main/province_neighbors.json` and `province_centroids.json` present on staging
- [ ] `/map/main` nation mode: nation names along territory long axis (straight text)
- [ ] Exclaves get separate labels; small nations below threshold have no label
- [ ] Labels hidden when `mapType !== "nation"` (switch to kingdom/duchy/etc. — no labels)
- [ ] Cream halo readable on busy terrain
- [ ] Hover / drill / modal / pick unchanged
- [ ] Optional dev check: temporarily set `mapZoom={2}` in `MapViewer` — labels hidden
- [ ] Regen when `provinces.png` changes: `python -m scripts.map_tools.build_province_geometry main`

## Verify

- [x] All hub "next build" links → step-41
- [x] Step 40 index status → done (code complete)
- [x] No stale "step-40 next" / "backend curved labels" in active hub docs

## Status

**Done.**

## Next

[step-41 staff map access](../step-41/00-index.md).
