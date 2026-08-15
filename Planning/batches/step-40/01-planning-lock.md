# Step 40.01 — Planning lock

**Plan + docs only.** Lock nation label scope before implementation batches 02–06.

**Repos:** Planning (+ `ProvinceSystem` frontend for later batches)  
**Depends on:** [00-index](./00-index.md) · [step-39/01-planning-lock](../step-39/01-planning-lock.md)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 4

## Locked — visual target

Paradox / GSG-style **nation names on overview** — readable on the colour satellite base and parchment-wash overlays from step 39.

| Element | Choice (v1) |
|---------|-------------|
| Placement | Straight text along the line between two **endpoint province centroids** (diameter of connected province graph) |
| Curve | **Deferred** — no SVG `textPath` spline in v1; add in v1.1 if straight lines read poorly |
| Typography | Dark ink `#2a1f14`; optional light halo/stroke for contrast on busy terrain |
| Font | Bundled in frontend (serif matching site tone); exact face locked in [02-map-geometry](./02-map-geometry.md) spike |
| Zoom | Fixed font size in map-pixel units — **does not scale** with zoom |

Reference: political map **name layer** on Paradox overview — not modal text, not province tooltips.

## Locked — layer model

Extends step 38/39 stack:

| Layer | Source | Served as | On screen? | Pick? |
|-------|-----------|-----------|------------|-------|
| Colour base | `input/{map}/map.png` | `GET /{map}/map` | Yes — bottom | No |
| Region overlays | `regiongen.py` | `GET /{map}/regions/{mode}/…` | Yes — hover + drill | No |
| **Label layer** | **Frontend SVG** from geometry + `nation.json` | Computed client-side | Yes — above base, below UI chrome | No |
| Pick reference | `create_map(..., apply_overrides=False)` | `GET /{map}/mapdata/{mode}` | Hidden canvas only | **Yes** |

**Critical:** labels never touch pick maps, hidden canvas, or `regiongen` PNGs. Placement uses province graph + centroids only.

## Locked — static geometry files

Generated when `provinces.png` changes — **not** on every `fullregen`.

| File | Path | Generator |
|------|------|-----------|
| `province_neighbors.json` | `defines/{map}/` | Refactor [`find_neighbours.py`](../../../backend/src/editor/find_neighbours.py) → map-scoped script using [`dirs.py`](../../../backend/src/scripts/util/dirs.py) |
| `province_centroids.json` | `defines/{map}/` | New script: scan `input/{map}/provinces.png`; per province id store `{ x, y, pixel_count }` (mean pixel position + area) |

**Current gap:** [`defines/dev/province_neighbors.json`](../../../backend/src/defines/dev/province_neighbors.json) exists; **`main` (Calavorn) has neither file** — batch [02-map-geometry](./02-map-geometry.md).

### `province_neighbors.json` shape

```json
{
  "291": [290, 292, 310],
  "290": [291, 289]
}
```

Keys and values are province id strings; adjacency is undirected (4-connected on `provinces.png`).

### `province_centroids.json` shape

```json
{
  "291": { "x": 1420, "y": 880, "pixel_count": 1240 }
}
```

`x` / `y` = mean pixel of province colour on the map grid. `pixel_count` used for min-area filter.

## Locked — label layout algorithm (v1)

Input per frame: `nation.json` (political state) + static geometry files. **No region overlay PNGs.**

For each nation entry with `provinces[]`:

1. **Connected components** — restrict `province_neighbors` to the nation's province set; BFS or union-find. Each component → one label (exclaves get separate labels).
2. **Diameter endpoints** — on each component subgraph: BFS from arbitrary node → farthest `A` → BFS from `A` → farthest `B`.
3. **Segment** — line from `centroid(A)` to `centroid(B)` in map pixel space.
4. **Text** — nation `name` centered on segment midpoint; rotate to segment angle; fixed `LABEL_FONT_SIZE` (map pixels).
5. **Skip** component when:
   - `province_count < MIN_PROVINCES` (v1 default: **3**), or
   - `sum(pixel_count)` across component `< MIN_PIXEL_AREA` (v1 default: **TBD in 02** — tune on `main`).

Layout function (frontend): `computeNationLabels(regionData, neighbors, centroids) -> LabelSpec[]`.

## Locked — map mode scope

| Mode | Labels v1 |
|------|-----------|
| `nation` | **Yes** — `/map/main` default |
| `kingdom`, `duchy`, `empire`, `county`, `trade` | **No** in step 40 — see [step 47](../step-47/00-index.md) |
| `terrain`, `fertility`, `prosperity` | **No** |

