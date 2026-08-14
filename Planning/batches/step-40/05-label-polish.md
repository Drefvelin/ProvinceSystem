# Step 40.05 — Label polish

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [04-frontend-layer](./04-frontend-layer.md)

## Goal

Improve label readability (ink + cream halo) and wire the zoom-hide contract as a stub until pan/zoom ships.

## Build

| File | Action |
|------|--------|
| [`frontend/app/lib/mapLabels.ts`](../../../frontend/app/lib/mapLabels.ts) | `LABEL_INK`, `LABEL_HALO`, stroke/weight constants; `LABEL_MAX_ZOOM`, `DEFAULT_MAP_ZOOM`, `shouldShowLabelsAtZoom` |
| [`frontend/app/lib/mapLabels.test.ts`](../../../frontend/app/lib/mapLabels.test.ts) | Zoom visibility tests |
| [`frontend/app/components/map/LabelLayer.tsx`](../../../frontend/app/components/map/LabelLayer.tsx) | Halo stroke, `visible` prop |
| [`frontend/app/components/map/MapCanvas.tsx`](../../../frontend/app/components/map/MapCanvas.tsx) | `mapZoom` prop → `shouldShowLabelsAtZoom` |
| [`frontend/app/components/MapViewer.tsx`](../../../frontend/app/components/MapViewer.tsx) | Pass `DEFAULT_MAP_ZOOM` (stub) |

## Styling (shipped)

| Token | Value |
|-------|-------|
| `LABEL_INK` | `#2a1f14` |
| `LABEL_HALO` | `#e8e4d9` (cream stroke) |
| `LABEL_STROKE_WIDTH` | `4` map px |
| `LABEL_FONT_WEIGHT` | `500` |
| `LABEL_FONT_SIZE` | `28` (from 40.03) |

SVG: `paintOrder="stroke"`, `strokeLinejoin="round"`, Fraunces.

## Min-size filters (from 40.03 — unchanged)

| Constant | Value |
|----------|-------|
| `MIN_PROVINCES` | 3 |
| `MIN_PIXEL_AREA` | 15000 |

## Zoom stub

| Constant | Value | Role |
|----------|-------|------|
| `DEFAULT_MAP_ZOOM` | `1` | Passed from `MapViewer` until pan/zoom exists |
| `LABEL_MAX_ZOOM` | `1.5` | Labels hidden when `mapZoom > 1.5` |

Replace `mapZoom={DEFAULT_MAP_ZOOM}` with live zoom state when pan/zoom lands.

## Verify

- [ ] `/map/main` nation mode: labels readable on busy terrain (cream halo)
- [x] `npm test` passes
- [x] `npm run build` passes
- [ ] Optional: temporarily set `mapZoom={2}` — labels hidden
- [ ] Hover / drill / modal / pick unchanged

## Out of scope

- Pan/zoom implementation
- Cross-nation collision
- Font size scaling with zoom

## Status

**Done** (40.05). Next batch: [06-docs-verify](./06-docs-verify.md).
