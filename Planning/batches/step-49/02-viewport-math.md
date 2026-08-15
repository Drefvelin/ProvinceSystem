# Step 49.02 — Viewport math + hook

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Goal

Ship the pan/zoom **math library** and **React hook** per the planning lock. No UI integration in this batch — `MapCanvas` stays unchanged until [03-map-viewport](./03-map-viewport.md).

## Fit-scale model

Today the map uses `w-full` (fit-to-width). At user zoom `1`, the displayed map width must equal viewport width. Clamp formulas in the lock use `Mw·s`; resolve this with two scales:

| Scale | Formula | Role |
|-------|---------|------|
| **`fitScale`** | `viewportW / mapW` | Width-fit; matches current `w-full` behaviour |
| **`userScale`** | `1 … 3` (`MAP_ZOOM_MIN` / `MAP_ZOOM_MAX`) | User-controlled zoom |
| **`displayScale`** | `fitScale * userScale` | Used in clamp, zoom-at-point, and `screenToMap` |

Inner layer in 49.03 will be sized at `mapW × mapH` CSS pixels; transform is `translate(tx, ty) scale(displayScale)` with `transform-origin: 0 0`.

## Build

| File | Action |
|------|--------|
| `frontend/app/lib/mapViewportMath.ts` | create — constants, fit scale, clamp, zoom-at-point, screen/map transforms |
| `frontend/app/lib/mapViewportMath.test.ts` | create — clamp, zoomAtPoint, round-trip |
| `frontend/app/hooks/useMapViewport.ts` | create — ResizeObserver, wheel, middle-drag, reset |

## `mapViewportMath.ts` API

**Constants:**

```typescript
MAP_ZOOM_MIN = 1
MAP_ZOOM_MAX = 3
MAP_ZOOM_WHEEL_FACTOR = 1.1
```

**Functions:**

| Function | Role |
|----------|------|
| `computeFitScale(viewport, map)` | `viewport.w / map.w` |
| `computeDisplayScale(fitScale, userScale)` | `fitScale * userScale` |
| `clampUserScale(s)` | Clamp to `[MAP_ZOOM_MIN, MAP_ZOOM_MAX]` |
| `clampTranslate(viewport, map, displayScale, tx, ty)` | Lock algorithm; pin axis to `0` when `map·displayScale ≤ viewport` |
| `zoomAtPoint(viewport, map, transform, cursor, wheelDelta)` | Derive zoom direction from `deltaY`; apply factor; return new `{ userScale, translateX, translateY }` |
| `mapToScreen(mapX, mapY, displayScale, translate)` | Forward transform |
| `screenToMap(vx, vy, displayScale, translate)` | Inverse; returns floats (caller floors for pick) |
| `viewportTransformStyle(displayScale, tx, ty)` | CSS string: `translate(txpx, typx) scale(s)` |

## `useMapViewport.ts` API

```typescript
type UseMapViewportOptions = {
  mapSize: Size
  enabled?: boolean  // default true
}

type UseMapViewportResult = {
  viewportRef: RefObject<HTMLDivElement>
  userScale: number           // for labels in 49.05
  translateX: number
  translateY: number
  displayScale: number
  fitScale: number
  isPanning: boolean
  transformStyle: string
  cursorClassName: string     // cursor-grab / cursor-grabbing
  resetViewport: () => void
  screenToMapFromClient: (clientX, clientY) => { x, y } | null
}
```

**DOM listeners** (on `viewportRef`; `passive: false` for wheel):

| Event | Behaviour |
|-------|----------|
| `wheel` | `preventDefault`; `zoomAtPoint` with cursor relative to viewport rect |
| `mousedown` (button `1`) | Start pan; record last client position |
| `mousemove` (window) | If panning, delta → translate → clamp |
| `mouseup` / `mouseleave` | End pan on middle button |
| `contextmenu` | `preventDefault` while panning |
| `auxclick` | `preventDefault` for middle button |

**Re-clamp on resize:** when `viewportSize` or `mapSize` changes, re-run `clampTranslate` with current scale/translate.

## Verify

- [x] `npm test -- mapViewportMath` passes (7 tests)
- [x] `npm run build` passes (hook compiles; unused until 49.03)
- [x] No changes to `MapCanvas.tsx` or `useMapCoords.ts`

## Out of scope

- `MapViewport` component / CSS layout (49.03)
- Pick/hover coordinate pipeline (49.04)
- Label `mapZoom` wiring (49.05)
- Mobile pinch
