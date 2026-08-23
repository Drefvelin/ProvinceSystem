# Step 72.09 — Save, upload, and regen

> **Superseded by [step 74](../step-74/00-index.md) (2026-08-23):** editor **Download ZIP** replaces Save to server; **Reset changes** replaces Regenerate in UI; no Open map link. Operator merges JSON into `defines/` and runs mapgen on host. Step 72 history retained below.

**Build:** ProvinceSystem frontend + backend integration  
**Depends on:** [02-staff-write-api](./02-staff-write-api.md) · [08-kingdom-empire-mode](./08-kingdom-empire-mode.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Persist draft to server, trigger regen, and link to map viewer for preview.

## Deliverables

### 1. Save bar

[`EditorSaveBar.tsx`](../../../frontend/app/components/map/editor/EditorSaveBar.tsx)

Buttons:

| Button | Action |
|--------|--------|
| **Save to server** | `POST /{map}/editor/titles/{tier}` with draft body |
| **Regenerate** | `POST /{map}/editor/regen/fullregen:{tier}` (enabled after successful save) |
| **Open map** | Link `/map/main` or `/map/{mapId}` new tab |

States: idle, saving, save error, regen running, regen done.

### 2. Client validation before save

Mirror server rules from 72.02:

- Non-empty name.
- Valid rgb.
- No duplicate members.
- Show inline errors in sidebar (no em dash in messages).

### 3. Unsaved changes guard

- `beforeunload` when dirty.
- Tier/map switch modal: "Discard unsaved changes?"

### 4. Regen feedback

After regen success:

- Toast: "Map updated. Open viewer to preview."
- Optional: bust cache on map assets (`fetchMapBlobUrl` revoke).

### 5. Error handling

| Error | UI |
|-------|-----|
| 403 | Redirect to gate |
| 400 validation | Show `detail` under save bar |
| Regen timeout | "Regen still running" or retry (document server sync behavior) |

### 6. Incremental save scope

**Locked v1:** Save replaces **entire tier file** (full JSON). No per-title PATCH.

## Done when

- Edit county name → Save → `defines/main/county.json` on disk updates (verify via GET).
- Regenerate → `output/main/regions/county/` updates; viewer shows new colour.
- Dirty flag clears after successful save.

## Status

Done.
