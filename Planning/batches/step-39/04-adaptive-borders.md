# Step 39.04 — Adaptive ink borders

**Repos:** `ProvinceSystem` backend  
**Depends on:** [03-earth-tone-fills](./03-earth-tone-fills.md) (works with current `display_rgb` fills)

## Goal

Nation borders visible on **both** dark and light fills: cream ink on dark realms (Drakhanate), dark brown ink on light realms — fixing Step 38 uniform black stroke + black soften halo.

## Plan

1. **`border_paint.py`** — add `border_color_for_fill(fill_rgb) -> (r,g,b,a)` using relative luminance threshold (~0.55)
2. **`apply_region_borders`** — accept per-region border colour **or** compute from representative fill colour passed from `regiongen`
3. **Soften pass** — remove `soften_color = (0,0,0,128)` default; replace with optional 1px **inner highlight** using opposite ink colour at 40% opacity, or disable soften entirely for v1
4. **`regiongen.py` border loop**:
   - Pass `display_rgb(color)` as fill reference for border colour selection
   - **Fast path fix:** border owner matching must use same colour space as painted pixels (audit 38.03 fast path using raw `color` key vs `display_color` in nested path)
5. **Thickness** — keep `border_thickness = 5` at full canvas; no scale change in v1

## Build

| File | Action |
|------|--------|
| `backend/src/scripts/util/border_paint.py` | `luminance`, `border_color_for_fill`, updated `apply_region_borders` |
| `backend/src/scripts/mapgen/regiongen.py` | per-nation border colour; fast/nested path consistency |
| `backend/src/scripts/util/test_border_paint.py` | create — dark fill → light border, light fill → dark border |

## Shipped constants

```python
INK_DARK = (42, 31, 20, 255)
INK_LIGHT = (232, 220, 200, 255)
LUMINANCE_THRESHOLD = 0.55
```

Soften halo disabled (`soften=False` default). Fast path owner key remains pick `color`; stroke from `display_rgb` / `hover_rgb` luminance.

## Visual acceptance

| Check | Pass when |
|-------|-----------|
| Drakhanate | Border traceable around realm silhouette at `/map/main` zoom |
| Light nations | Border not overpowering (no thick black halo) |
| Nimbus / mixed | Border consistent along coastline-adjacent provinces |
| Nested drill | Subject/vassal borders same rules on nested PNGs |
| Hover | Border visible on `_hover` variants |

## Verify

- [x] `border_paint.py` + `regiongen.py` adaptive strokes wired (fast + nested paths)
- [x] Unit tests: `python -m unittest src.scripts.util.test_border_paint` (4 tests)
- [x] `fullregen` for `main` completes (~8.4 min on 4096²)
- [x] No pick regression (borders display-only in region PNGs)
- [ ] Operator spot-check: dark / light / mid nation borders on `/map/main`

## Status

**Done** (39.04 code). Operator visual pass recommended.

## Out of scope

Variable thickness by zoom (frontend concern); curved labels ([step-40](../step-40/00-index.md)).
