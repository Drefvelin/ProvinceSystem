# Step 73.02 — Nav cleanup and viewer edit entry

**Build:** ProvinceSystem frontend  
**Depends on:** [01-planning-lock](./01-planning-lock.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Remove global nav clutter; add **Edit titles** on the map viewer for staff (and UI dev) that deep-links to the editor for the current map.

## Deliverables

### 1. `SiteHeader` cleanup

[`frontend/app/components/shell/SiteHeader.tsx`](../../../frontend/app/components/shell/SiteHeader.tsx)

- Remove **Map editor** link (`showEditor` block).
- Remove `staffNavLinks` rendering (Adavaar / dev map link).
- Remove `useAccessibleMaps` from header if no longer needed (header returns to static links only).
- Keep `staticLinks` as today: Home, Map (`/map/main`), Skins, Drinks, Character.

### 2. `canEditMap` helper

New hook or lib helper, e.g. [`frontend/app/hooks/useCanEditMap.ts`](../../../frontend/app/hooks/useCanEditMap.ts) or [`frontend/lib/map/editorAccess.ts`](../../../frontend/lib/map/editorAccess.ts):

| Input | Output |
|-------|--------|
| `mapId`, `sessionToken` | `loading`, `canEdit`, `error` |

Logic:

- UI dev (`isCharacterUiDev()`): `canEdit = true` for `main` and `dev`.
- Else: probe `GET /{mapId}/editor/provinces` with Bearer; `200` → true, `403` → false.
- Cache result per `(mapId, token)` for session; refresh on storage event.

Avoid calling `useAccessibleMaps` on every page for nav.

### 3. Viewer **Edit titles** button

[`frontend/app/components/MapViewer.tsx`](../../../frontend/app/components/MapViewer.tsx) and/or [`MapPageLayout.tsx`](../../../frontend/app/components/map/MapPageLayout.tsx):

- When `canEdit` for current `mapId`, show link/button **Edit titles**.
- `href`: `/map/editor?map=${mapId}` (use `encodeURIComponent`).
- Style: secondary button matching shell (not a nav link).
- Suggested placement: header row beside map title, or top of desktop side panel above map mode.

Do **not** add edit entry to global nav.

### 4. Regression

- Anonymous `/map/main`: no edit button.
- Staff `/map/main`: edit button → editor with `map=main`.
- Staff `/map/r3b1rth` (`mapId=dev`): edit button → `map=dev`.
- UI dev without login: edit button visible; editor loads with dev bypass.

## Files touched

| File | Change |
|------|--------|
| `SiteHeader.tsx` | Remove staff + editor links |
| `MapViewer.tsx` / `MapPageLayout.tsx` | Edit titles CTA |
| `useCanEditMap.ts` or `editorAccess.ts` | Staff probe helper |
| `useAccessibleMaps.ts` | Only if still needed elsewhere |

## Done when

- Header nav matches static five links (+ TFMC brand).
- Staff sees Edit titles on map pages they can write; link opens correct `?map=`.
- Vitest for `canEditMap` probe mapping (mock fetch) if helper is non-trivial.

## Status

Done.
