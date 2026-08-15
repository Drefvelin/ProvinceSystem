# Step 48.01 — Planning lock

**Plan + docs only.** Lock label-neighbor graph scope and algorithm before batches 48.02–48.04.

**Repos:** Planning (+ `ProvinceSystem` for later batches)  
**Depends on:** [00-index](./00-index.md) · [step-40/01-planning-lock](../step-40/01-planning-lock.md) · [step-47/01-planning-lock](../step-47/01-planning-lock.md)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md)

## Locked — why a second graph

| Graph | File | Adjacency rule | Used for |
|-------|------|----------------|----------|
| **True** | `province_neighbors.json` | Shared edge on `provinces.png`; black breaks | Future game/map logic; reference |
| **Label** | `province_label_neighbors.json` | True neighbors **plus** water bridges ≤ 100px | `connectedComponents` in label layout only |

Rationale: label blobs should follow **human-readable territory** (one name across a narrow channel), not raster 4-connectivity.

## Locked — bridge rules

Two provinces `A` and `B` get a label-neighbor edge when **all** of:

1. `A` and `B` are distinct province ids present on the map.
2. They are **not** already in `province_neighbors` (those edges are copied in unconditionally).
3. Minimum **Euclidean** distance between their silhouettes on `provinces.png` is **≤ `LABEL_BRIDGE_MAX_PX`** (v1: **100**).
4. There exists a connecting path from a boundary pixel of `A` to a boundary pixel of `B` that only traverses:
   - pixels belonging to `A` or `B`, or
   - **crossable** pixels (see below),
   and never enters a **land** pixel of any other province `C`.

### Crossable pixels

| Map | Crossable |
|-----|-----------|
| `main` (Calavorn) | Black `(0,0,0)` only — no water terrain entries in `provinces.txt` |
| `dev` (Adavaar) | Black **or** province terrain `water` **or** `sea` |

**Not crossable:** any painted province pixel whose terrain is not in the water set above (plains, hills, forest, farmland, …).

This blocks “bridging” through a third nation’s land while allowing names to span rivers, lakes, and sea channels.

### Transitive grouping

Label layout already runs BFS/union-find on the graph restricted to each region’s `provinces[]`. A chain `A — water — B — water — C` yields **one** label component. No separate transitive-closure file.

## Locked — builder algorithm (v1)

Offline in Python (extend [`province_geometry.py`](../../../backend/src/scripts/map_tools/province_geometry.py) or sibling module called from same CLI):

```text
1. Load provinces.png + provinces.txt (color → id, id → terrain).
2. Compute strict province_neighbors (existing scan).
3. Initialize label_neighbors = copy(province_neighbors).
4. Build crossable_mask[y,x] from RGB + terrain rules.
5. For each province A (spatial index: bbox expanded by LABEL_BRIDGE_MAX_PX):
   Multi-source BFS from boundary pixels of A into crossable cells (+ A’s own pixels).
   Track Euclidean distance from each BFS origin boundary pixel; stop expanding past LABEL_BRIDGE_MAX_PX.
   When BFS first reaches any pixel of province B, add undirected edge A↔B.
6. validate: symmetric graph, all ids in defines, label_neighbors ⊇ province_neighbors.
7. Write defines/{map}/province_label_neighbors.json.
```

Performance: bbox pruning + boundary-only BFS seeds; run once per map when `provinces.png` / `provinces.txt` changes (~tens of seconds acceptable).

## Locked — JSON shape

Same as `province_neighbors.json` — string keys, sorted neighbor id lists, undirected:

```json
{ "291": [290, 292, 310, 315] }
```

Optional metadata file is **out of scope** v1 (distance and bridge type are not stored per edge).

## Locked — constants

| Constant | Value | Notes |
|----------|-------|-------|
| `LABEL_BRIDGE_MAX_PX` | **100** | Map pixel space (4096-wide `provinces.png`); tune on `main` after first build |
| `WATER_TERRAINS` | `water`, `sea` | From `provinces.txt` terrain column; extend only if new water types added |

## Locked — build / operator workflow

When `input/{map}/provinces.png` or `defines/{map}/provinces.txt` changes:

```bash
cd backend/src
python -m scripts.map_tools.build_province_geometry main
python -m scripts.map_tools.test_province_geometry   # extend or add test_label_neighbors
```

Same command regenerates neighbors, centroids, label grid, **and** label neighbors. **Not** part of `fullregen`.

## Locked — API

Reuse [`data_routes.py`](../../../backend/src/api/data_routes.py) `{file}.json` pattern:

| Route | File | Consumer |
|-------|------|----------|
| `GET /{map}/data/province_label_neighbors` | `defines/{map}/province_label_neighbors.json` | `useMapGeometry` |

No new route shape; file must exist for `main` after 48.02.

## Locked — frontend behaviour

| Piece | Change |
|-------|--------|
| `useMapGeometry` | Fetch `province_label_neighbors`; expose as `labelNeighbors` |
| `labelsForProvinces` / `computeVisibleRegionLabels` | `connectedComponents(..., labelNeighbors)` instead of strict `neighbors` |
| `graphDiameterEndpoints` | **Unused in production path** — axis uses `pixelDiameterEndpoints` (40.08); no change |
| Fallback | If fetch fails or file missing, use `province_neighbors` (current behaviour) |

**Do not** swap `province_neighbors` globally — only the label component step.

## Locked — map modes

All label modes from step 47 use the label graph:

`nation`, `county`, `duchy`, `kingdom`, `empire`, `trade` on `/map/main`.

Terrain / fertility / prosperity: no labels (unchanged).

## Locked — tests

| Test | Expectation |
|------|-------------|
| Synthetic: two provinces, 1px black gap, ≤100px apart | One component with label neighbors |
| Synthetic: same but land province in gap | Two components |
| Synthetic: gap >100px | Two components |
| Existing exclave fixtures | Still two components (strict land separation) |
| Validation | `label_neighbors` ⊇ `province_neighbors` for every edge |

## Out of scope (v1)

- Manual override JSON per nation/island (follow-up if 100px mis-tunes a case)
- Per-map `LABEL_BRIDGE_MAX_PX` in defines (CLI flag optional later)
- Changing `province_neighbors` or pick/hover logic
- Labels on terrain/fertility/prosperity modes
- Chronicle (step 45) — will inherit label graph automatically when wired

## Manual overrides (deferred)

If operator review finds one realm over-merged or under-merged, a future `province_label_neighbor_overrides.json` can add/remove edges. Not in 48.x unless a concrete `main` case blocks ship.

## Status

**Done.** Next: [02-label-neighbor-geometry](./02-label-neighbor-geometry.md).
