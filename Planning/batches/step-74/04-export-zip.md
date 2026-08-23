# Step 74.04 — Download ZIP (no Save to server)

**Build:** ProvinceSystem frontend  
**Depends on:** [03-loading-progress](./03-loading-progress.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Replace **Save to server** with **Download ZIP** containing `county.json`, `duchy.json`, `kingdom.json`, and `empire.json`. Filename: `{mapId}-titles-{YYYY-MM-DD}.zip`.

## Deliverables

### Per-tier draft cache

[`useEditorDraft.ts`](../../../frontend/app/hooks/useEditorDraft.ts): `tierDrafts` / `tierSnapshots`, `anyTierDirty`, `getTierDraftsForExport()`.

### Export utilities

- [`validateAllTiersForExport.ts`](../../../frontend/app/lib/map/editor/validateAllTiersForExport.ts) - cross-tier validation; empty `duchy` / `kingdom` / `empire` allowed
- [`buildEditorTitlesZip.ts`](../../../frontend/app/lib/map/editor/buildEditorTitlesZip.ts) - `fflate` ZIP via `serializeTitleDraftForSave`
- [`downloadBlob.ts`](../../../frontend/app/lib/downloadBlob.ts)

### Hooks + UI

- [`useEditorExport.ts`](../../../frontend/app/hooks/useEditorExport.ts) - validate, build ZIP, browser download
- [`useEditorRegen.ts`](../../../frontend/app/hooks/useEditorRegen.ts) - regen only (unchanged until 74.05)
- [`EditorSaveBar.tsx`](../../../frontend/app/components/map/editor/EditorSaveBar.tsx) - **Download ZIP** replaces Save to server; Regenerate + Open map remain until 74.05
- [`MapTitleEditor.tsx`](../../../frontend/app/components/map/editor/MapTitleEditor.tsx) - wires export hook; `anyTierDirty` for unsaved badge

Removed: [`useEditorSave.ts`](../../../frontend/app/hooks/useEditorSave.ts) and editor `POST /editor/titles` path.

## Verification

```bash
cd ProvinceSystem/frontend
npm test -- app/lib/map/editor/validateAllTiersForExport.test.ts app/lib/map/editor/buildEditorTitlesZip.test.ts
```

Manual: edit county, switch tabs, **Download ZIP** - zip contains four JSON files; county edits included; no Save to server button.

## Done when

- Download ZIP in editor; no Save to server UI or save POST from editor
- Cross-tab edits appear in export
- Tests pass; docs closed

## Status

**Done.**
