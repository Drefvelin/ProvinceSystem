# Step 48.03 — Frontend wiring

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [02-label-neighbor-geometry](./02-label-neighbor-geometry.md)

## Goal

Load `province_label_neighbors.json` and use it **only** for label connected-component grouping across all political label modes.

## Build

| File | Action |
|------|--------|
| [`frontend/app/hooks/useMapGeometry.ts`](../../../frontend/app/hooks/useMapGeometry.ts) | Fetch `province_label_neighbors`; expose `labelNeighbors`; fallback to `neighbors` on failure |
| [`frontend/app/lib/mapLabels.ts`](../../../frontend/app/lib/mapLabels.ts) | `labelsForProvinces` / `computeNationLabels` / `computeVisibleRegionLabels` accept `labelNeighbors` for `connectedComponents` |
| [`frontend/app/components/MapViewer.tsx`](../../../frontend/app/components/MapViewer.tsx) | Pass `labelNeighbors ?? neighbors` into label pipeline |
| [`frontend/app/lib/mapLabels.test.ts`](../../../frontend/app/lib/mapLabels.test.ts) | Bridge vs land-block fixtures; exclave tests unchanged on strict graph |

### Type alias

Reuse `ProvinceNeighbors` type for label neighbors (same JSON shape). Optional rename to `ProvinceAdjacency` later — not required for 48.

### Fallback contract

```text
labelNeighbors = fetched label graph ?? strict neighbors
```

Keeps dev/staging working if JSON not deployed yet.

## Behaviour checks

| Scenario | Expected |
|----------|----------|
| Nation with water-separated provinces &lt; 100px | Single label |
| Nation with land-separated exclave | Multiple labels (same name) |
| Title modes (kingdom, duchy, …) | Same grouping rules per title’s province set |
| Trade guild exclaves | Water-connected blobs merge; land exclaves stay split |
| `terrain` / `fertility` / `prosperity` | No labels |

## Unit tests

Add fixtures to `mapLabels.test.ts`:

1. **`labelBridgeNeighbors`** — provinces 1 and 2 connected only via label graph; `connectedComponents` returns one component.
2. **`labelBridgeBlocked`** — strict neighbors match exclave fixture; label graph must not add edge through province 99 “land bridge”.
3. **`labelNeighborsSuperset`** — every strict edge still connects in label graph (mirror backend validation).

Keep existing exclave tests using **strict** neighbors where they assert land separation.

## Verify

- [ ] `npm test` — mapLabels tests green
- [ ] `npm run build` passes
- [ ] `/map/main` nation mode: archipelago spot-check (manual)
- [ ] `/map/main` kingdom/trade: labels still render; no regression on hover/pick

## Out of scope

- Hub docs ([04-docs-verify](./04-docs-verify.md))
- Changing `province_neighbors` usage outside labels

## Status

**Done.** Next: [04-docs-verify](./04-docs-verify.md).
