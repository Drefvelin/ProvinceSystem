# Step 49.05 — Live zoom labels + viewport reset

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [04-pick-hover](./04-pick-hover.md)

## Goal

Complete the step-40 label zoom-hide stub: labels hide when `userScale > 1.5`, and viewport resets to `(userScale=1, translate=0,0)` on map or mode change.

## Problem

[`MapViewer.tsx`](../../../frontend/app/components/MapViewer.tsx) passed a fixed `mapZoom={DEFAULT_MAP_ZOOM}` stub. [`MapCanvas.tsx`](../../../frontend/app/components/map/MapCanvas.tsx) owned real `userScale` from `useMapViewport` but did not use it for label visibility. Pan/zoom state persisted across `mapType` / `mapId` changes.

## Build

| File | Action |
|------|--------|
| `frontend/app/components/map/MapCanvas.tsx` | use `viewport.userScale` for labels; `resetViewport` on `mapId`/`mapType` |
| `frontend/app/components/MapViewer.tsx` | remove `DEFAULT_MAP_ZOOM` stub and `mapZoom` prop |

## Changes

**Label visibility:** `shouldShowLabelsAtZoom(viewport.userScale)` — uses user zoom (1…3), not `displayScale`. `LABEL_MAX_ZOOM = 1.5` unchanged.

**Viewport reset:**

```tsx
useEffect(() => {
  viewport.resetViewport();
}, [mapId, mapType, viewport.resetViewport]);
```

Runs in `MapCanvas` (owns `useMapViewport`), aligned with MapViewer's existing hover/drill clears on mode change.

**MapViewer:** removed `mapZoom={DEFAULT_MAP_ZOOM}` — no new state needed; `MapCanvas` re-renders on `userScale` changes internally.

## Verify

- [x] `npm run build` passes
- [x] Labels driven by live `userScale`
- [x] Viewport resets on `mapId` / `mapType` change

## Out of scope

- Resize / late `mapSize` edge cases (49.06)
- STAGING / manual QA (49.07)
