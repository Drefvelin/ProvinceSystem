# Step 40 — Nation labels (province graph)

**Repos:** `ProvinceSystem` frontend (+ map geometry tooling in backend)  
**Depends on:** [step-39](../step-39/00-index.md) (ink cartography base)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 4

## Goal

**Frontend-rendered** nation names on overview zoom: one label per connected province component, placed along the long axis (province-graph diameter) from centroid to centroid. Driven by static geometry JSON + `nation.json` political state — not backend PNGs. Same compositor will power live map and chronicle (step 45 state snapshots).

## Problem statement

| Issue | Approach |
|-------|----------|
| Map reads unnamed at overview | Nation `name` labels on each contiguous territory blob |
| Chronicle needs interactive dates | Store political **state** per day; client renders map + labels + charts |
| Placement without region PNGs | Province neighbor graph + centroids from `provinces.png` |
| Exclaves | Separate connected components → separate labels |

## Locked rules (summary)

See [01-planning-lock](./01-planning-lock.md). Highlights:

| Piece | Choice |
|-------|--------|
| Renderer | **Frontend SVG** (`LabelLayer`) — not Cairo/PNG |
| Components | One label per connected province component per nation |
| Placement | Inset corridor search on label grid; `fontSize` scaled from `segmentPx` (40.08–40.09) |
| Data | `province_neighbors.json` + `province_centroids.json` + `province_label_grid` + `nation.json` |
| Map mode | **Nation only** on `/map/main` v1 |
| Zoom | Font scales with blob span (clamped); hide when `currentZoom > LABEL_MAX_ZOOM` |
| Pick layer | Unchanged — labels never on pick canvas |

## Batches

1. **[01-planning-lock](./01-planning-lock.md)** — Scope, algorithm, API, chronicle cross-ref **done**
2. **[02-map-geometry](./02-map-geometry.md)** — Neighbors + centroids for `main`; API routes **done**
3. **[03-layout-lib](./03-layout-lib.md)** — `computeNationLabels()` + unit tests **done**
4. **[04-frontend-layer](./04-frontend-layer.md)** — `LabelLayer` in `MapCanvas`; nation mode only **done**
5. **[05-label-polish](./05-label-polish.md)** — Min-size filters, zoom-hide stub, font + ink styling **done**
6. **[06-docs-verify](./06-docs-verify.md)** — Hub close-out + STAGING Step 40 **done**
7. **[07-label-visibility](./07-label-visibility.md)** — Overlay visibility, drill scopes, z-order **done**
8. **[08-pixel-diameter](./08-pixel-diameter.md)** — Euclidean farthest pair + scaled font **done**
9. **[09-inset-corridors](./09-inset-corridors.md)** — Text corridor inset from blob border **done**

## Checkpoint

```text
defines/main/province_neighbors.json + province_centroids.json + province_label_grid exist
/map/main nation mode shows names along territory long axis
exclaves get separate labels; tiny nations skipped
labels hidden when mapType !== "nation"
labels above political PNGs; only visible nations labeled
full-border labels at overview; direct-holdings label when drilled into suzerain
label fontSize scales with blob pixel span (Nimbus large, Tenceur small)
hover / drill / modal / pick unchanged
chronicle (step 45) can reuse same LabelLayer + state JSON
```

## Status

**Step 40 done (40.01–40.09).**

## Next

[step-41 staff map access](../step-41/00-index.md).
