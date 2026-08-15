# Step 49.04 — Pick/hover coordinate pipeline

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [03-map-viewport](./03-map-viewport.md)

## Goal

Fix nation hover, province tooltips, and region pick after 49.03 pan/zoom. Cursor events map to correct **map pixel indices** at any `displayScale` and translate.

## Problem

[`getMapCoords`](../../../frontend/app/hooks/useMapCoords.ts) assumed uniform canvas-rect scaling. After 49.03, the pick canvas sits inside a CSS-transformed inner layer, so linear rect scaling breaks when zoomed or panned.

## Build

| File | Action |
|------|--------|
| `frontend/app/hooks/useMapCoords.ts` | extend — `MapPickViewport` type + `screenToMap` viewport path |
| `frontend/app/hooks/useMapCoords.test.ts` | create — legacy, fit-scale, zoom, pan, bounds |
| `frontend/app/hooks/useMapHover.ts` | pass `viewportCoordsRef` to `getMapCoords` |
| `frontend/app/components/map/MapCanvas.tsx` | populate `viewportCoordsRef` from `useMapViewport` |
| `frontend/app/components/MapViewer.tsx` | create ref; wire to `MapCanvas` and `useMapHover` |

## `getMapCoords` API

```typescript
type MapPickViewport = {
  displayScale: number
  translateX: number
  translateY: number
  viewportElement: HTMLDivElement | null
  mapSize: { w: number; h: number }
}

getMapCoords(event, canvas, mapId, viewport?)
```

**Viewport path:** viewport-local coords → `screenToMap` → floor → bounds check against `mapSize`.

**Legacy path:** unchanged rect-based scaling when viewport is absent.

## Wiring

`MapCanvas` owns `useMapViewport` and writes live transform state into `viewportCoordsRef` each render. `MapViewer` holds the ref and passes it to `useMapHover`, which calls `getMapCoords` on each rAF tick.

`useRegionHover` / `useProvinceHover` unchanged — they consume floored map pixels for `getImageData`.

## Verify

- [x] `npm test -- useMapCoords` passes (7 tests)
- [x] `npm run build` passes
- [x] Hover/pick uses viewport transform via `screenToMap`

## Out of scope

- Live `mapZoom` → labels (49.05)
- Viewport reset on `mapId` / `mapType` (49.05)
- Resize / late `mapSize` edge cases (49.06)
