# Step 40.02 — Map geometry

**Repos:** `ProvinceSystem` backend  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Goal

Generate static province **neighbor graph** and **centroids** for label layout. Commit JSON under `defines/{map}/`; serve via existing data API. Not part of `fullregen`.

## Build

| File | Action |
|------|--------|
| [`backend/src/scripts/map_tools/province_geometry.py`](../../../backend/src/scripts/map_tools/province_geometry.py) | Single-pass scan: neighbors + centroids |
| [`backend/src/scripts/map_tools/build_province_geometry.py`](../../../backend/src/scripts/map_tools/build_province_geometry.py) | CLI entry |
| [`backend/src/scripts/map_tools/test_province_geometry.py`](../../../backend/src/scripts/map_tools/test_province_geometry.py) | Unit tests (synthetic grids) |
| [`backend/src/defines/main/province_neighbors.json`](../../../backend/src/defines/main/province_neighbors.json) | Generated — Calavorn |
| [`backend/src/defines/main/province_centroids.json`](../../../backend/src/defines/main/province_centroids.json) | Generated — Calavorn |
| [`backend/src/defines/dev/province_neighbors.json`](../../../backend/src/defines/dev/province_neighbors.json) | Regenerated (parity) |
| [`backend/src/defines/dev/province_centroids.json`](../../../backend/src/defines/dev/province_centroids.json) | Generated — dev |

**Step 48:** same CLI also writes `province_label_neighbors.json` (water bridges for label grouping only). See [step-48/02-label-neighbor-geometry](../step-48/02-label-neighbor-geometry.md).

[`find_neighbours.py`](../../../backend/src/editor/find_neighbours.py) — comment points to new CLI; editor script unchanged.

## Operator command

When `input/{map}/provinces.png` or `defines/{map}/provinces.txt` changes:

```bash
cd backend/src
python -m scripts.map_tools.build_province_geometry main
python -m scripts.map_tools.test_province_geometry
```

Optional: `dev` for editor map parity.

## API (no new routes)

Existing [`data_routes.py`](../../../backend/src/api/data_routes.py):

| URL | File |
|-----|------|
| `GET /{map}/data/province_neighbors` | `defines/{map}/province_neighbors.json` |
| `GET /{map}/data/province_centroids` | `defines/{map}/province_centroids.json` |

## JSON shapes

**Neighbors** — string keys, sorted neighbor id lists, undirected 4-adjacency on `provinces.png`:

```json
{ "291": [290, 292, 310] }
```

**Centroids** — mean pixel position + area:

```json
{ "291": { "x": 1420.45, "y": 880.12, "pixel_count": 1240 } }
```

## Locked constants for batch 03

From `main` distribution (317 provinces, 2026-03):

| Constant | Value | Notes |
|----------|-------|-------|
| `MIN_PROVINCES` | **3** | From [01-planning-lock](./01-planning-lock.md) |
| `MIN_PIXEL_AREA` | **15000** | Sum of `pixel_count` across component; smallest single province on `main` ≈ 5352 px |

## Shipped stats (`main`)

- Provinces: **317**
- Undirected edges: **790**
- Build time: ~28s (single Pillow pass)

## Verify

- [x] `python -m scripts.map_tools.test_province_geometry` passes
- [x] `defines/main/province_neighbors.json` and `province_centroids.json` committed
- [x] Province count matches `provinces.txt` (317)
- [ ] `GET /main/data/province_neighbors` returns JSON (operator, backend running)
- [ ] `GET /main/data/province_centroids` returns JSON (operator)

## Out of scope

- `computeNationLabels` ([03-layout-lib](./03-layout-lib.md))
- `fullregen` hook
- Frontend label layer

## Status

**Done** (40.02 code + `main`/`dev` JSON). Next batch: [03-layout-lib](./03-layout-lib.md).
