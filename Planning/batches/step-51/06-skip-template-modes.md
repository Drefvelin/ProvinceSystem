# Step 51.06 — Skip template-only modes on fullregen

**Repos:** `ProvinceSystem` backend  
**Depends on:** [05-regiongen-numpy](./05-regiongen-numpy.md)

## Goal

On Adavaar today, **county/duchy/kingdom/empire** still process hundreds of **world-template** title buckets (placeholder RGBs) while live play only has **Lantan** at nation level. Skip modes that have **no queued entries and no live-owned provinces** on `fullregen`, or add explicit `fullregen_modes` config.

Target: further **30–50%** cut when sparse (empire scans 255 buckets today).

## Locked rules (proposed — confirm in implementation)

| Rule | Choice |
|------|--------|
| Default `fullregen` | Still generates **nation** + **trade** always |
| Title modes | Generate only if `defines/{map}/queue.json` has entries for that mode **OR** at least one province maps to non-null non-black color |
| Empty empire | Skip if all provinces map to `(0,0,0)` |
| Override | Env `REGEN_FULL_ALL_MODES=1` or API flag restores old behaviour |
| Frontend | Toolbar modes hidden already per map — no FE change if mode PNG absent |

## Build

| File | Action |
|------|--------|
| [`backend/src/scripts/util/regeneration.py`](../../../backend/src/scripts/util/regeneration.py) | Mode skip logic + log skipped modes |
| [`backend/src/scripts/benchmarks/compare_regen_snapshot.py`](../../../backend/src/scripts/benchmarks/compare_regen_snapshot.py) | Support `skipped_modes` in manifest metadata |
| Planning / STAGING | Document operator `REGEN_FULL_ALL_MODES` |

### Alternative (stricter)

Only regen modes listed in `input/{map}/queue.json` even for `fullregen` — matches incremental regen semantics. **Product decision:** nation map must always exist for public `/map/main`.

## Benchmark

```bash
python -m scripts.benchmarks.run_benchmark_regen --map main --label v4-skip-templates
python -m scripts.benchmarks.compare_regen_snapshot --map main --a v3-regiongen --b v4-skip-templates
```

Compare **nation + trade** subsets with `--pixels`; expect fewer files under `regions/empire/` etc.

**Gate:** total ≤ **300s**; nation/trade outputs unchanged vs `v3-regiongen`.

## Verify

- [ ] `fullregen` skips empire/duchy/kingdom/county when template-only (log lines)
- [ ] Nation + trade PNGs still match
- [ ] `GET /main/mapdata/nation` 200
- [ ] `REGEN_FULL_ALL_MODES=1` reproduces `v3-regiongen` file set

## Status

**Cancelled** (2026-08-16). Product decision: `fullregen` must regenerate all modes; skipping title layers is not acceptable. Proceed to [07-parallel-modes](./07-parallel-modes.md).
