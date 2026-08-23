# Step 74 — Map title editor: offline export workflow

**Repos:** `ProvinceSystem` frontend + backend  
**Depends on:** [step-72](../step-72/00-index.md) (editor shipped) · [step-73](../step-73/00-index.md) (UX + perf) · [step-54](../step-54/00-index.md) (province grid) · [step-41](../step-41/00-index.md) (staff read gate)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Shift lore-staff workflow from **push JSON to server + regen in browser** to **edit locally, download ZIP, manual deploy**. Improve load UX with staged progress. Use **only precomputed** province grid files (no on-demand grid build when only titles change).

**Supersedes** step 72 save-to-server + editor regen UI. **Does not** reopen step 73 entry, nav, layout, or canvas paint work.

## Problem statement

| Issue | Symptom | Target |
|-------|---------|--------|
| Deploy model | Save to server writes `defines/` from browser | Download ZIP; operator merges JSON on host |
| Preview model | Regenerate triggers mapgen from editor | Live canvas paint only; mapgen on host after ZIP merge |
| Province grid | On-demand rebuild + image fallback (73.05) | `province_id_grid.bin.gz` required; script when provinces change |
| Loading UX | Generic "Loading..." | Staged % + label ("40% - Loading province index…") |
| Redundant UI | Open map link in save bar | Map already embedded; remove link |
| Wrong action | Regenerate button | **Reset changes** reverts to loaded snapshot |

## Locked UX (step 74)

| Piece | Choice |
|-------|--------|
| Persist | **Download ZIP** (`county.json`, `duchy.json`, `kingdom.json`, `empire.json`) |
| Reset | Revert all four tiers to **last loaded** server snapshot (confirm if dirty) |
| Regenerate | **Not in editor UI**; operator runs mapgen on host |
| Open map | **Removed** from toolbar |
| Province grid | `defines/{map}/province_id_grid.bin.gz` **required**; `GET /editor/province-index` reads file only |
| Grid rebuild | Manual: `python -m scripts.tools.build_province_id_grid --map {map}` when `provinces.png` / `provinces.txt` change |
| Loading | Staged progress with % and stage labels |
| Auth reads | Staff GET (titles, pick, grid, map image) unchanged |
| Auth writes | Editor does **not** call POST titles/regen in product path |
| SF deploy | Title JSON → `defines/` + mapgen; `province_id_grid.bin.gz` → SF **only when provinces change** (step 54) |

Entry, nav, and locked map from step 73 remain unchanged.

## Operator workflow (locked)

```text
1. Lore staff: edit in browser → Download ZIP
2. Operator: merge JSON into defines/{map}/
3. Operator: run mapgen / fullregen on host (not in browser)
4. Deploy viewer output; copy province_id_grid to SF only if provinces changed
```

## Batches

1. **[01-planning-lock](./01-planning-lock.md)** — Lock offline export, reset, grid-only, progress UX  
2. **[02-precomputed-grid-only](./02-precomputed-grid-only.md)** — Grid endpoint file-only; drop on-demand build  
3. **[03-loading-progress](./03-loading-progress.md)** — Staged loader with % and messages  
4. **[04-export-zip](./04-export-zip.md)** — Download ZIP; remove Save to server  
5. **[05-reset-and-toolbar](./05-reset-and-toolbar.md)** — Reset replaces Regenerate; remove Open map  
6. **[06-api-deprecation](./06-api-deprecation.md)** — Remove editor calls to POST titles/regen  
7. **[07-docs-verify](./07-docs-verify.md)** — STAGING, runbook, checklist close-out  

## Checkpoint

```text
Editor: Download ZIP contains valid tier JSON; no Save to server
Reset restores loaded snapshot; no Regenerate; no Open map link
Loading shows progress stages (e.g. 40% - Loading province index…)
province-index 404 if grid file missing (clear error + script hint)
npm test + test_editor_routes green
STAGING reflects ZIP workflow (74.07)
```

## Status

**74.01 done.** **74.02 done.** **74.03 done.** **74.04 done.** **74.05–74.07 planned.**

## Next

Implement [74.05](./05-reset-and-toolbar.md) Reset replaces Regenerate; remove Open map.
