# Map regeneration benchmarks

Compare `fullregen` output and timings across Step 51 optimization checkpoints.

## Layout

```
regen/
  README.md           # this file
  snapshots/          # gitignored — full PNG trees per label
    v0-baseline/
    v1-map-paint/
    ...
  timings/            # committed — JSON from _RegenTimings
    v0-baseline.json
  manifests/          # committed — path → sha256 per snapshot
    v0-baseline.json
```

## Labels (Step 51)

| Label | Pipeline stage |
|-------|----------------|
| `v0-baseline` | Pre-optimization (PIL pixel loops) |
| `v1-map-paint` | Numpy LUT `create_map` (−70% map paint, −18% total regen) |
| `v2-geometry-cache` | Shared province arrays + province-id LUT (−91% map paint, −31% total regen) |
| `v3-regiongen` | Numpy mask/crop regiongen (−44% region sum, −42% total regen) |
| `v4-skip-templates` | ~~Skip empty title modes~~ **cancelled** |
| `v5-parallel` | Parallel per-mode workers (`REGEN_PARALLEL_MODES=4`) |

## Commands

```bash
cd ProvinceSystem/backend/src
$env:PYTHONIOENCODING="utf-8"

# Snapshot only — use when output/{map}/ is already fresh (baseline capture)
python -m scripts.benchmarks.snapshot_regen --map main --label v0-baseline

# Compare two checkpoints
python -m scripts.benchmarks.compare_regen_snapshot --map main --a v3-regiongen --b v5-parallel --pixels

# Parallel fullregen (set worker count)
$env:REGEN_PARALLEL_MODES="4"
python -m scripts.benchmarks.run_benchmark_regen --map main --label v5-parallel
```

Do **not** use `run_benchmark_regen` to capture `v0-baseline`. The baseline was snapshotted from existing 50.04 output without re-running `fullregen`.

## What gets compared

- `output/main/maps/*.png`
- `output/main/regions/{mode}/*.png`
- Timing steps from [`regeneration.py`](../../src/scripts/util/regeneration.py)

Commit **manifests** and **timings** only. Keep **snapshots** local (large).

## Baseline reference (2026-08-16)

| Label | Total | Map paint (6 modes) | Notes |
|-------|-------|---------------------|-------|
| `v0-baseline` | 1310788 ms | 309406 ms | PIL pixel loops |
| `v1-map-paint` | 1075535 ms | 94319 ms | Numpy LUT; pixel-identical to v0 |
| `v2-geometry-cache` | 737159 ms | 8447 ms | Province-id LUT + shared cache; identical to v1 |
| `v3-regiongen` | 430994 ms | 8447 ms | Numpy mask/crop regiongen; identical to v2 |
| `v5-parallel` | 326175 ms | 8447 ms | 4 workers (`REGEN_PARALLEL_MODES=4`); identical to v3 |

- Map: `main` (Adavaar 6400²)
- Top wall-clock bottleneck after v5: county + duchy + kingdom regions (parallel; critical path ~245s)
- **Env:** `REGEN_PARALLEL_MODES=4` enables parallel mode workers; `REGEN_SERIAL_MODES=1` forces serial. Each worker loads its own geometry cache (~4× RAM vs serial).
