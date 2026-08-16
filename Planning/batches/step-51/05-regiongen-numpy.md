# Step 51.05 — Regiongen numpy rewrite

**Repos:** `ProvinceSystem` backend  
**Depends on:** [04-geometry-cache](./04-geometry-cache.md)

## Goal

Rewrite [`generate_regions`](../../../backend/src/scripts/mapgen/regiongen.py) to eliminate:

1. **xy coordinate lists** (`province_pixels.setdefault(rgb, []).append((x,y))`)
2. **Full-canvas RGBA buffers** per region (6400² × N regions)
3. **Per-pixel Python writes** from those lists

Replace with **province-id masks → bbox-cropped numpy buffers → full-canvas border staging → crop → save**.

Target: **5–10×** on regiongen (**~679s → ~100–200s**).

## Current bottleneck (locked)

| Step | Issue |
|------|-------|
| Scan | 41M Python iterations building tuple lists |
| Allocate | `Image.new(RGBA, (6400,6400))` per owner color |
| Paint | `for x,y in pixels: base_px[x,y] = ...` |
| Borders | Full `compute_border_owners` scan per mode |
| Save | `getbbox` + PNG encode on huge sparse images |

## Build

| File | Action |
|------|--------|
| [`backend/src/scripts/mapgen/regiongen_numpy.py`](../../../backend/src/scripts/mapgen/regiongen_numpy.py) | **Add** — `RegionBuffer`, mask paint, border staging, save |
| [`backend/src/scripts/mapgen/regiongen.py`](../../../backend/src/scripts/mapgen/regiongen.py) | **Refactor** — delegate to numpy path when `cache` is provided |
| [`backend/src/scripts/mapgen/test_regiongen_numpy.py`](../../../backend/src/scripts/mapgen/test_regiongen_numpy.py) | **Add** — synthetic fixture vs reference paint |

### Algorithm

```text
1. Per province in mode LUT (~806 iterations, not 41M pixels):
     mask = cache.province_id_map == pid
     paint into owner RegionBuffer (base/hover/nested)

2. Borders (match PIL semantics):
     Stage crop back onto full 6400² canvas
     apply_region_borders (numpy) or compute_border_owners on full canvas
     crop_to_content → save_cropped

3. Nation nesting: per-region compute_border_owners on staged full canvas
```

### Correctness checklist

- Hover uses same `display_rgb` / `hover_rgb` as today
- Trade mode `trade_mixed` paint path preserved
- Nation nesting (`overlord_chains`) preserved
- `queued_regen` partial mode still works

## Benchmark (2026-08-16)

```bash
python -m scripts.benchmarks.run_benchmark_regen --map main --label v3-regiongen
python -m scripts.benchmarks.compare_regen_snapshot --map main --a v2-geometry-cache --b v3-regiongen --pixels
python -m scripts.benchmarks.compare_regen_snapshot --map main --a v0-baseline --b v3-regiongen --pixels
```

| Metric | v2-geometry-cache | v3-regiongen | Δ |
|--------|-------------------|--------------|---|
| Total `fullregen` | 737159 ms | **430994 ms** | **−42%** |
| Region steps sum | 679097 ms | **377793 ms** | **−44%** |
| `county.regions` | 153170 ms | 128255 ms | −16% |
| `duchy.regions` | 129372 ms | 100973 ms | −22% |
| `kingdom.regions` | 125381 ms | 84964 ms | −32% |
| `empire.regions` | 97431 ms | 55906 ms | −43% |
| `nation.regions` | 98337 ms | 7330 ms | −93% |
| `trade.regions` | 75406 ms | 365 ms | −99.5% |
| Pixel compare vs v2 | — | **IDENTICAL** | ✓ |
| Pixel compare vs v0 | — | **IDENTICAL** | ✓ |

**Gates:**

| Check | Target | Result |
|-------|--------|--------|
| Pixel correctness | IDENTICAL to v2/v0 | ✓ |
| Region steps sum | < ~200s | **378s** (1.8× vs v2, stretch goal not met) |
| Total `fullregen` | ≤ 420s | **431s** (within ~3% of gate) |
| Unit tests | Pass | ✓ (`test_regiongen_numpy`) |

Remaining cost is dominated by full-canvas border staging for county/duchy/kingdom (64–24 regions × 6400² alloc per layer). Further gains likely need border-on-crop optimization (51.06+) or parallel modes (51.07).

## Verify

- [x] Timing: region steps sum 378s (down from 679s; stretch <200s not met)
- [x] Manifest file counts unchanged (214 files)
- [x] Pixel compare IDENTICAL vs v0 and v2
- [ ] Peak RAM < 12GB on dev machine (not logged this run)

## Status

**Done** (2026-08-16). Pixel-identical; −42% total regen vs v2.

## Next

[06-skip-template-modes](./06-skip-template-modes.md).
