# Step 73.03 — Locked map context in editor

**Build:** ProvinceSystem frontend  
**Depends on:** [02-nav-and-entry](./02-nav-and-entry.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Editor always edits **one map** passed via query param. Remove map dropdown and in-editor map switching.

## Deliverables

### 1. Require `?map=`

[`frontend/app/map/editor/MapEditorPageClient.tsx`](../../../frontend/app/map/editor/MapEditorPageClient.tsx):

- Parse `map` from search params.
- If missing or invalid: `redirect('/map/main')` **or** show gate with copy: "Open the editor from the map page" + link to `/map/main`.
- Pass `mapId` as fixed prop to `MapTitleEditor`; do not allow client-side map changes.

### 2. `MapTitleEditor` header

[`frontend/app/components/map/editor/MapTitleEditor.tsx`](../../../frontend/app/components/map/editor/MapTitleEditor.tsx):

- Remove map `<select>` and `useAccessibleMaps` for map options.
- Show read-only label: `MAP_DISPLAY_NAMES[mapId]` or "Editing: Calavorn".
- Remove `editor.setMapId` from UI; drop `mapOptions` block.

### 3. `useEditorDraft`

[`frontend/app/hooks/useEditorDraft.ts`](../../../frontend/app/hooks/useEditorDraft.ts):

- Remove or noop `setMapId` export (or keep internal-only if tests need it).
- `mapId` state initialized from `initialMapId` only; no user-facing switch.
- Remove confirm-on-map-switch path (tier switch confirm remains).

### 4. `EditorSaveBar`

[`frontend/app/components/map/editor/EditorSaveBar.tsx`](../../../frontend/app/components/map/editor/EditorSaveBar.tsx):

- **Open map** link: viewer route for same `mapId` (`/map/main` or `/map/r3b1rth` for dev).

### 5. Optional route hardening

Consider `middleware` or page metadata disallowing `/map/editor` bookmark without map - redirect only on client is OK for v1.

## Files touched

| File | Change |
|------|--------|
| `MapEditorPageClient.tsx` | Required `map` param |
| `MapTitleEditor.tsx` | No dropdown |
| `useEditorDraft.ts` | Fixed mapId |
| `EditorSaveBar.tsx` | Viewer link |

## Done when

- No map dropdown in editor UI.
- `/map/editor?map=main` and `?map=dev` work; bare `/map/editor` does not silently edit wrong map.
- Tier tabs and save/regen unchanged.

## Status

Done.
