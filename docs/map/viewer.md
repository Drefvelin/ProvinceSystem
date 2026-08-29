# Map viewer (performance and UX)

Making the map **feel fast and responsive** is a top priority. Product goals: [overview.md](./overview.md).

## Problems addressed

1. **Full-map region PNGs** - [`regiongen.py`](../../backend/src/scripts/mapgen/regiongen.py) historically allocated full-canvas images per region. Files were huge; the browser stacked many transparent full canvases.
2. **Hover lookup** - [`useRegionHover.ts`](../../frontend/app/hooks/useRegionHover.ts) uses `ctx.getImageData(x, y, 1, 1)` on mousemove.
3. **Province modes** - [`useProvinceHover.ts`](../../frontend/app/hooks/useProvinceHover.ts) may `fetch` meta on move for terrain/fertility/prosperity (cached later).
4. **Layout** - [`MapViewer.tsx`](../../frontend/app/components/MapViewer.tsx) was desktop `flex-row`; improved for small screens.

## Cropped overlays + offsets

### Generator change

When painting a region:

1. Track all painted pixels.
2. Compute bounding box: `minX, minY, maxX, maxY` (optionally pad 1-2 px for borders).
3. Crop the buffer to that box and save the small PNG.
4. Persist placement metadata next to the asset.

Preferred shape per overlay:

```json
{
  "path": "192_159_77",
  "x": 1204,
  "y": 880,
  "w": 312,
  "h": 268
}
```

Same for `_hover` and `_nested` variants.

### Frontend change

Position with percentages so CSS scaling matches the base map:

```tsx
<img
  src={`${API}/${mapId}/regions/${mapType}/${path}`}
  alt=""
  className="absolute pointer-events-none"
  style={{
    left: `${(x / mapW) * 100}%`,
    top: `${(y / mapH) * 100}%`,
    width: `${(w / mapW) * 100}%`,
    height: `${(h / mapH) * 100}%`,
  }}
/>
```

`mapW` / `mapH` come from the loaded map image. `MapEngineContext` carries `x,y,w,h` on `mapObjects` (default `0,0,full,full` for backward compatibility).

### API

Prefer **folding bbox into existing mode JSON** during compile/regen so the client needs one fewer round trip. [`file_routes.py`](../../backend/src/api/file_routes.py) serves files by name.

## Pan and zoom

Desktop pan/zoom on `/map/{id}`:

- Wheel zoom toward cursor
- Middle-mouse pan
- Clamped bounds

## Hover / lookup performance

Keep **one** full-resolution lookup surface (the existing mapdata canvas).

Live map assets (pick PNGs, region overlays, banners, ZOC, and defines JSON such as `nation.json`) are served with `Cache-Control: no-store` so regen updates reach browsers without heuristic image cache. If a reverse proxy uses `proxy_cache`, it must honour origin `Cache-Control`. After deploy, users who already cached an old PNG may need one hard reload.

Improvements:

1. **Restore card fields** - pass through size/subjects.
2. **Throttle** mousemove handling with `requestAnimationFrame`.
3. **Skip work** if pixel RGB unchanged from last event.
4. **RGB → id map** - build `Record<rgb, id>` once when `regionData` loads.
5. **Optional:** cache `ImageData` / `Uint32Array` once and index `y * width + x`.
6. **Province modes:** resolve province id from a local provinces color map when feasible; otherwise debounce meta fetches (50-100 ms).

## Drill-down and nesting

Cropped overlays must still layer correctly:

- Independent nations: visible cropped bases.
- Drill-down: hide parent base, show `_nested` + subject crops.
- Hover: only the active visible layer's `_hover` crop.

## Migration / regen

- Full regen required after generator change (old full-size PNGs obsolete).
- Queued regen must write bbox metadata for touched regions only.
- After pull, run fullregen once ([ops/local-dev.md](../ops/local-dev.md)).

## Mobile layout

| Desktop | Mobile |
|---------|--------|
| Map + right sidebar | Map full width; panels below or in a drawer |
| Tall hero banner | Shorter hero or collapse into header |
| Hover tooltips | Tap to select region; show same info card |

Avoid horizontal squeeze of narrow sidebars. Touch: `click` / tap drives drill-down; ensure hit targets are large enough.

## Out of scope (for later)

- Rewriting mapgen in Rust/C
- Vector/WebGL map engine
- Perfect pixel-perfect retina atlases
