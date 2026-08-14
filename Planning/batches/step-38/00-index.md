# Step 38 — Parchment visual pipeline

**Repos:** `ProvinceSystem` backend (`mapgen`, `regiongen`)  
**Depends on:** [step-37](../step-37/00-index.md) (layout can ship first in parallel)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirements 2, 3

## Goal

Ingest Xaero world map PNG; generate parchment terrain base; render desaturated fantasy nation fills with improved borders (not flat RGB blobs).

## Locked rules

| Piece | Choice |
|-------|--------|
| Input | `input/{map}/xaero_world.png` aligned to `provinces.png` grid |
| Base | Parchment grade: desaturate, warm tone, paper texture multiply, vignette |
| Nations | Dulled HSL vs nation.json `rgb`; optional interior parchment mask |
| Borders | Enhanced `border_paint` (softened/jittered edges TBD in batch) |
| Pick layer | Unchanged pick-safe RGB map separate from display composites |

## Batches (when step starts)

1. **01-planning-lock**  
2. **02-xaero-ingest** — Input validation + parchment_base generator  
3. **03-muted-political** — Desaturated fills + border pass  
4. **04-frontend-composite** — Layer stack: base + political + pick  
5. **05-docs-verify** — STAGING Step 38  

## Status

**Planned.**
