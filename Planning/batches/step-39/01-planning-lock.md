# Step 39.01 — Planning lock

**Plan + docs only.** Lock ink cartography scope before implementation batches 02–06.

**Repos:** Planning  
**Depends on:** [00-index](./00-index.md) · [step-38/01-planning-lock](../step-38/01-planning-lock.md)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md)

## Locked — visual target

Step 38 v1 = *desaturated satellite on warm paper*. Step 39 = *hand-drawn fantasy map*:

| Element | 38 v1 (current) | 39 ink (target) |
|---------|-----------------|-----------------|
| Terrain colour | Grey-green wash | Cream/tan parchment; shadows warm brown |
| Coastlines / rivers | Faded photo detail | Reinforced **ink lines** (edge detect overlay) |
| Nation fills | Muted original hue @ 72% | Earth-tone wash (ochre, rust, sepia); identity via hue **shift into earth band** |
| Borders | Always black + black soften | **Adaptive** dark or cream ink by fill luminance |
| Mood | Disabled / foggy | Finished cartography |

Reference aesthetic: Paradox / GSG political map **terrain layer** (before labels) — not satellite, not flat vector.

## Locked — layer model

Unchanged from Step 38 — only **display generators** change:

| Layer | Generator | Served as | Pick? |
|-------|-----------|-----------|-------|
| Ink parchment base | `parchmentgen.py` (new grade) | `GET /{map}/map` | No |
| Pick reference | `create_map(..., apply_overrides=False)` | `GET /{map}/mapdata/{mode}` | **Yes** |
| Region overlays | `regiongen.py` + earth-tone + adaptive borders | `GET /{map}/regions/…` | No |

**Critical:** never bake ink grade or earth-tone into pick maps or hidden canvas source.

## Locked — ink palette (constants in `parchmentgen.py`)

Tunable in 39.02; lock v1 defaults here:

| Token | RGB (v1) | Use |
|-------|----------|-----|
| `PAPER_HIGH` | `#f0e6d2` | Highlights, coast foam |
| `PAPER_MID` | `#d4c4a8` | Midtones |
| `PAPER_SHADOW` | `#8b7355` | Hills, forest mass |
| `INK_DARK` | `#2a1f14` | Coastlines, rivers, strong edges |
| `INK_MID` | `#4a3728` | Secondary terrain lines |

Luminance remap: convert source `map.png` to greyscale → map pixel value through 3-stop gradient (shadow → mid → high). Optional slight warm multiply after.

## Locked — edge overlay (39.02)

1. Build luminance from source `map.png`
2. Edge detect (PIL `FIND_EDGES` or Sobel via numpy if already a dep — prefer Pillow-only v1)
3. Invert/threshold to ink mask
4. Composite `INK_DARK` lines on parchment base at `EDGE_OPACITY` (~0.45–0.65)
5. Reduce or remove Step 38 vignette (`VIGNETTE_STRENGTH` ≤ 0.15); texture via soft-light/overlay blend not heavy multiply

## Locked — earth-tone fills (39.03)

Replace `display_rgb()` HSL half-sat with:

1. Convert nation `rgb` → HSL
2. **Clamp hue** into earth band (~25°–55°) with small per-nation offset from original hue (preserve distinguishability)
3. Saturation cap ~0.35–0.45; lightness ~0.45–0.55 for fills
4. `hover_rgb()` — raise lightness + slight sat bump (same earth family)

Optional v1.1 (defer if slow): sample `parchment_base` median under region bbox; blend fill 15% toward that sample.

## Locked — adaptive borders (39.04)

| Fill luminance (relative) | Border colour | Notes |
|---------------------------|---------------|-------|
| ≥ 0.55 (light) | `INK_DARK` `(42, 31, 20)` | Current behaviour |
| < 0.55 (dark) | `INK_LIGHT` `(232, 220, 200)` | Cream ink on dark realms |
| All | Drop black soften halo **or** replace with 1px opposite-contrast inner stroke |

`border_thickness` stays **5** at full map resolution; nested fast-path border owner keys must use **display colour** consistently (audit 38.03 fast vs nested path).

## Locked — frontend (39.05)

| Layer | Opacity (v1) |
|-------|----------------|
| Hover overlay | `0.72` (unchanged or `0.75`) |
| Drill stack (`mapObjects` visible) | `0.88` |
| Province modes (`terrain` / etc.) | `0.72` unchanged |

## Locked — regen / API

| Change | Detail |
|--------|--------|
| Output path | Same `parchment_base.png` — in-place algorithm swap |
| `regeneration.py` | No new hook; `create_parchment_base` behaviour changes |
| `map_routes.py` | No route change |
| Tests | Update `test_display_colour.py`; add parchment grade snapshot or constant unit tests |

## Out of scope (step 39)

- Curved nation labels → [step-40](../step-40/00-index.md)
- Pan/zoom tiered label density
- Full vector hatching / biome icons
- Pick map or province grid changes
- Re-exporting `map.png` from Xaero (operator asset unchanged)

## Verify (planning)

- [x] Palette and layer model locked
- [x] Pick safety rule restated
- [x] Batch split 02–06 agreed
- [ ] Implementation batches 02–05 complete
- [ ] Operator STAGING Step 39 checklist

## Status

**39.01 done.** Next batch: [02-ink-base](./02-ink-base.md).
