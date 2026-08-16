# Step 51.04 — Province geometry cache

**Repos:** `ProvinceSystem` backend  
**Depends on:** [03-vectorize-map-paint](./03-vectorize-map-paint.md)

## Goal

Load `provinces.png` **once per `_sync_regeneration`** and build reusable arrays shared by all modes:

- `provinces_rgba` — `(H, W, 4)` uint8
- `province_id_map` — `(H, W)` uint16 (rgb → id via `load_provinces`)
- `land_mask` — boolean (exclude sea/water if needed)

Eliminates **13×** full image open + decode and enables province-id LUT map paint.

## Build

| File | Action |
|------|--------|
| [`backend/src/scripts/mapgen/geometry_cache.py`](../../../backend/src/scripts/mapgen/geometry_cache.py) | **Add** — `MapGeometryCache` dataclass + `load(map_name)` |
| [`backend/src/scripts/mapgen/map_paint_numpy.py`](../../../backend/src/scripts/mapgen/map_paint_numpy.py) | **Add** — `paint_from_province_id_lut` |
| [`backend/src/scripts/util/regeneration.py`](../../../backend/src/scripts/util/regeneration.py) | **Wire** — create cache before mode loop; pass into mapgen/regiongen |
| [`backend/src/scripts/mapgen/mapgen.py`](../../../backend/src/scripts/mapgen/mapgen.py) | Accept optional `cache` |
| [`backend/src/scripts/mapgen/prosperitygen.py`](../../../backend/src/scripts/mapgen/prosperitygen.py) | Accept optional `cache` |
| [`backend/src/scripts/mapgen/regiongen.py`](../../../backend/src/scripts/mapgen/regiongen.py) | Accept optional `cache` (numpy array scan) |
| [`backend/src/scripts/mapgen/test_geometry_cache.py`](../../../backend/src/scripts/mapgen/test_geometry_cache.py) | **Add** — cache + LUT correctness tests |

## Benchmark results (2026-08-16)

| Metric | v1-map-paint | v2-geometry-cache | Change |
|--------|--------------|-------------------|--------|
| Total `fullregen` | 1075535 ms | **737159 ms** | **−31%** (~5.6 min saved) |
| Map paint sum (6 modes) | 94319 ms | **8447 ms** | **−91%** (~11× faster) |
| Per-mode map (typical) | ~12–21s | **~0.8–2.2s** | ~11× faster |
| `geometry.cache` (one-time) | — | 32254 ms | single load + id LUT build |
| Pixel output vs v1 | — | **IDENTICAL** | `compare_regen_snapshot --pixels` pass |

Regiongen also improved (~2× on several modes) from eliminating repeated `provinces.png` decode and faster numpy pixel reads in the scan loop.

## Verify

- [x] Single `provinces.png` open per regen (via `geometry.cache` timing row)
- [x] Manifest match vs `v1-map-paint` (IDENTICAL)
- [x] Unit tests pass (`test_geometry_cache`, `test_map_paint_numpy`)

## Status

**Done** (2026-08-16).

## Next

[05-regiongen-numpy](./05-regiongen-numpy.md).
