# Step 40.09 — Inset label corridors

**Repos:** `ProvinceSystem` frontend + backend geometry tooling  
**Depends on:** [08-pixel-diameter](./08-pixel-diameter.md)

## Goal

Keep nation labels inside territory blobs by searching for the longest axis whose **text corridor** (chord + arc bulge + glyph height) clears the blob border, instead of using raw centroid farthest pairs.

## Locked rules

| Rule | Choice |
|------|--------|
| Blob geometry | 512-wide dominant-province grid from `provinces.png` |
| Clearance | BFS distance transform per component at label time |
| Margin | `max(40px, fontSize × 0.38 + segment × 0.08 + 8px)` |
| Search | Longest valid candidate-pair segment; fallback ladder 1 → 0.75 → 0.5 margin; centroid seed if none fit |
| Drill / visibility | Unchanged from 40.07 |

## Constants

| Constant | Value |
|----------|-------|
| `LABEL_MIN_INSET_PX` | 40 |
| `LABEL_INSET_PADDING_PX` | 8 |
| `LABEL_GRID_WIDTH` | 512 |

## Build

| File | Action |
|------|--------|
| [`backend/src/scripts/map_tools/province_geometry.py`](../../../backend/src/scripts/map_tools/province_geometry.py) | `build_label_grid`, write `province_label_grid.json` + `.bin.gz` |
| [`backend/src/api/data_routes.py`](../../../backend/src/api/data_routes.py) | `GET /{map}/data/province_label_grid_bin` |
| [`frontend/app/lib/labelBlobGeometry.ts`](../../../frontend/app/lib/labelBlobGeometry.ts) | Mask, DT, corridor check, `insetLabelEndpoints` |
| [`frontend/app/lib/mapLabels.ts`](../../../frontend/app/lib/mapLabels.ts) | Optional `grid` in options; wire inset search |
| [`frontend/app/hooks/useMapGeometry.ts`](../../../frontend/app/hooks/useMapGeometry.ts) | Fetch grid meta + gzip binary |
| [`frontend/app/components/MapViewer.tsx`](../../../frontend/app/components/MapViewer.tsx) | Pass `labelGrid` to label compute |

## Regen

When `provinces.png` changes:

```bash
cd backend/src
python -m scripts.map_tools.build_province_geometry main
```

## Verify

- [x] `python -m scripts.map_tools.test_province_geometry` passes
- [x] `npm test` passes
- [x] `npm run build` passes
- [ ] `/map/main`: Drakhanate / Eoridcois labels stay inside blob
- [ ] Drilled suzerain direct-holdings label respects inset
- [ ] Dev map without grid falls back to centroid diameter

## Status

**Done** (40.09).

## Next

[step-41 staff map access](../step-41/00-index.md).
