# Step 40.04 — Frontend layer

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [03-layout-lib](./03-layout-lib.md)

## Goal

Render nation name labels on `/map/main` in **nation** mode: fetch geometry JSON, run `computeNationLabels`, draw SVG `LabelLayer` in `MapCanvas`.

## Build

| File | Action |
|------|--------|
| [`frontend/app/hooks/useMapGeometry.ts`](../../../frontend/app/hooks/useMapGeometry.ts) | Fetch `province_neighbors` + `province_centroids` for `main` |
| [`frontend/app/components/map/LabelLayer.tsx`](../../../frontend/app/components/map/LabelLayer.tsx) | SVG text from `NationLabelSpec[]` |
| [`frontend/app/components/MapViewer.tsx`](../../../frontend/app/components/MapViewer.tsx) | `useMemo` labels; pass to canvas |
| [`frontend/app/components/map/MapCanvas.tsx`](../../../frontend/app/components/map/MapCanvas.tsx) | `labels` prop; layer after pick canvas |

## Layer order (MapCanvas)

```text
base map
pick canvas (invisible)
LabelLayer
province mode overlay
hover overlay
drill stack overlays
```

## Visibility (v1)

| Condition | Labels |
|-----------|--------|
| `mapId === "main"` && `mapType === "nation"` | Shown when geometry + nation data loaded |
| Other map or mode | Hidden |
| Geometry fetch fails | Hidden (console error; map still works) |

## Styling (minimal — polish in 40.05)

- Fill `#2a1f14`, Fraunces, `LABEL_FONT_SIZE` (28 map px)
- No stroke/halo or zoom-hide yet

## Verify

- [ ] `/map/main` nation mode: nation names along territories
- [ ] Kingdom/duchy/etc.: labels hidden
- [ ] `/map/dev`: no labels
- [ ] Hover / drill / modal / pick unchanged
- [x] `npm test` and `npm run build` pass
- [ ] Operator: backend running with geometry JSON (40.02)

## Out of scope

- Text halo, `LABEL_MAX_ZOOM` ([05-label-polish](./05-label-polish.md))
- Cross-nation collision
- Non-nation modes

## Status

**Done** (40.04). Next batch: [05-label-polish](./05-label-polish.md).
