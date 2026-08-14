# Step 38.01 — Planning lock

**Plan + docs only.** Lock parchment pipeline scope before implementation batches 02–05.

**Repos:** Planning  
**Depends on:** [00-index](./00-index.md) · [16-map-platform.md](../../16-map-platform.md) (requirements 2, 3)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md)

## Locked — layer model

| Layer | Generator | Served as | On screen? | Pick? |
|-------|-----------|-----------|------------|-------|
| Parchment base | `parchmentgen.py` | `GET /{map}/map` (preferred) | Yes — bottom | No |
| Pick reference | `create_map(..., apply_overrides=False)` | `GET /{map}/mapdata/{mode}` | Hidden canvas only | **Yes** |
| Region overlays | `regiongen.py` (muted fills + borders) | `GET /{map}/regions/{mode}/…` | Yes — hover + drill stack | No |
| Province modes | existing `terrain` / `fertility` / `prosperity` | `mapdata` + overlay img | Yes (dev) | Yes |

**Critical:** never bake parchment grading or HSL muting into pick maps or the hidden canvas source. Vassal pixels must remain selectable ([`mapgen.py`](../../../backend/src/scripts/mapgen/mapgen.py) `apply_overrides=False`).

## Locked — inputs

| File | Path | Rule |
|------|------|------|
| Background (Xaero) | `input/{map}/map.png` | Plain world map export from Xaero; **source** for parchment; same pixel grid as `provinces.png`; never overwritten by regen |
| Province grid | `input/{map}/provinces.png` | Dimension authority for validation |
| Parchment output | `output/{map}/maps/parchment_base.png` | Generated display base |
| Paper texture | `backend/src/assets/map/paper_texture.png` | Tileable multiply overlay (add in 38.02) |

Validation on regen start: if `map.png` missing or size mismatch vs `provinces.png` → log warning, skip parchment step, `/map` keeps serving raw `map.png`.

**Do not** write graded pixels back to `map.png` — preserves the pristine Xaero source for re-runs.

## Locked — parchment grade (batch 02)

Pipeline order (each step on full RGBA canvas):

1. **Desaturate** — reduce saturation (~40–55%; exact factor tuned in 38.02)
2. **Warm tone** — slight sepia / lift reds-yellows (color matrix or HSL hue shift)
3. **Paper texture** — multiply blend with tiled `paper_texture.png` at low opacity
4. **Vignette** — radial darken toward edges (subtle; must not crush coast detail)
5. **Write** `output/{map}/maps/parchment_base.png`

No vector labels, no political colour in this file.

## Locked — muted political colour (batch 03)

| Decision | Choice |
|----------|--------|
| Source RGB | Nation `rgb` from compiled mode JSON (same as today) |
| Transform | Shared helper `display_rgb(rgb) -> (r,g,b)` — desaturate + lower lightness vs pick colour |
| Apply in | `regiongen.py` paint + hover lighten path; **not** in pick `create_map` |
| Interior mask | Optional: multiply nation fill toward parchment sample under bbox (defer if slow; v1 = HSL only) |
| Static overlays | Visible `mapObjects` region PNGs use same muted palette |
| Borders | `border_thickness = 5` via [`border_paint.py`](../../../backend/src/scripts/util/border_paint.py); colour near-black `(0,0,0)`; optional 1px inner glow / soften pass in 38.03 |

Pick colours stay the raw `rgb` triple used in `nation_map.png` for canvas lookup.

## Locked — API / regen (batch 02–03)

| Change | Detail |
|--------|--------|
| `map_routes.py` `GET /{map}/map` | Prefer `output/{map}/maps/parchment_base.png`; else `input/{map}/map.png` (raw Xaero) |
| `regeneration.py` | After compile, before mode loop: `create_parchment_base(map_name)` when `map.png` valid |
| `dirs.py` | `parchment_image(map_name)` helper |
| New modules | `mapgen/parchmentgen.py`, `util/display_colour.py` |

No new public JSON routes required for v1.

## Locked — frontend (batch 04)

| Decision | Choice |
|----------|--------|
| Base `<img>` | Keep `src={api}/{mapId}/map` — backend swap only |
| Overlay opacity | Tune default `opacity-80` → ~`opacity-70` if muted fills read too strong (verify visually) |
| Province modes | Unchanged (`terrain` / `fertility` / `prosperity` still use `mapdata` overlay) |
| Fallback | If parchment missing, existing raw `map.png` behaviour |

No pan/zoom library; no label layer ([step-40](../step-40/00-index.md)).

## Out of scope (step 38)

- Paradox curved labels ([step-40](../step-40/00-index.md))
- Staff map gating ([step-40](../step-40/00-index.md))
- Capitals, forts, wars, chronicle, wealth ([step-42](../step-42/00-index.md)–[46](../step-46/00-index.md))
- SimpleFactions export changes
- Rewriting pick/hover architecture
- Separate `xaero_world.png` input file (use existing `map.png`)

## Hub edits (38.01)

- [x] [00-index](./00-index.md) — batch links + status
- [x] [08-implementation-checklist.md](../../08-implementation-checklist.md) — M2 sub-bullets
- [x] [STAGING.md](../../../STAGING.md) — Step 38 operator checklist
- [x] [16-map-platform.md](../../16-map-platform.md) — layer table + diagram

## Verify

- [x] Locked tables in this file
- [x] Batches [02](./02-parchment-base.md)–[05](./05-docs-verify.md) exist
- [x] Hub docs updated
- [x] No application code in 38.01

## Status

**Done** (38.01). Next: [02-parchment-base](./02-parchment-base.md).
