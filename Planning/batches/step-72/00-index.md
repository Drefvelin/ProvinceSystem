# Step 72 — Map title editor

**Repos:** `ProvinceSystem` frontend + backend  
**Depends on:** [step-41](../step-41/00-index.md) (staff map gate) · [step-49](../step-49/00-index.md) (pan/zoom) · [step-47](../step-47/00-index.md) (title rollup)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Staff-gated **web map editor** for political title hierarchy: provinces → counties → duchies → kingdoms → empires. Non-technical lore/map staff can name titles, pick RGB colours (skins-style picker), click-combine territories with clear selection vs active layers, live canvas paint, upload JSON, and regen preview.

**Operator milestone:** Wipe duchies and above on `main` (Calavorn); rename counties; rebuild hierarchy in the editor.

## Problem statement

| Issue | Root cause |
|-------|------------|
| No web editor | Only read-only `MapViewer`; Tkinter `county_editor.py` is local desktop |
| Title JSON edited by hand | `county.json` / `duchy.json` live in `defines/` with no guided UI |
| Upload API is open | `POST /{map}/data/upload/{mode}` has no staff auth |
| No RGB picker for map titles | `NameColourPicker` is hex multi-stop for MC names, not `"R,G,B"` |
| Duchy+ wrong on Calavorn | Counties OK; higher tiers need wipe + rebuild |
| No live edit feedback | Viewer only shows colours after server regen |

## Locked rules (summary)

See [01-planning-lock](./01-planning-lock.md). Highlights:

| Piece | Choice |
|-------|--------|
| Route | `/map/editor` (staff nav link when permitted) |
| Auth | Bearer + `tfmc.map.staff` (same as step 41) |
| Tiers | `county`, `duchy`, `kingdom`, `empire` (not nation/trade) |
| County pick | Province RGB from `provinces.png` / province pick map |
| Higher tiers | Pick child tier map (`mapdata/county` etc.) |
| Selection opacity | ~40% child / unassigned layer |
| Active opacity | ~90% current title + selection highlight |
| Colour storage | `"R,G,B"` string; picker UI uses hex like skins |
| Save | Full tier JSON POST to guarded upload or staff write API |
| Regen | `fullregen:{tier}` after save (operator button) |
| Overlay bbox | Omitted on save - regen computes |

## Batches

1. **[01-planning-lock](./01-planning-lock.md)** — Scope, UX, API, data contracts **done**
2. **[02-staff-write-api](./02-staff-write-api.md)** — Guarded write + validation endpoints
3. **[03-title-rgb-picker](./03-title-rgb-picker.md)** — `TitleRgbPicker` component
4. **[04-editor-route-shell](./04-editor-route-shell.md)** — Route, gate, layout, tier toolbar
5. **[05-province-pick-layer](./05-province-pick-layer.md)** — Pick canvas + live paint layers
6. **[06-county-mode](./06-county-mode.md)** — Province → county create/edit/delete
7. **[07-duchy-mode](./07-duchy-mode.md)** — County → duchy create/edit/delete
8. **[08-kingdom-empire-mode](./08-kingdom-empire-mode.md)** — Kingdom + empire modes
9. **[09-save-upload-regen](./09-save-upload-regen.md)** — Save draft, upload, regen trigger, preview link
10. **[10-main-calavorn-prep](./10-main-calavorn-prep.md)** — Wipe `main` duchy+; county rename operator runbook
11. **[11-docs-verify](./11-docs-verify.md)** — Hub, STAGING Step 72, QA checklist

## Checkpoint

```text
Staff without tfmc.map.staff → 403 on /map/editor and write APIs
Staff with permission → editor loads main or dev map
County mode: click provinces, name + colour, see live paint, save → county.json updated
Edit county: rename, recolour, add/remove provinces, delete
Duchy mode: counties at ~40% opacity; active duchy ~90%; save → duchy.json
Kingdom + empire modes same pattern
Save + Regenerate → /map/main shows new colours and labels
Calavorn: duchy/kingdom/empire empty or rebuilt; counties renamed
```

## Status

**72.01 done.** **72.02 done.** **72.03 done.** **72.04 done.** **72.05 done.** **72.06 done.** **72.07 done.** **72.08 done.** **72.09 done.** **72.10 done.** **72.11 done.**

## Next

After 72: [step-73](../step-73/00-index.md) editor UX polish + performance · optional chronicle edit log (step 45).
