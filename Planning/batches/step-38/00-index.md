# Step 38 — Parchment visual pipeline

**Repos:** `ProvinceSystem` backend (`mapgen`, `regiongen`) + frontend (`MapCanvas`)  
**Depends on:** [step-37](../step-37/00-index.md) (cropped overlays, interaction shell)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirements 2, 3

## Goal

Replace the flat satellite base and neon RGB nation blobs with a **fantasy cartography** look: parchment terrain graded from the plain Xaero `map.png`, muted political fills, and improved borders — while keeping the **pick-safe** RGB reference layer unchanged for hover/drill.

## Locked rules (summary)

See [01-planning-lock](./01-planning-lock.md). Highlights:

| Piece | Choice |
|-------|--------|
| Terrain input | `input/{map}/map.png` — plain Xaero world export (same pixel grid as `provinces.png`) |
| Parchment output | `output/{map}/maps/parchment_base.png` |
| Visual base URL | `GET /{map}/map` serves parchment when present; else raw `input/{map}/map.png` |
| Pick layer | `GET /{map}/mapdata/{mode}` unchanged (`apply_overrides=False`) |
| Nation display | Desaturated/dulled RGB in `regiongen` (+ static drill overlays) |
| Borders | Keep `apply_region_borders` thickness 5; optional edge soften in 38.03 |
| Labels | [step-40](../step-40/00-index.md) — after [step-39](../step-39/00-index.md) ink pass |

## Batches

1. **[01-planning-lock](./01-planning-lock.md)** — Scope lock **done**
2. **[02-parchment-base](./02-parchment-base.md)** — Grade `map.png` → `parchmentgen.py` + regen hook **done**
3. **[03-muted-political](./03-muted-political.md)** — Display colour grade + region/border pass **done**
4. **[04-frontend-composite](./04-frontend-composite.md)** — Parchment base + overlay tuning in `MapCanvas` **done**
5. **[05-docs-verify](./05-docs-verify.md)** — Hub close-out + STAGING Step 38 checklist **done**

## Checkpoint

```text
fullregen produces parchment_base.png per map
/map/main shows parchment terrain (not raw Xaero)
hover + drill overlays use muted nation colours
click / Ctrl+click / pick still work (mapdata unchanged)
readable on desktop and phone
```

## Status

**Step 38 done (38.01–38.05).** Step 39 refines nation washes, borders, and optional ink parchment (`/map/parchment`); default UI base remains colour satellite. Next build: [step-40 curved labels](../step-40/00-index.md).
