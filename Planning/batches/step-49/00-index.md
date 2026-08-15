# Step 49 — Pan and zoom

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [step-37](../step-37/00-index.md) (map shell), [step-40](../step-40/00-index.md) (labels + zoom-hide stub), [step-47](../step-47/00-index.md) (multi-mode labels), [step-48](../step-48/00-index.md) (label neighbors)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 4d

## Goal

Add interactive **pan and zoom** to `/map/{id}`: scroll wheel to zoom toward the cursor, middle-mouse drag to pan with grab/grabbing cursor, and clamped bounds so the user cannot pan past map edges at any zoom level.

## Problem statement

| Issue | Root cause |
|-------|------------|
| Map is fixed fit-to-width | [`MapCanvas.tsx`](../../../frontend/app/components/map/MapCanvas.tsx) stacks layers in a panel with `w-full`; no viewport transform |
| Zoom stub only affects label visibility | [`MapViewer.tsx`](../../../frontend/app/components/MapViewer.tsx) passes `mapZoom={DEFAULT_MAP_ZOOM}` (`1`) — not live scale |
| Hover/pick assume no transform | [`useMapCoords.ts`](../../../frontend/app/hooks/useMapCoords.ts) maps screen position to map pixels with uniform rect scaling only |

Users need desktop pan/zoom without breaking nation hover, click, drill, or province pick.

## Locked rules (summary)

See [01-planning-lock](./01-planning-lock.md). Highlights:

| Piece | Choice |
|-------|--------|
| Initial state | `scale = 1`, `translate = (0, 0)` — same visual as today |
| Wheel | Zoom in/out toward cursor; `preventDefault` over viewport |
| Middle mouse | Pan while held; `grab` / `grabbing` cursor |
| Pan limits | Clamp translate so map always covers viewport |
| Zoom limits | `MAP_ZOOM_MIN = 1`, `MAP_ZOOM_MAX = 3` |
| Labels | Hide when `scale > LABEL_MAX_ZOOM` (`1.5`); font size constant in map pixels |
| Transform | Single wrapper around base, overlays, labels, pick canvas |
| Reset | Viewport resets on `mapId` / `mapType` change |

## Batches

1. **[01-planning-lock](./01-planning-lock.md)** — Interaction model, math, constants, scope
2. **[02-viewport-math](./02-viewport-math.md)** — `mapViewportMath.ts` + `useMapViewport` hook
3. **[03-map-viewport](./03-map-viewport.md)** — `MapViewport` wrapper + `MapCanvas` integration
4. **[04-pick-hover](./04-pick-hover.md)** — `screenToMap` / `getMapCoords` pipeline
5. **[05-labels-reset](./05-labels-reset.md)** — Live zoom → labels; viewport reset on mode change
6. **[06-edge-cases](./06-edge-cases.md)** — Resize, `mapSize` load, middle-click suppression
7. **[07-docs-verify](./07-docs-verify.md)** — STAGING, checklist, manual QA on `main` + `dev`

## Status

**49.01–49.07 done.** Step 49 pan/zoom complete.

## Next

[step-41 staff map access](../step-41/00-index.md) · [step-42 capitals](../step-42/00-index.md).
