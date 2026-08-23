# Step 73.01 — Planning lock

**Plan + docs only**  
**Depends on:** [00-index](./00-index.md) · [step-72/01-planning-lock](../step-72/01-planning-lock.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Lock revised map editor **entry flow** and **locked-map** rules before code batches. Supersedes conflicting lines in step 72.01 (nav link + map dropdown).

## Locked — navigation

| Before (72.01) | After (73) |
|----------------|------------|
| `SiteHeader` "Map editor" when staff | **Removed** |
| Staff map links for non-`main` maps (Adavaar) | **Removed** from global nav |
| `/map/r3b1rth` URL-only dev viewer | **Unchanged** (not in nav) |

Staff maps remain reachable by direct URL and by staff who know the link; they are not promoted in the global header.

## Locked — entry from map viewer

| Piece | Choice |
|-------|--------|
| Control label | **Edit titles** (staff-only; not shown to anonymous players) |
| Placement | Map page header row or toolbar panel (same visual weight as mode selector) |
| Visibility | `canEditMap(mapId)` true: character session + staff write for **this** `mapId`, OR UI dev pair |
| Link target | `/map/editor?map={mapId}` (`main` or `dev`) |
| Optional tier | `?tier=county` only if deep-linking from a mode is useful later; default county |

Non-staff on `/map/main`: no button. Non-staff on `/map/r3b1rth`: existing staff gate unchanged.

## Locked — editor map context

| Piece | Choice |
|-------|--------|
| Map selection UI | **None** |
| Map identity | From required query `map=main|dev` |
| Display | Read-only title using `MAP_DISPLAY_NAMES` or registry `display_name` |
| `/map/editor` bare | Redirect to `/map/main` **or** gate: "Open the editor from the map page" |
| Tier switching | **Unchanged** (county / duchy / kingdom / empire tabs) |
| `useEditorDraft.setMapId` | Remove from public API / UI; internal state still keyed by initial map |

## Locked — performance targets (county tier)

Measure on representative hardware with full `main` `provinces.png` (document dimensions in batch close-out).

| Metric | Target |
|--------|--------|
| Province index build | One-time main-thread or worker build **< 2s** after pick image fetch |
| Paint after click | Selection/active layer update **< 100ms** perceived |
| Page layout | No document horizontal scroll at 1280px viewport |

Approaches allowed (pick in 73.05 / 73.06):

- Downscaled pick texture for hit-test only (if parity preserved)
- Backend `province_id_grid` or prebuilt RGB lookup (avoid full ImageData scan)
- Incremental paint (only changed province ids)
- `requestAnimationFrame` throttle on rapid draft updates
- `min-w-0` / overflow CSS (73.04)

## Locked — UI dev (local)

| Env | Role |
|-----|------|
| `NEXT_PUBLIC_CHARACTER_UI_DEV=1` | Frontend fake session + edit CTA |
| `CHARACTER_UI_DEV=1` | Backend accepts Bearer `ui-dev-session` for map staff write |

Document in DEV-SHORTCUTS; **unset both on production**.

## Deliverables

1. This file (lock).  
2. Amend [step-72/01-planning-lock](../step-72/01-planning-lock.md) with a short **Superseded by step 73** note on nav + map selector rows (do not delete 72 history).  
3. Add **Step 73** row to [08-implementation-checklist.md](../../08-implementation-checklist.md) M3e follow-up section.

## Done when

- 00-index locked UX table matches this doc.  
- Checklist has 73.01–73.07 placeholders.  
- No implementation code in this batch.

## Status

Done.
