# Step 73.04 — Editor layout and overflow

**Build:** ProvinceSystem frontend  
**Depends on:** [03-locked-map-editor](./03-locked-map-editor.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Fix editor layout so the map panel and controls stay on screen at desktop widths; eliminate horizontal page scroll caused by oversized map inner dimensions.

## Problem

- `MapTitleEditor` flex row: canvas column uses `flex-1` **without** `min-w-0`.
- `MapViewport` inner wrapper uses literal `width/height` in pixels (up to 6400) before CSS transform scales down.
- `MapPageLayout` already uses `min-w-0 flex-1`; editor shell should match.

## Deliverables

### 1. Flex containment

[`MapTitleEditor.tsx`](../../../frontend/app/components/map/editor/MapTitleEditor.tsx):

```text
Outer: max-w-[90rem] mx-auto (keep)
Row: flex flex-col lg:flex-row lg:items-start min-w-0
Sidebar: shrink-0 lg:w-80 (keep)
Canvas column: min-w-0 flex-1 min-h-[28rem]
```

Optional: `overflow-x-hidden` on page root wrapper (editor page only).

### 2. Map panel wrapper

[`MapEditorCanvas.tsx`](../../../frontend/app/components/map/editor/MapEditorCanvas.tsx):

- Ensure root panel `max-w-full overflow-hidden` (already present; verify parent chain).
- Confirm `MapViewport` outer `w-full` receives bounded width from flex parent.

### 3. Initial map size

- Avoid flashing 6400px layout: consider initializing `mapSize` from a conservative default or `aspect-ratio` only until `onLoad` (align with `MapCanvas` if it has a better pattern).

### 4. Manual QA sizes

| Viewport | Check |
|----------|-------|
| 1280×800 | No horizontal scrollbar on `body` |
| 1920×1080 | Sidebar + map visible; tier tabs clickable |
| Mobile | Stacked layout; map pan/zoom still usable |

## Files touched

| File | Change |
|------|--------|
| `MapTitleEditor.tsx` | `min-w-0`, overflow |
| `MapEditorCanvas.tsx` | Panel / viewport containment |
| `map/editor/page.tsx` | Optional page-level overflow |

## Done when

- Editor usable at 1280px without content disappearing off the right edge.
- No regression on `/map/main` viewer layout.

## Status

Done.
