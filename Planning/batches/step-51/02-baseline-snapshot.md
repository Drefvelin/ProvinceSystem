# Step 51.02 — Baseline snapshot + harness

**Repos:** `ProvinceSystem` backend  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Goal

Capture **`v0-baseline`** from the **current** (pre-optimization) pipeline and add scripts to snapshot, compare, and record timings for every later batch.

## Build

| Path | Action |
|------|--------|
| [`backend/benchmarks/regen/README.md`](../../../backend/benchmarks/regen/README.md) | **Add** — layout, commands, labels |
| [`backend/benchmarks/regen/timings/.gitkeep`](../../../backend/benchmarks/regen/timings/.gitkeep) | **Add** |
| [`backend/benchmarks/regen/manifests/.gitkeep`](../../../backend/benchmarks/regen/manifests/.gitkeep) | **Add** |
| [`backend/src/scripts/benchmarks/snapshot_regen.py`](../../../backend/src/scripts/benchmarks/snapshot_regen.py) | **Add** — copy `output/{map}` → `benchmarks/regen/snapshots/{label}/` + write manifest |
| [`backend/src/scripts/benchmarks/compare_regen_snapshot.py`](../../../backend/src/scripts/benchmarks/compare_regen_snapshot.py) | **Add** — manifest diff + optional per-pixel PNG compare |
| [`backend/src/scripts/benchmarks/run_benchmark_regen.py`](../../../backend/src/scripts/benchmarks/run_benchmark_regen.py) | **Add** — run `fullregen`, write timing JSON, call snapshot (**post-optimization only**) |
| [`.gitignore`](../../../.gitignore) | **Add** `/backend/benchmarks/regen/snapshots/` |

### `snapshot_regen.py` behaviour

```bash
cd ProvinceSystem/backend/src
python -m scripts.benchmarks.snapshot_regen --map main --label v0-baseline
```

- Recursively hash every file under `output/main/maps/` and `output/main/regions/`
- Write `benchmarks/regen/manifests/{label}.json`
- Copy tree to `benchmarks/regen/snapshots/{label}/` (local only)

### `compare_regen_snapshot.py` behaviour

```bash
python -m scripts.benchmarks.compare_regen_snapshot --map main --a v0-baseline --b v1-map-paint
```

Report:

- Files added / removed / size changed
- SHA256 mismatches
- Optional `--pixels` — decode PNG pairs, report max channel delta and mismatch count

### `run_benchmark_regen.py` behaviour

```bash
python -m scripts.benchmarks.run_benchmark_regen --map main --label v1-map-paint
```

1. Run `_sync_regeneration(map, 'fullregen')`
2. Write `_RegenTimings.to_dict()` → `benchmarks/regen/timings/{label}.json`
3. Call `snapshot_regen` with same label

**Post-optimization only.** Do not use for `v0-baseline` — output was already fresh from 50.04.

## Operator steps (baseline capture)

`output/main/` was already fresh from 50.04. Baseline captured **without** re-running `fullregen`:

```bash
cd ProvinceSystem/backend/src
$env:PYTHONIOENCODING="utf-8"
python -m scripts.benchmarks.snapshot_regen --map main --label v0-baseline --notes "Pre-step-51 pipeline; from 50.04 output"
```

Committed artifacts:

- `manifests/v0-baseline.json` — 214 files (10 maps, 204 regions)
- `timings/v0-baseline.json` — seeded from instrumented run 603856 (1310788 ms total)

## Verify

- [x] `v0-baseline` manifest lists all expected `maps/*.png` (10) and `regions/{mode}/*.png` (204)
- [x] `timings/v0-baseline.json` matches last `_RegenTimings` summary
- [x] `compare_regen_snapshot --a v0-baseline --b v0-baseline` reports identical
- [x] Snapshots folder gitignored; manifests/timings tracked

## Status

**Done** (2026-08-16).

## Next

[03-vectorize-map-paint](./03-vectorize-map-paint.md).
