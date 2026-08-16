# Step 51.08 — Docs verify + benchmark close-out

**Repos:** Planning + `ProvinceSystem`  
**Depends on:** [02](./02-baseline-snapshot.md)–[07](./07-parallel-modes.md)

## Goal

Close Step 51 with a **before/after benchmark table**, STAGING operator notes, and locked final snapshot label.

## Docs to update

| File | Action |
|------|--------|
| [step-51/00-index.md](./00-index.md) | All batches **done**; final timings |
| [batches/README.md](../README.md) | step-51 row |
| [STAGING.md](../../../STAGING.md) | Regen benchmark commands; expected durations |
| [09-map-system.md](../../09-map-system.md) | Note optimized pipeline; `REGEN_*` env vars |
| [04-regen-main.md](../step-50/04-regen-main.md) | Link to 51 for performance expectations |

## Final benchmark table (fill on completion)

| Label | Total (s) | vs baseline | Notes |
|-------|-----------|-------------|-------|
| `v0-baseline` | ~1311 | — | PIL loops |
| `v1-map-paint` | | | numpy create_map |
| `v2-geometry-cache` | | | shared id map |
| `v3-regiongen` | | | numpy regiongen |
| `v4-skip-templates` | | | sparse mode skip |
| `v5-parallel` | | | optional |

Artifacts: [`backend/benchmarks/regen/timings/`](../../../backend/benchmarks/regen/timings/) · [`manifests/`](../../../backend/benchmarks/regen/manifests/)

## Automated verify

```bash
cd ProvinceSystem/backend/src
python -m unittest discover -s scripts/mapgen -p "test_*.py" -v
python -m unittest src.api.test_map_access -v
python -m scripts.map_tools.test_province_geometry
python -m scripts.benchmarks.compare_regen_snapshot --map main --a v0-baseline --b v5-parallel --pixels
```

## STAGING checklist

- [ ] `fullregen main` completes under **7 min** (target; **3 min** stretch with parallel)
- [ ] Timing summary printed at end of every regen
- [ ] `v0-baseline` manifest committed for regression compares
- [ ] Operator knows how to refresh baseline after intentional visual changes

## Status

**Planned.**

## Next

Step 50.05 (cutover registry) or Step 43 forts — independent tracks.
