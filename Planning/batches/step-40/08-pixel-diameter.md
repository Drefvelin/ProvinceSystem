# Step 40.08 — Pixel diameter and scaled font

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [07-label-visibility](./07-label-visibility.md)

## Goal

Per province blob, pick the farthest province pair by **map-pixel distance** (not graph hops) and scale label `fontSize` from segment length so large nations read larger than small ones.

## Locked rules

| Rule | Choice |
|------|--------|
| Blobs | One label per connected province component (unchanged) |
| Endpoints | `pixelDiameterEndpoints` — max Euclidean distance between centroids |
| Font | `fontSizeForSegment(segmentPx)` with min/max clamps; no `textLength` stretch |
| Visibility / drill | Unchanged from 40.07 |

## Constants (shipped)

| Constant | Value |
|----------|-------|
| `LABEL_MIN_FONT_SIZE` | 14 |
| `LABEL_MAX_FONT_SIZE` | 42 |
| `LABEL_FONT_SCALE` | 0.07 |
| `LABEL_FONT_SIZE` | 28 (legacy reference) |

## Build

| File | Action |
|------|--------|
| [`frontend/app/lib/mapLabels.ts`](../../../frontend/app/lib/mapLabels.ts) | `pixelDiameterEndpoints`, `fontSizeForSegment`, `segmentPx` + `fontSize` on spec |
| [`frontend/app/lib/mapLabels.test.ts`](../../../frontend/app/lib/mapLabels.test.ts) | Pixel diameter + font scaling tests |
| [`frontend/app/components/map/LabelLayer.tsx`](../../../frontend/app/components/map/LabelLayer.tsx) | Per-label `fontSize`; stroke scales with font |

## Verify

- [x] `npm test` passes (27 tests)
- [x] `npm run build` passes
- [ ] `/map/main`: Tiayeouph / Drakhanate blobs use farthest pixel pair
- [ ] Nimbus visibly larger than House Tenceur
- [ ] Grand Drakhanate: one label per disconnected blob, each sized to blob span
- [ ] 40.07 visibility/drill unchanged

## Out of scope

- Single merged suzerain full-border label (deferred until river/sea provinces)
- Curved `textPath`
- Live pan/zoom font scaling

## Status

**Done** (40.08).

## Next

[step-41 staff map access](../step-41/00-index.md).
