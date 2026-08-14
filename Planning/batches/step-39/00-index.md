# Step 39 — Ink cartography visual pass

**Repos:** `ProvinceSystem` backend (`parchmentgen`, `display_colour`, `border_paint`, `regiongen`) + frontend (`MapCanvas`)  
**Depends on:** [step-38](../step-38/00-index.md) (parchment pipeline v1 — wash/mute baseline)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirements 2, 3 (refinement)

## Goal

Replace the **washed-out satellite** look from Step 38 with **faithful-hue parchment washes** on nation overlays, **uniform ink borders**, and an optional **ink-on-parchment** base at `/map/parchment` — while the UI default base remains **colour satellite** (`map.png`). Pick-safe RGB reference layer unchanged.

## Problem statement (operator feedback)

| Issue | Root cause (38 v1) |
|-------|---------------------|
| Base looks foggy / disabled | Heavy desat + multiply texture + vignette stacks on green satellite |
| Still reads as biome colours | No palette remap toward sepia/ink |
| Borders invisible on dark nations (e.g. Drakhanate) | Solid black borders on `display_rgb` darkened fills |
| Borders too strong on light nations | Same stroke regardless of fill luminance |
| Drill stack overlays faint | Single 0.72 opacity for hover + static |

## Locked rules (summary)

See [01-planning-lock](./01-planning-lock.md). Highlights:

| Piece | Choice |
|-------|--------|
| Terrain input | Still `input/{map}/map.png` only — never overwrite |
| Base output | Still `output/{map}/maps/parchment_base.png` — **replace grade algorithm** |
| Visual target | Parchment cream/tan paper + dark brown ink lines; **no green/blue cast** |
| Pick layer | `GET /{map}/mapdata/{mode}` unchanged (`apply_overrides=False`) |
| Map base (UI) | **Colour satellite** default (`GET /{map}/map` → `input/.../map.png`); ink parchment at `/map/parchment` only — no base toggle |
| Nation display | Faithful-hue parchment washes (`parchment_wash_rgb`) — keep nation hue, not earth-band or neon |
| Borders | Uniform **INK_DARK** stroke on all nation edges (shared-edge consistency; per-fill adaptation dropped) |
| Labels | [step-40](../step-40/00-index.md) — after ink base lands |

## Batches

1. **[01-planning-lock](./01-planning-lock.md)** — Palette, pipeline order, pick safety **done**
2. **[02-ink-base](./02-ink-base.md)** — `parchmentgen.py` luminance remap + edge overlay **done**
3. **[03-earth-tone-fills](./03-earth-tone-fills.md)** — `display_colour.py` faithful-hue parchment washes + `regiongen` **done**
4. **[04-adaptive-borders](./04-adaptive-borders.md)** — Uniform `INK_DARK` borders in `border_paint.py` **done**
5. **[05-frontend-opacity](./05-frontend-opacity.md)** — Split hover vs drill-stack opacity in `MapCanvas` **done**
6. **[06-docs-verify](./06-docs-verify.md)** — Hub close-out + STAGING Step 39 **done**

## Checkpoint

```text
fullregen rewrites parchment_base.png with ink grade (served at /map/parchment)
/map/main default base is colour satellite (map.png); nation washes on top
nation overlays are faithful-hue parchment washes (Nimbus blue, Drakhanate red, …)
uniform INK_DARK borders on all nation edges (no white/black clash at shared edges)
drill stack overlays slightly stronger than hover-only; hover crop expand 1%
click / Ctrl+click / pick still work (mapdata unchanged)
```

## Status

**Step 39 done (39.01–39.06).** Next build: [step-40 curved labels](../step-40/00-index.md).
