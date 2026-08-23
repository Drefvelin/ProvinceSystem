# Step 72.04 — Editor route and shell

**Build:** ProvinceSystem frontend  
**Depends on:** [01-planning-lock](./01-planning-lock.md) · [step-41/04-frontend-gate](../step-41/04-frontend-gate.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Staff-gated `/map/editor` page with map selector, tier tabs, and sidebar + map split layout. No paint logic yet (placeholder map panel).

## Deliverables

### 1. Route

[`frontend/app/map/editor/page.tsx`](../../../frontend/app/map/editor/page.tsx)

- `"use client"` page component.
- Loads character session token (same as map viewer).
- Checks staff access via `fetchAccessibleMaps` or dedicated probe.
- Shows `MapAccessGate` on login/permission failure.

### 2. `MapTitleEditor` shell

[`frontend/app/components/map/editor/MapTitleEditor.tsx`](../../../frontend/app/components/map/editor/MapTitleEditor.tsx)

Layout:

```text
┌─────────────────────────────────────────────────────────┐
│ Map editor    [Map: main ▼]    County | Duchy | Kingdom | Empire │
├──────────────────┬──────────────────────────────────────┤
│ TitleSidebar     │ MapEditorCanvas (placeholder)         │
│ (list + form)    │ "Map loads in 72.05"                  │
└──────────────────┴──────────────────────────────────────┘
```

### 3. `TitleSidebar` stub

- Search/filter titles (by name).
- List entries: name + colour chip.
- **New** / **Delete** buttons (wired in tier batches).
- Fields: Name input, `TitleRgbPicker` placeholder.

### 4. `useEditorDraft` hook

[`frontend/app/hooks/useEditorDraft.ts`](../../../frontend/app/hooks/useEditorDraft.ts)

- State: `mapId`, `tier`, `draft`, `serverSnapshot`, `selectedId`, `dirty`.
- `loadTier(mapId, tier)` → GET `/{map}/data/{tier}`.
- `setDraft`, `markDirty`, `resetToServer`.

### 5. Nav link

[`SiteHeader`](../../../frontend/app/components/shell/SiteHeader.tsx):

- Show **Map editor** link when `accessibleMaps` includes staff maps or staff flag detected (same condition as dev map link pattern).

### 6. API client

Extend [`frontend/lib/map/api.ts`](../../../frontend/lib/map/api.ts):

- `postEditorTitles(mapId, tier, body, token)`
- `postEditorRegen(mapId, regenType, token)`
- `fetchEditorProvinces(mapId, token)`

## Files touched

| File | Change |
|------|--------|
| `frontend/app/map/editor/page.tsx` | New |
| `frontend/app/components/map/editor/MapTitleEditor.tsx` | New |
| `frontend/app/components/map/editor/TitleSidebar.tsx` | New |
| `frontend/app/hooks/useEditorDraft.ts` | New |
| `frontend/lib/map/api.ts` | Editor endpoints |
| `frontend/app/components/shell/SiteHeader.tsx` | Nav link |

## Done when

- Staff opens `/map/editor` → shell with map dropdown and tier tabs.
- Non-staff → gate screen.
- Switching tier loads JSON into draft (network tab shows GET data/county etc.).
- Vitest for `useEditorDraft` load/reset optional.

## Status

**Done** (code + tests).