Rationale: only `nation.json` (and `county.json`) carry `provinces[]` in step 40; kingdom/duchy entries use title trees without province lists ([`kingdom.json`](../../../backend/src/defines/main/kingdom.json)). Title/trade labels and Calavorn province modes are [step 47](../step-47/00-index.md).

## Locked — zoom behaviour

Pan/zoom is not shipped yet; lock the rule for when it lands:

| Rule | Choice |
|------|--------|
| Overview | Labels **visible** when `currentZoom <= LABEL_MAX_ZOOM` |
| Zoomed in | Labels **hidden** when `currentZoom > LABEL_MAX_ZOOM` |
| Font size | **Constant** — no scaling with zoom |
| `LABEL_MAX_ZOOM` | Placeholder constant (e.g. `1.5`); tuned when pan/zoom ships |

Batch [05-label-polish](./05-label-polish.md) adds a stub hook; implementation waits on zoom feature.

## Locked — data flow / API

Reuse [`data_routes.py`](../../../backend/src/api/data_routes.py) `{file}.json` pattern:

| Route | File | Consumer |
|-------|------|----------|
| `GET /{map}/data/nation` | `defines/{map}/nation.json` | Existing — [`useMapModeData.ts`](../../../frontend/app/hooks/useMapModeData.ts) |
| `GET /{map}/data/province_neighbors` | `defines/{map}/province_neighbors.json` | New — batch 02 |
| `GET /{map}/data/province_centroids` | `defines/{map}/province_centroids.json` | New — batch 02 |

Layout runs **in the browser** — no server-side layout cache for v1. Chronicle (step 45) reuses the same compositor with per-date nation state.

## Locked — chronicle cross-reference (step 45)

[Step 45](../step-45/00-index.md) will store **daily political state JSON** (nation ownership, subjects, wealth, events) — not composited map PNGs. The website renders each date with:

- same `MapCanvas` + region overlays + `LabelLayer`
- date slider + wealth charts

Label layout recomputes from that day's `nation` state + static geometry. Update step 45 snapshot wording in [06-docs-verify](./06-docs-verify.md).

## Locked — frontend integration (later batches)

| Piece | Location |
|-------|----------|
| Layout lib | `frontend/app/lib/mapLabels.ts` |
| Label SVG | `frontend/app/components/map/LabelLayer.tsx` |
| Compose | [`MapCanvas.tsx`](../../../frontend/app/components/map/MapCanvas.tsx) — nation mode only |
| Pointer events | `pointer-events: none` on label layer |

## Out of scope (step 40)

- Backend PNG / Cairo / Skia label rasterization
- Curved `textPath` splines (v1.1)
- Labels on kingdom / duchy / empire / county / trade modes → shipped in [step 47](../step-47/00-index.md) (**done**)
- Cross-nation label collision priority (tier overlap) — defer until multi-mode labels
- Pan/zoom implementation itself
- Pick layer / `regiongen` / `fullregen` hook changes for labels
- Region overlay PNGs for placement

## Batches 02–06

| Batch | Focus |
|-------|--------|
| [02-map-geometry](./02-map-geometry.md) | Generate neighbors + centroids for `main`; API routes |
| [03-layout-lib](./03-layout-lib.md) | `computeNationLabels()` + unit tests |
| [04-frontend-layer](./04-frontend-layer.md) | `LabelLayer` in `MapCanvas`; nation mode only |
| [05-label-polish](./05-label-polish.md) | Min-size filters, zoom-hide stub, font + ink styling |
| [06-docs-verify](./06-docs-verify.md) | Hub close-out + STAGING Step 40 |

## STAGING operator checklist (preview — 40.06)

- [ ] `defines/main/province_neighbors.json` and `province_centroids.json` present
- [ ] `/map/main` nation mode: nation names along territory long axis
- [ ] Exclaves get separate labels
- [ ] Labels hidden when `mapType !== "nation"`
- [ ] Hover / drill / modal / pick unchanged
- [ ] Small island nations below threshold have no label

## Verify (planning)

- [x] Layer model and pick-safety restated
- [x] Frontend-rendered labels locked (not PNG)
- [x] Province graph + centroid data model locked
- [x] Diameter algorithm locked
- [x] Nation-mode-only v1 locked
- [x] Zoom-hide rule locked (no text scaling)
- [x] Chronicle state model cross-referenced
- [x] Batches 02–06 named in 00-index

## Status

**40.01 done.** [02-map-geometry](./02-map-geometry.md) **done.** Next batch: [03-layout-lib](./03-layout-lib.md).
