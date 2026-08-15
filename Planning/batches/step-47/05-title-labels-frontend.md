# Step 47.05 — Title labels (frontend)

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [04-title-province-rollup](./04-title-province-rollup.md)

## Goal

Show region names on `/map/main` for `county`, `duchy`, `kingdom`, and `empire` modes using the same `LabelLayer` pipeline as nations.

## Locked rules

| Rule | Choice |
|------|--------|
| Modes | `county`, `duchy`, `kingdom`, `empire` |
| Visibility | All regions with `rgb` in active mode JSON (no overlord hide) |
| Layout | Reuse `labelsForProvinces`, inset grid, min area/province thresholds |
| Names | Strip `§` codes if present (`cleanRegionName`) |
| Geometry | Same `useMapGeometry` for `main` |
| Hover | 1% scale on hovered region (`selectedRegionId`) — unchanged from recent work |
| Z-order | Labels above hover wash, below pick canvas |

## Build

| File | Action |
|------|--------|
| [`frontend/app/lib/mapLabels.ts`](../../../frontend/app/lib/mapLabels.ts) | `computeVisibleRegionLabels(mapType, regionData, titleLayers, …)` |
| [`frontend/app/lib/mapLabels.ts`](../../../frontend/app/lib/mapLabels.ts) | `provincesForRegionLabel` — nation branch unchanged; title branch uses rollup |
| [`frontend/app/hooks/useTitleLayerData.ts`](../../../frontend/app/hooks/useTitleLayerData.ts) | Load title layers when mode needs rollup |
| [`frontend/app/components/MapViewer.tsx`](../../../frontend/app/components/MapViewer.tsx) | Replace `mapType !== "nation"` gate with label-mode allowlist |
| [`frontend/app/lib/mapLabels.test.ts`](../../../frontend/app/lib/mapLabels.test.ts) | Title mode label tests |

## Verify

- [x] `/map/main` kingdom mode: kingdom names on each province blob (e.g. Revenor, Domenia)
- [x] County mode: county names on blobs
- [x] Duchy / empire: names visible on correct blobs
- [x] Exclaves: separate labels per connected component
- [x] Nation mode: unchanged (full realm, drill, Cordelia island, etc.)
- [x] Switching modes clears/recalculates labels; pick canvas updates
- [x] `npm test` + `npm run build`

## Out of scope

- Title drill scopes
- Trade labels (47.06)

## Status

**Done.**

## Next

[06-trade-labels](./06-trade-labels.md).
