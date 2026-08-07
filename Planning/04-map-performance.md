# 04 — Map performance and mobile

Making the map **feel fast and responsive** is a top priority. Generators on `dev` are already much faster; the remaining pain is mostly **runtime in the browser** (and a small hover-card wiring bug).

## Problems

1. **Full-map region PNGs** — [`regiongen.py`](../backend/src/scripts/mapgen/regiongen.py) still allocates `Image.new("RGBA", (width, height), …)` per region (and hover / nested variants). Files are huge; the browser stacks many transparent full canvases.
2. **Hover lookup** — [`useRegionHover.ts`](../frontend/app/hooks/useRegionHover.ts) uses `ctx.getImageData(x, y, 1, 1)` on mousemove (forces canvas sync).
3. **Province modes** — [`useProvinceHover.ts`](../frontend/app/hooks/useProvinceHover.ts) may `fetch` meta on move for terrain/fertility/prosperity (cached later, still chatty at first).
4. **Hover card data** — realm size / subjects not passed into card state (display bug, not generator bug).
5. **Layout** — [`MapViewer.tsx`](../frontend/app/components/MapViewer.tsx) is desktop `flex-row`; weak on small screens.

## Approach: cropped overlays + offsets

### Generator change

When painting a region:

1. Track all painted pixels (already available via province pixel lists).
2. Compute bounding box: `minX, minY, maxX, maxY` (optionally pad 1–2 px for borders).
3. Crop the buffer to that box and save the small PNG.
4. Persist placement metadata next to the asset.

Metadata can live in:

- fields on each region in `defines/{map}/{mode}.json`, or
- a sidecar `defines/{map}/regions_{mode}_meta.json`, or
- filenames plus a single `index.json` under `output/{map}/regions/{mode}/`.

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

Same for `_hover` and `_nested` variants (bbox may differ slightly; store each or share if identical).

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

`mapW` / `mapH` come from the loaded map image (already known when the canvas is sized). Update [`MapEngineContext`](../frontend/app/core/MapEngineContext.tsx) so `mapObjects` carry `x,y,w,h` (default `0,0,full,full` for backward compatibility during rollout).

### API

[`file_routes.py`](../backend/src/api/file_routes.py) can keep serving files by name. Either:

- extend the data JSON the frontend already loads for the mode, or
- add `GET /{map}/regions/{mode}/index` returning the bbox map.

Prefer **folding bbox into existing mode JSON** during compile/regen so the client needs one fewer round trip.

## Hover / lookup performance

Keep **one** full-resolution lookup surface (the existing mapdata canvas is fine).

Improvements, in order:

1. **Restore card fields** — pass through size/subjects (quick win).
2. **Throttle** mousemove handling with `requestAnimationFrame` (one read per frame).
3. **Skip work** if pixel RGB unchanged from last event.
4. **RGB → id map** — build `Record<rgb, id>` once when `regionData` loads instead of `Object.keys().find` every move.
5. **Optional:** after drawing mapdata, cache `ImageData` / `Uint32Array` once and index `y * width + x` instead of `getImageData` per move.
6. **Province modes:** resolve province id from a local provinces color map when feasible; otherwise debounce meta fetches (50–100 ms).

Do not require WebGL for v1; cropped PNGs + rAF + RGB map should be enough.

## Drill-down and nesting

Cropped overlays must still layer correctly:

- Independent nations: visible cropped bases.
- Drill-down: hide parent base, show `_nested` + subject crops.
- Hover: only the active visible layer’s `_hover` crop (same bbox rules).

Z-index / paint order stays as today; only dimensions and position change.

## Migration / regen

- Full regen required after generator change (old full-size PNGs obsolete).
- Queued regen must write bbox metadata for touched regions only and leave others consistent.
- Document in [06-local-development.md](./06-local-development.md): after pull, run fullregen once.

## Mobile layout

Minimum bar for Phase 1:

| Desktop | Mobile |
|---------|--------|
| Map + right sidebar | Map full width; panels below or in a drawer |
| Tall hero banner | Shorter hero or collapse into header |
| Hover tooltips | Tap to select region; show same info card |

Avoid horizontal squeeze of `w-[18%]` sidebars. Touch: `click` / tap already drives drill-down; ensure hit targets are large enough.

## Out of scope (for later)

- Rewriting mapgen in Rust/C
- Vector/WebGL map engine
- Perfect pixel-perfect retina atlases

## Acceptance checks

- [ ] Nation hover card shows realm size and subject list when data exists
- [ ] Region PNG file sizes drop dramatically vs full canvas
- [ ] Visible overlay count unchanged but memory/network much lower
- [ ] Panning hover feels smooth on a mid laptop
- [ ] Phone: can open map, read a nation card, change map mode
