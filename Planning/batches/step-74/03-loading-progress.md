# Step 74.03 — Loading progress UI

**Build:** ProvinceSystem frontend  
**Depends on:** [01-planning-lock](./01-planning-lock.md) · [02-precomputed-grid-only](./02-precomputed-grid-only.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Replace generic "Loading titles..." / "Loading map pick data..." with a unified staged progress bar: `{percent}% - {label}` over enabled stages only. County mode skips child-pick weight so progress reaches 100% without the child tier stage.

## Stage model

| Stage ID | Weight | Label |
|----------|--------|-------|
| `titles` | 15 | Loading title data... |
| `provinceCatalog` | 10 | Loading province catalog... |
| `provinceGrid` | 35 | Loading province index... |
| `mapImage` | 25 | Loading map image... |
| `childPick` | 15 | Loading pick layers... |

Percent = `completedWeight / enabledTotalWeight * 100` (renormalized). Active label = current in-progress stage. Overlay hidden when all enabled stages complete.

## Deliverables

### Progress utilities

[`editorLoadProgress.ts`](../../../frontend/app/lib/map/editor/editorLoadProgress.ts): `getEnabledStages`, `computeEditorLoadProgress`, weight/label maps.

[`editorLoadProgress.test.ts`](../../../frontend/app/lib/map/editor/editorLoadProgress.test.ts): county 100%, child tier weights, partial percent, active label.

### Hook + UI

[`useEditorLoadProgress.ts`](../../../frontend/app/hooks/useEditorLoadProgress.ts): `markActive`, `markComplete`, `resetStages`.

[`EditorLoadProgress.tsx`](../../../frontend/app/components/map/editor/EditorLoadProgress.tsx): progress bar + `{percent}% - {label}`.

### Wiring

[`useEditorProvinceIndex.ts`](../../../frontend/app/hooks/useEditorProvinceIndex.ts): optional `onCatalogLoaded` / `onIndexLoaded` after catalog response and grid build.

[`MapTitleEditor.tsx`](../../../frontend/app/components/map/editor/MapTitleEditor.tsx): single full-panel overlay; tier switch resets `titles` + `childPick`; always mounts canvas for map image load.

[`MapEditorCanvas.tsx`](../../../frontend/app/components/map/editor/MapEditorCanvas.tsx): `onMapImageLoaded` from natural size sync; `suppressLoadingOverlay` when parent shows unified progress.

## Verification

```bash
cd ProvinceSystem/frontend && npm test -- app/lib/map/editor/editorLoadProgress.test.ts
```

Manual: open `/map/editor?map=main` - progressing % and labels; county tab switch briefly re-shows title stage; no generic loading strings in sidebar.

## Done when

- Unified progress bar during initial load and tier title reload
- Stage weights match 74.01 lock
- Tests pass; docs closed

## Status

**Done.**
