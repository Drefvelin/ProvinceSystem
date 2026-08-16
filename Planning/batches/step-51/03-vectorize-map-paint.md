# Step 51.03 — Vectorize map paint

**Repos:** `ProvinceSystem` backend  
**Depends on:** [02-baseline-snapshot](./02-baseline-snapshot.md)

## Goal

Replace Python PIL pixel loops in [`create_map`](../../../backend/src/scripts/mapgen/mapgen.py) with **numpy LUT** painting. Target: **10–20×** faster per mode (~50s → **3–5s** each).

## Build

| File | Action |
|------|--------|
| [`backend/requirements.txt`](../../../backend/requirements.txt) | **Add** `numpy` |
| [`backend/src/scripts/mapgen/map_paint_numpy.py`](../../../backend/src/scripts/mapgen/map_paint_numpy.py) | **Add** — `paint_from_rgb_lut` via packed RGB + `np.unique` gather |
| [`backend/src/scripts/mapgen/mapgen.py`](../../../backend/src/scripts/mapgen/mapgen.py) | **Refactor** — numpy path; PIL for save + `paint_borders` |
| [`backend/src/scripts/mapgen/terraingen.py`](../../../backend/src/scripts/mapgen/terraingen.py) | **Refactor** — same helper |
| [`backend/src/scripts/mapgen/prosperitygen.py`](../../../backend/src/scripts/mapgen/prosperitygen.py) | **Refactor** — same helper |
| [`backend/src/scripts/mapgen/fertilitygen.py`](../../../backend/src/scripts/mapgen/fertilitygen.py) | **Refactor** — same helper |
| [`backend/src/scripts/mapgen/test_map_paint_numpy.py`](../../../backend/src/scripts/mapgen/test_map_paint_numpy.py) | **Add** — unit tests vs slow reference |

### Borders

Keep [`paint_borders`](../../../backend/src/scripts/util/border_paint.py) on PIL load for 51.03.

## Benchmark results (2026-08-16)

| Metric | v0-baseline | v1-map-paint | Change |
|--------|-------------|--------------|--------|
| Total `fullregen` | 1310788 ms | **1075535 ms** | **−18%** (~3.9 min saved) |
| Map paint sum (6 modes) | 309406 ms | **94319 ms** | **−70%** (~3.3× faster) |
| Per-mode map (typical) | ~50–62s | **~12–21s** | ~3× faster |
| Pixel output | — | **IDENTICAL** | `compare_regen_snapshot --pixels` pass |
| Map paint in top-3 steps | yes | **no** | regions now dominate |

Map paint speedup fell short of the **8×** stretch gate; `np.unique` on 6400² plus 6× `provinces.png` reloads remain overhead. Further gains expected from [51.04 geometry cache](./04-geometry-cache.md) (province-id LUT, single load).

## Verify

- [x] All `output/main/maps/*_map.png` match `v0-baseline` (`--pixels` → IDENTICAL)
- [x] `v1-map-paint` total `fullregen` ≤ ~1100s (1075s)
- [x] Unit tests pass (`scripts.mapgen.test_map_paint_numpy`)

## Status

**Done** (2026-08-16).

## Next

[04-geometry-cache](./04-geometry-cache.md).
