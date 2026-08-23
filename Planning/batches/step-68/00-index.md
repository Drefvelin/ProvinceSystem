# Step 68 — War map export (full)

**Repo:** SF · [war-build-order.md](../../war-build-order.md)  
**Depends on:** [58](../step-58/00-index.md)–[63](../step-63/00-index.md), [66](../step-66/00-index.md) (route + battle pins) · **Next:** [44](../step-44/00-index.md) (PS occupation tint)

## Goal

Extend `wars[]` in `map_markers` upload beyond the step 66 route slice: **occupation** (`occupied_by_*`), initiative display fields, belligerent chronicle hooks, and any remaining war metadata for the full web map layer.

| Step 66 (done first) | Step 68 (this step) |
|----------------------|---------------------|
| Campaign axis line + battle schedule pins | Occupation province lists |
| Capital endpoints, dual schedules | Chronicle `events[]` / war lifecycle payloads |
| Smooth route visualization | Full parity with [Wars.md](../../../../simplefactions/Documentation/Wars.md) map contract |

## Status

**Planned** - route visualization **shipped in step 66** (2026-08-23). Occupation lists, chronicle hooks, and remaining `wars[]` fields remain for this step.
