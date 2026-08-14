# Step 38.03 — Muted political layers

**Repos:** `ProvinceSystem` backend  
**Depends on:** [02-parchment-base](./02-parchment-base.md) (parchment can land in parallel after 38.01)

## Goal

Nation hover overlays and drill-visible region PNGs use **desaturated fantasy fills** and improved borders; pick maps stay raw RGB.

## Plan

1. **`display_colour.py`** — `display_rgb(rgb: tuple[int,int,int]) -> tuple[int,int,int]`:
   - Desaturate vs nation.json `rgb` (target ~50% sat or equivalent HSL)
   - Slightly lower lightness so fills sit on parchment without neon glow
   - `hover_rgb(rgb)` — lighten/contrast variant for `_hover` PNGs (replace ad-hoc `lighten_color` scaling or wrap it)
2. **`regiongen.py`** — Paint `base_px` / `hover_px` / nested buffers with `display_rgb` / `hover_rgb`; borders unchanged in position, still `border_thickness = 5`.
3. **Border polish (optional v1)** — In `border_paint.apply_region_borders`, optional 1-pass soften: dilate border mask by 1px at 50% opacity black before final black stroke (tune in implementation; skip if perf regresses).
4. **Pick safety audit** — Confirm `create_map(..., apply_overrides=False)` still writes raw `rgb`; add comment + unit-style spot test or script comparing one pixel in pick map vs display region PNG.
5. **Full regen** — Required after deploy for all modes (`main`, `dev`).

## Build

| File | Action |
|------|--------|
| `backend/src/scripts/util/display_colour.py` | create — shared mute + hover helpers |
| `backend/src/scripts/mapgen/regiongen.py` | use display colours for all painted pixels |
| `backend/src/scripts/util/border_paint.py` | optional edge soften (keep thickness 5) |
| `backend/src/scripts/mapgen/mapgen.py` | document pick vs display; no mute on pick path |

## Visual acceptance

| Check | Pass when |
|-------|-----------|
| On parchment | Nation blobs readable but not fluorescent |
| Adjacent nations | Border black visible at zoom levels used on `/map/main` |
| Hover | Hover state brighter than base fill, same hue family |
| Drill stack | Nested + subject overlays match muted palette |
| Pick | Hover tooltip and Ctrl+drill still resolve correct nation at province edges |

## Verify

- [x] Region PNGs differ from pre-38 RGB (spot-check one nation hex)
- [x] `nation_map.png` pick pixels still match raw `rgb` in defines JSON (code audit + unit test)
- [x] Borders present on hover overlays after fullregen (border soften enabled; operator spot-check on staging)
- [ ] `fullregen` for `main` completes without error (operator after deploy)
- [x] No regression in cropped `overlay` bbox metadata ([step-37](../step-37/03-cropped-overlays.md))

## Status

**Done** (38.03 code). Run fullregen on `main` to refresh region PNGs.

## Out of scope

Full-map political composite layer (regions-only display is enough for v1); curved labels ([step-40](../step-40/00-index.md)).
