# Step 48.02 — Label neighbor geometry

**Repos:** `ProvinceSystem` backend  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Goal

Implement offline computation of `province_label_neighbors.json` and commit generated files for `main` and `dev`.

## Build

| File | Action |
|------|--------|
| [`backend/src/scripts/map_tools/province_geometry.py`](../../../backend/src/scripts/map_tools/province_geometry.py) | Add `build_label_neighbors()`, crossable mask, bounded BFS bridge scan |
| [`backend/src/scripts/map_tools/build_province_geometry.py`](../../../backend/src/scripts/map_tools/build_province_geometry.py) | Write label neighbors in same CLI run |
| [`backend/src/scripts/map_tools/test_province_geometry.py`](../../../backend/src/scripts/map_tools/test_province_geometry.py) | Synthetic grid tests for bridge / block / distance cap |
| [`backend/src/defines/main/province_label_neighbors.json`](../../../backend/src/defines/main/province_label_neighbors.json) | Generated — Calavorn |
| [`backend/src/defines/dev/province_label_neighbors.json`](../../../backend/src/defines/dev/province_label_neighbors.json) | Generated — dev parity |

### Loader helpers

- Read terrain per province id from existing [`load_provinces`](../../../backend/src/scripts/loader/provinces.py) or extend it to expose `id → terrain`.
- `WATER_TERRAINS = frozenset({"water", "sea"})`.

### Validation (hard failures)

- Symmetric undirected graph (same as strict neighbors).
- Every edge in `province_neighbors` present in `province_label_neighbors`.
- No self-loops; neighbor ids exist in `provinces.txt`.

### Validation (warnings)

- Edge count much larger than strict graph (log for operator review).
- Provinces with zero neighbors in both graphs (isolated island — expected rare).

## Operator command

```bash
cd backend/src
python -m scripts.map_tools.build_province_geometry main
python -m scripts.map_tools.build_province_geometry dev
python -m scripts.map_tools.test_province_geometry
```

## API

Existing [`data_routes.py`](../../../backend/src/api/data_routes.py) serves any `defines/{map}/*.json` by filename — confirm `province_label_neighbors` resolves without route changes.

| URL | File |
|-----|------|
| `GET /{map}/data/province_label_neighbors` | `defines/{map}/province_label_neighbors.json` |

## Expected stats (`main`, estimate)

- Provinces: **317** (unchanged)
- Strict undirected edges: **~790**
- Label edges: **strict + water bridges** (operator logs delta after first build)
- Build time: add **~10–60s** to geometry CLI (target: single pass + pruned BFS, not O(n²) full image BFS)

## Visual QA (operator)

After generation, spot-check on `/map/main`:

- [ ] Southern island nation(s) — one label per archipelago where channels &lt; 100px
- [ ] Known land exclaves — still separate labels
- [ ] No obvious over-merge across wide bays (if found, note for `LABEL_BRIDGE_MAX_PX` tune)

## Verify

- [x] `python -m scripts.map_tools.test_province_geometry` passes (including new cases)
- [x] `defines/main/province_label_neighbors.json` committed
- [x] `defines/dev/province_label_neighbors.json` committed
- [x] `label ⊇ strict` validation passes in tests
- [ ] `GET /main/data/province_label_neighbors` returns JSON (backend running)

## Out of scope

- Frontend wiring ([03-frontend-wiring](./03-frontend-wiring.md))
- `fullregen` hook
- Manual override file

## Status

**Done.** Next: [03-frontend-wiring](./03-frontend-wiring.md).
