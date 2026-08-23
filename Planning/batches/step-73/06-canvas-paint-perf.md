# Step 73.06 — Canvas paint layer performance

**Build:** ProvinceSystem frontend  
**Depends on:** [05-province-index-perf](./05-province-index-perf.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Make live paint updates feel instant after index load; avoid full-map repaints on every draft keystroke or province toggle.

## Current cost

[`MapEditorCanvas.tsx`](../../../frontend/app/components/map/editor/MapEditorCanvas.tsx) `useEffect` on `[draft, selectedId, …]`:

- [`paintSelectionLayer`](../../../frontend/app/lib/map/editor/paintTitleLayers.ts) / `paintActiveLayer` iterate **entire** `provinceMap` (all pixels).
- Runs on every draft change (rename, colour tweak, province toggle).

## Deliverables

### 1. Incremental paint

Extend [`paintTitleLayers.ts`](../../../frontend/app/lib/map/editor/paintTitleLayers.ts):

- `paintProvincesSubset(provinceMap, provinceIds, rgb)` - only touch pixels for given province ids.
- On county toggle: repaint affected province ids only (added/removed + neighbours if needed).
- On rename/colour change: repaint counties whose colour changed (member provinces).

Full repaint still on tier switch or map load.

### 2. Throttle / rAF

- Debounce colour picker drag: max one paint per animation frame.
- Optional: separate "structure dirty" (membership) vs "colour dirty" paths.

### 3. Canvas size discipline

- Do not resize canvases every effect if dimensions unchanged (already sets width/height when index loads; avoid redundant clears).

### 4. Child tier modes

- `paintChildSelectionLayer` / `paintParentActiveLayer`: apply same subset strategy using resolved child province sets from `titleLayers`.

### 5. Tests

- Vitest on subset paint: given small synthetic `provinceMap`, only target pixels change.
- Manual: rapid province clicks feel responsive after 73.05 index build.

## Files touched

| File | Change |
|------|--------|
| `paintTitleLayers.ts` | Subset paint helpers |
| `MapEditorCanvas.tsx` | Incremental effect deps |
| `countyDraftActions` / pick handlers | Pass changed province ids upstream (optional) |

## Done when

- Click-to-add/remove province updates overlay in < 100ms perceived (after index ready).
- Typing in name field does not trigger full-map paint (only colour changes repaint colour).
- No visual regression vs full paint on tier load.

## Status

**Done.** Cached ImageData buffers, province pixel index, snapshot diff (skips name-only edits), incremental subset paint, and rAF-coalesced updates in `MapEditorCanvas`.
