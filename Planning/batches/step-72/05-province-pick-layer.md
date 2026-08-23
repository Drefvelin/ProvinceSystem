# Step 72.05 — Province pick layer and live paint

**Build:** ProvinceSystem frontend  
**Depends on:** [04-editor-route-shell](./04-editor-route-shell.md) · [step-49/04-pick-hover](../step-49/04-pick-hover.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Replace placeholder map panel with pan/zoom canvas: hidden pick layer for province id resolution and **visible paint layers** that update on click without server regen.

## Deliverables

### 1. `MapEditorCanvas`

[`frontend/app/components/map/editor/MapEditorCanvas.tsx`](../../../frontend/app/components/map/editor/MapEditorCanvas.tsx)

Reuses:

- `MapViewport`, `useMapViewport`, `useMapCoords` / `screenToMap`
- `MAP_BOUNDS`, map size from base image load

Layers:

1. `MapAuthImage` base terrain.
2. **Selection canvas** (`<canvas>`) - child/unassigned at `EDITOR_SELECTION_OPACITY`.
3. **Active canvas** (`<canvas>`) - active title + click selection at `EDITOR_ACTIVE_OPACITY`.
4. Hidden pick canvas - province or tier pick image.

### 2. `buildProvinceIndex.ts`

[`frontend/app/lib/map/editor/buildProvinceIndex.ts`](../../../frontend/app/lib/map/editor/buildProvinceIndex.ts)

From `GET /editor/provinces` + optional province pick image load:

- `rgbToProvinceId: Record<string, number>`
- `provinceToRgb: Record<number, string>`
- `provinceMap: Int32Array` or sparse lookup for paint (width × height) - build from pick image `getImageData` once on load (mirror `county_editor.build_province_map`).

### 3. `paintTitleLayers.ts`

[`frontend/app/lib/map/editor/paintTitleLayers.ts`](../../../frontend/app/lib/map/editor/paintTitleLayers.ts)

Functions:

- `paintSelectionLayer(ctx, provinceMap, assignment, colours, opacity)`
- `paintActiveLayer(ctx, provinceMap, activeMembers, activeRgb, selectionIds, highlightRgb, opacity)`
- `fillProvincePixels(ctx, provinceMap, provinceIds, rgb)`

Called on: load, tier change, selection change, colour change.

Use `requestAnimationFrame` debounce if needed for large maps.

### 4. `useEditorPick`

[`frontend/app/hooks/useEditorPick.ts`](../../../frontend/app/hooks/useEditorPick.ts)

- Load pick image URL: county tier → province pick (`mapdata` mode that matches raw province colours, or dedicated province pick endpoint if needed).
- On click: `screenToMap` → `getImageData` → province id.
- Returns `onClick`, `onMouseMove` (optional hover tooltip with province id).

### 5. Pick map source (county tier)

**Locked:** Use full-map pick image where each province pixel = province RGB from `provinces.txt`.

Options (pick one in build):

- A) `GET /{map}/mapdata/county` with `apply_overrides=False` pick variant if exists.
- B) New `GET /{map}/editor/pick/provinces` static PNG from `input/{map}/provinces.png` (staff only).

Document choice in implementation; 72.01 prefers raw province RGB alignment.

### 6. Wire into shell

`MapTitleEditor` passes draft + selection state to `MapEditorCanvas`.

## Performance notes

- Build `provinceMap` once per map load (can be 8k×8k - use typed array + single pass over pick image).
- Paint only visible viewport region if needed (defer: full repaint v1 OK for staff desktop).

## Tests

- `buildProvinceIndex` fixture small 4×4 pick image.
- `paintTitleLayers` sets expected pixel colour for one province id.

## Done when

- County tier tab: click toggles province selection; purple highlight on selected provinces; assigned counties show at 40% on selection layer.
- Pan/zoom works; pick coords accurate at zoom 2x.
- No network call on click (only initial pick image + provinces list).

## Status

Done.
