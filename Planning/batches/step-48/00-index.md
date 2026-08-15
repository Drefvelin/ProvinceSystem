# Step 48 — Label neighbor graph (water bridges)

**Repos:** `ProvinceSystem` backend + frontend  
**Depends on:** [step-40](../step-40/00-index.md) (province geometry + label layout), [step-47](../step-47/00-index.md) (multi-mode labels)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — extends requirement 4 / 4b

## Goal

Precompute a **label-only** province neighbor graph that treats narrow water gaps as connected for name blobs, without changing true map adjacency. Archipelagos and river-separated holdings share one label when separated only by black sea or water terrain, up to a fixed pixel distance.

## Problem statement

| Issue | Root cause |
|-------|------------|
| Southern island chains get multiple labels for one nation | `province_neighbors.json` is strict 4-connected shared-edge adjacency; black pixels break the graph |
| Narrow straits / rivers split one realm into several label blobs | Same — water is not a province pixel on `main` (black) or is a separate `water`/`sea` province on `dev` |
| True adjacency must stay strict | Game/political logic may need real borders; label grouping is a separate concern |

## Locked rules (summary)

See [01-planning-lock](./01-planning-lock.md). Highlights:

| Piece | Choice |
|-------|--------|
| New artifact | `defines/{map}/province_label_neighbors.json` |
| True adjacency | `province_neighbors.json` **unchanged** |
| Label graph | Superset of `province_neighbors` + water-bridge edges |
| Bridge distance | **100px** max edge-to-edge (Euclidean), constant in builder |
| Crossable cells | Black `(0,0,0)` + provinces whose terrain is `water` or `sea` |
| Not crossable | Any other province land pixels (blocks shortcuts through third countries) |
| Build | Offline with `build_province_geometry` (same trigger as neighbors/centroids/grid) |
| Runtime | **Never** recalculated in browser or during `fullregen` |
| Consumer | `connectedComponents` in label layout only (`mapLabels.ts`) |
| Unchanged | `pixelDiameterEndpoints`, inset grid, pick canvas, `province_neighbors` for anything else |

## Batches

1. **[01-planning-lock](./01-planning-lock.md)** — Algorithm, JSON shape, constants, scope **done**
2. **[02-label-neighbor-geometry](./02-label-neighbor-geometry.md)** — Python builder + tests + `main`/`dev` JSON **done**
3. **[03-frontend-wiring](./03-frontend-wiring.md)** — API fetch, `mapLabels` + tests, `MapViewer` **done**
4. **[04-docs-verify](./04-docs-verify.md)** — Hub, STAGING Step 48, operator regen notes **done**

## Status

**48.01–48.04 done.**

## Next

[step-41 staff map access](../step-41/00-index.md) · [step-42 capitals](../step-42/00-index.md).
