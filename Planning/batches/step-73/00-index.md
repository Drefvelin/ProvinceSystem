# Step 73 — Map editor UX polish and performance

**Repos:** `ProvinceSystem` frontend (+ optional backend pick endpoint tweak)  
**Depends on:** [step-72](../step-72/00-index.md) (editor shipped) · [step-41](../step-41/00-index.md) (staff gate) · [step-49](../step-49/00-index.md) (pan/zoom)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Fix editor UX discovered after step 72 ship: remove stray nav links, enter editor from the map you are viewing, lock map context in the editor (no dropdown), fix layout overflow, and make county-tier editing responsive on full-resolution pick maps.

**Revises** step 72.01 nav + map-selector choices without re-opening core editor features (tiers, save, regen).

## Problem statement

| Issue | Symptom | Likely cause |
|-------|---------|--------------|
| Nav clutter | "Adavaar" and "Map editor" in header | `SiteHeader` staff links + UI dev listing all maps |
| Wrong entry flow | Editor is a global nav target | 72.04/72.01 locked nav link; no viewer CTA |
| Map picker unwanted | Staff can switch `main` / `dev` inside editor | `MapTitleEditor` map `<select>` + `setMapId` |
| Layout off-screen | Page scrolls horizontally; controls unreachable | Flex child without `min-w-0`; `MapViewport` inner size at 6400px before scale |
| Lag / frozen UI | Map never finishes loading; buttons dead | Full-pixel `buildProvinceIndexFromImageData` + full `provinceMap` paint on every draft change |
| UI dev local test | Login gate without paired env flags | Frontend/backend `CHARACTER_UI_DEV` (see DEV-SHORTCUTS) |

## Locked UX (step 73)

| Piece | Choice |
|-------|--------|
| Global nav | **No** "Map editor" link; **no** staff map links (e.g. Adavaar) in `SiteHeader` |
| Entry | **Edit titles** on `/map/{page}` when staff can write **that** map (or UI dev) |
| Editor URL | `/map/editor?map=main` or `?map=dev` (required `map` query) |
| Missing `map` | Redirect to `/map/main` or gate with "Open editor from the map page" |
| Editor header | Read-only map name (e.g. Calavorn); **no** map dropdown |
| `setMapId` | Removed from UI; `useEditorDraft` map fixed for session |
| Dev map page | `/map/r3b1rth` still URL-only; edit button uses `map=dev` |
| Staff probe | Reuse `GET /{map}/editor/provinces` or shared `canEditMap(mapId)` helper |

## Batches

1. **[01-planning-lock](./01-planning-lock.md)** — Lock revised nav + entry + locked-map rules  
2. **[02-nav-and-entry](./02-nav-and-entry.md)** — Strip header links; viewer **Edit titles** CTA  
3. **[03-locked-map-editor](./03-locked-map-editor.md)** — Remove map selector; require `?map=`  
4. **[04-layout-overflow](./04-layout-overflow.md)** — Flex `min-w-0`, overflow containment  
5. **[05-province-index-perf](./05-province-index-perf.md)** — Faster province index build  
6. **[06-canvas-paint-perf](./06-canvas-paint-perf.md)** — Incremental / throttled paint layers  
7. **[07-docs-verify](./07-docs-verify.md)** — Hub, STAGING, checklist, amend 72.01 lock notes  

## Checkpoint

```text
SiteHeader: Home, Map, Skins, Drinks, Character only (no Adavaar, no Map editor)
Staff on /map/main → "Edit titles" → /map/editor?map=main (Calavorn label, no dropdown)
Staff on /map/r3b1rth → "Edit titles" → /map/editor?map=dev
/map/editor without ?map= → redirect or gate (no silent default editing wrong map)
Editor layout: no horizontal page scroll at 1280px; map panel visible; tier tabs clickable
County mode: initial load completes in <3s on dev laptop; click paint feels instant after load
UI dev: NEXT_PUBLIC_CHARACTER_UI_DEV=1 + CHARACTER_UI_DEV=1 → edit CTA + editor without redeem
```

## Status

Step 73 **complete** (73.01–73.07).
