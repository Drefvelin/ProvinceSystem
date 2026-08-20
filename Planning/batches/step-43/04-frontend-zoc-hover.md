# Step 43.04 — Frontend fort ZOC hover

**Repo:** `ProvinceSystem` (frontend)  
**Depends on:** [03-ps-zocgen](./03-ps-zocgen.md)  
**Unlocks:** [05-docs-verify](./05-docs-verify.md)

## Goal

On political marker modes, hovering a **fort** installation pin shows the precomputed ZOC hatch overlay from 43.03. Port/airport pins show no ZOC. Nation region hover remains separate (`hoveredOverlay`).

## Deliverables

| Item | Path / behavior |
|------|-----------------|
| Types | `FortMarker` + `forts[]` on `MapMarkersResponse` in `types.ts` |
| Data hook | `useMapMarkers` passes through `forts[]` |
| Lookup | `app/lib/fortZoc.ts` — `lookupFortZocOverlay(marker, forts)` |
| Hover state | `hoveredFortZoc` in `MapViewer` + `useMapHover` |
| Render | `MapCanvas` ZOC layer via `HoverOverlayImage` (opacity 1) |
| Tests | `fortZoc.test.ts` |

## Locked behavior

- Trigger: hover fort installation marker (`kind === "fort"`)
- Modes: political marker modes only (`isMarkerMapMode`)
- Lookup: `installation:{id}` marker → `forts[]` row by `id`
- Layer: separate from nation `hoveredOverlay`; marker hover still clears nation overlay
- Stack: drill stack → `hoveredFortZoc` → nation hover → markers

## Verification

- [x] `npm test` — `fortZoc.test.ts` passes
- [ ] Hover fort pin on `nation` mode → hatch appears
- [ ] Hover port/airport → no hatch
- [ ] Hover nation region (not pin) → nation fill, no ZOC
- [ ] `terrain` mode → no markers, no ZOC
- [ ] `dev` map with auth → ZOC PNG loads via bearer token

## Status

**Done** (2026-08-19).
