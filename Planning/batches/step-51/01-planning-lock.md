# Step 51.01 — Planning lock

**Repos:** Planning  
**Depends on:** —

## Goal

Lock performance targets, correctness gates, and the benchmark snapshot workflow for all Step 51 batches.

## Locked decisions

### Performance targets (Adavaar `main`, `fullregen`)

| Milestone | Target wall time | Notes |
|-----------|------------------|-------|
| **Baseline** | ~1311s (recorded) | `v0-baseline` — do not regress correctness |
| After 51.03 (map paint) | ≤ ~1100s | ~15% off map paint alone |
| After 51.05 (regiongen) | **≤ 420s (~7 min)** | Primary win |
| After 51.06 (skip templates) | **≤ 300s (~5 min)** | If template modes skipped |
| After 51.07 (parallel) | **≤ 180s (~3 min)** | 4+ cores; memory ~8GB+ peak |

Stretch goal **2–4 min** only with 51.05 + 51.06 + 51.07 combined.

### Correctness gates (every batch)

| Gate | Requirement |
|------|-------------|
| **Manifest** | `compare_regen_snapshot.py` reports no unexpected file changes vs previous checkpoint |
| **Pick maps** | `nation_map.png`, `trade_map.png`, etc. — per-pixel RGBA match OR documented tolerance (see below) |
| **Region crops** | Same file set (count + names); bbox metadata in defines JSON unchanged |
| **Defines JSON** | `defines/main/{mode}.json` overlay fields unchanged |
| **API smoke** | `test_map_access`, `test_markers`, `test_province_geometry` pass |
| **Timing log** | `_RegenTimings` summary saved to `benchmarks/regen/timings/{label}.json` |

### Acceptable diff tolerance

| Output | Tolerance |
|--------|-----------|
| Political fill RGBA | **Exact** match on land pixels |
| Borders (5px ink) | ±1px shift acceptable if visual pass OK (document in batch PR) |
| PNG compression | Prefer compare **decoded pixels**, not file bytes |
| Skipped modes (51.06) | Fewer region files **allowed** if batch explicitly skips template-only modes — manifest must list `skipped_modes` |

### Technology choices

| Piece | Choice |
|-------|--------|
| Vectorization | **`numpy`** (add to backend requirements); no new mandatory C extension beyond Pillow |
| Optional speedups | `opencv-python-headless` only if needed for morphology borders — evaluate in 51.05 |
| Parallelism | `multiprocessing` per mode in 51.07; not before regiongen rewrite is stable |
| Instrumentation | Keep existing [`regeneration.py`](../../../backend/src/scripts/util/regeneration.py) `_RegenTimings`; extend with sub-phase labels only if needed |

### Benchmark layout

```
backend/benchmarks/regen/
  README.md
  snapshots/           # gitignored — full PNG trees
    v0-baseline/
    v1-map-paint/
    ...
  timings/
    v0-baseline.json   # committed — ms per step + total
    ...
  manifests/
    v0-baseline.json   # committed — path → sha256, bytes, mtime
```

### What to snapshot each run

Copy from `backend/src/output/main/`:

- `maps/*.png` (all mode maps + parchment + prosperity)
- `regions/{mode}/*.png` (all political modes)
- Optional: `defines/main/{nation,county,...}.json` overlay sections only

Do **not** snapshot `input/` or geometry `.bin.gz` (unchanged by mapgen).

## Root causes (locked analysis)

1. **~72% regiongen** — Python xy lists, full-canvas buffers per region, 6× full scans
2. **~24% map paint** — 6× 41M-pixel PIL loops
3. **Template world** — county/duchy/kingdom/empire process 64–255 region buckets despite sparse live factions
4. **Not** compile, parchment, or prosperity (combined &lt;3%)

## Verify

- [ ] Team agrees targets and correctness gates
- [ ] `benchmarks/regen/` layout created (51.02)
- [ ] `v0-baseline` captured before 51.03 code lands

## Status

**Planned.**

## Next

[02-baseline-snapshot](./02-baseline-snapshot.md).
