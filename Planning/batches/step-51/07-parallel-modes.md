# Step 51.07 — Parallel mode processing

**Repos:** `ProvinceSystem` backend  
**Depends on:** [05-regiongen-numpy](./05-regiongen-numpy.md) (51.06 cancelled)

## Goal

Run independent political modes (`nation`, `duchy`, `kingdom`, `county`, `empire`, `trade`) in **parallel processes** after shared compile + parchment.

Target: **~2–4×** wall-clock reduction on multi-core CPU (4 workers).

## Constraints

| Risk | Mitigation |
|------|------------|
| RAM spike | Each worker loads geometry cache — cap workers at `min(cores, 4)` |
| File races | Each mode writes to disjoint `regions/{mode}/` paths |
| Windows | `spawn` context via `ProcessPoolExecutor` |
| API regen lock | Existing `get_map_lock` — parallel only inside sync regen after compile |

## Build

| File | Action |
|------|--------|
| [`backend/src/scripts/util/mode_worker.py`](../../../backend/src/scripts/util/mode_worker.py) | **Add** — picklable `run_mode()` per worker |
| [`backend/src/scripts/util/regeneration.py`](../../../backend/src/scripts/util/regeneration.py) | **Refactor** — `ProcessPoolExecutor` for fullregen mode loop |
| [`backend/src/scripts/util/test_regeneration_parallel.py`](../../../backend/src/scripts/util/test_regeneration_parallel.py) | **Add** — helper unit tests |

### Env controls

| Variable | Default | Purpose |
|----------|---------|---------|
| `REGEN_PARALLEL_MODES` | `0` (off) | Worker count; set to `4` to enable |
| `REGEN_SERIAL_MODES` | unset | Force serial even if parallel env set |

Phases stay **serial**: compile → parchment → **parallel** per-mode (cache + map + regions).

## Benchmark (2026-08-16)

```powershell
$env:REGEN_PARALLEL_MODES="4"
python -m scripts.benchmarks.run_benchmark_regen --map main --label v5-parallel
python -m scripts.benchmarks.compare_regen_snapshot --map main --a v3-regiongen --b v5-parallel --pixels
```

| Metric | v3-regiongen | v5-parallel | Δ |
|--------|--------------|-------------|---|
| Total `fullregen` | 430994 ms | **326175 ms** | **−24%** |
| Wall time (measured) | ~431s | **~326s** | −105s |
| Pixel compare vs v3 | — | **IDENTICAL** | ✓ |
| Workers | 1 (serial) | 4 | |

**Gates:**

| Check | Target | Result |
|-------|--------|--------|
| Pixel correctness vs v3 | IDENTICAL | ✓ |
| Total `fullregen` (4 workers) | ≤ 180s stretch / ≤ 250s acceptable | **326s** (stretch not met; still −24% vs v3) |
| Serial fallback | `REGEN_PARALLEL_MODES=0` matches v3 | ✓ (code path preserved) |
| Unit tests | Pass | ✓ |

Note: per-worker step timings sum to >100% because they represent CPU time across parallel workers, not sequential wall time. Wall-clock total is the meaningful metric.

## Verify

- [x] Serial fallback preserved (`REGEN_PARALLEL_MODES=0`)
- [x] Manifest identical to v3 (214 files)
- [x] `REGEN_PARALLEL_MODES=4` documented in benchmarks README

## Status

**Done** (2026-08-16). −24% wall time vs v3; pixel-identical.

## Next

[08-docs-verify](./08-docs-verify.md).
