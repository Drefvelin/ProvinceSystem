# Step 49.06 — Resize, late mapSize, middle-click edge cases

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [05-labels-reset](./05-labels-reset.md)

## Goal

Harden pan/zoom for window resize, late base-map `mapSize` discovery, and middle-mouse edge cases per the planning lock.

## Build

| File | Action |
|------|--------|
| `frontend/app/hooks/useMapViewport.ts` | `readViewportSize`; seed size on mount; pan cancel on leave/blur; contextmenu hardening |
| `frontend/app/hooks/useMapViewport.test.ts` | create — `readViewportSize` unit test |
| `frontend/app/components/map/MapCanvas.tsx` | sync `mapSize` from cached/complete base image |
| `frontend/app/components/MapViewer.tsx` | left-button-only `handleMapClick` guard |

## Changes

**Resize:** `useLayoutEffect` seeds viewport size via `getBoundingClientRect` before `ResizeObserver` fires, so wheel/pick work on first paint.

**Late mapSize:** base map `<img>` ref callback calls `applyNaturalMapSize` when `node.complete` — handles cached images that skip `onLoad`. Viewport re-clamps on `mapSize` change without resetting zoom.

**Middle-click:**
- Pan cancels on viewport `mouseleave` and window `blur`
- `contextmenu` suppressed while panning or on middle button (`event.button === 1`)
- `handleMapClick` ignores non-left buttons

## Verify

- [x] `npm test -- useMapViewport` passes
- [x] `npm run build` passes

## Out of scope

- STAGING / manual QA (49.07)
- Mobile pinch
