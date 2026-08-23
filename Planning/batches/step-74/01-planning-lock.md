# Step 74.01 — Planning lock

**Plan + docs only**  
**Depends on:** [00-index](./00-index.md) · [step-72/09-save-upload-regen](../step-72/09-save-upload-regen.md) · [step-73/01-planning-lock](../step-73/01-planning-lock.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Lock the **offline export** editor model before code batches 74.02–74.07. Supersedes step 72 save-to-server + editor regen UI (not step 73 entry/nav/perf).

## Locked — export and toolbar

| Before (72/73) | After (74) |
|----------------|------------|
| **Save to server** → `POST /editor/titles/{tier}` | **Download ZIP** (four tier JSON files) |
| **Regenerate** → `POST /editor/regen/...` | **Reset changes** → revert to last loaded snapshot (all four tiers) |
| **Open map** link to viewer | **Removed** (map already in editor) |
| Preview via regen + new tab | Live canvas paint only; public map updates after operator mapgen |

ZIP filename pattern (implementation detail): e.g. `{mapId}-titles-{date}.zip`.

Validation before export uses same rules as save today ([`validateEditorDraft`](../../../frontend/app/lib/map/editor/validateEditorDraft.ts)).

## Locked — province grid

| Piece | Choice |
|-------|--------|
| Artifact | `defines/{map}/province_id_grid.bin.gz` (step 54 format) |
| Editor fetch | `GET /{map}/editor/province-index` reads committed file only |
| Missing file | **404** with message to run admin script (no on-demand numpy rebuild) |
| Image fallback | **Removed** from editor (73.05 fallback retired in 74.02) |
| When to rebuild | Only when `provinces.png` or `provinces.txt` change (not on title edits) |
| Admin script | `python -m scripts.tools.build_province_id_grid --map main` from `ProvinceSystem/backend` |
| Client reverse index | One-time `buildProvincePixelIndex` after grid decode unless profiling warrants server-side artifact (defer) |

Copy grid to SimpleFactions `Input/province_id_grid.bin.gz` only when provinces change ([step-54](../step-54/03-sf-province-grid.md)).

## Locked — loading progress

Staged loader with approximate weights and user-visible labels:

| Stage | Weight (example) | Label |
|-------|------------------|-------|
| Title JSON | 15% | Loading title data… |
| Province catalog | 10% | Loading province catalog… |
| Province grid | 35% | Loading province index… |
| Base map image | 25% | Loading map image… |
| Child pick / layers (duchy+) | 15% | Loading pick layers… |

Display: single progress bar + `"{percent}% - {label}"`. Stage-based % is sufficient (no byte-level streaming required for v1).

## Locked — auth

| Direction | Choice |
|-----------|--------|
| Read | Staff GET: titles data, `editor/provinces`, `editor/pick/provinces`, `editor/province-index`, map image. Gate + UI dev pair unchanged (step 73). |
| Write (editor UI) | **No** Save to server or Regenerate in product path after 74.04/74.06 |
| Write (API) | Keep `POST /editor/titles` and `POST /editor/regen` **live but undocumented** for one release (operator curl escape hatch). Remove from editor client. |

## Locked — operator workflow

```text
1. Lore staff: Edit titles in browser → Download ZIP
2. Operator: Merge JSON into defines/{map}/
3. Operator: Run mapgen / fullregen on host (not in browser)
4. Deploy viewer output; copy province_id_grid to SF only if provinces changed
```

Title JSON does **not** go directly to the SF plugin. SF consumes `province_id_grid.bin.gz` for in-game province lookup. Website map layers come from PS `defines/` + mapgen.

## Deferred (not locked here)

- **Import ZIP** — optional in 74.04 or follow-up batch
- **Precomputed reverse pixel index file** — only if client pass after grid fetch is too slow

## Deliverables

1. This file (lock).  
2. [00-index](./00-index.md) locked UX table matches this doc.  
3. Amend [17-map-title-editor.md](../../17-map-title-editor.md) with offline export section; note save/regen UI superseded.  
4. Amend [step-72/09-save-upload-regen.md](../step-72/09-save-upload-regen.md) with superseded-by-74 note (keep history).  
5. Add **M3g** to [08-implementation-checklist.md](../../08-implementation-checklist.md) with 74.01–74.07 placeholders.  
6. Add step-74 row to [batches/README.md](../README.md).

## Done when

- Lock docs written; checklist and README updated.  
- **No implementation code** in this batch.

## Status

Done.
