# Step 57 — Pathfinder & campaign

**Repo:** SF · **Spec:** [Wars.md](../../../../simplefactions/Documentation/Wars.md) · [war-build-order.md](../../war-build-order.md)  
**Depends on:** [56](../step-56/00-index.md) · **Next:** [58](../step-58/00-index.md)

## Goal

`ProvincePathfinder`, border-first campaign start, route priority (land → sea → land+neutral), campaign polyline, objective province selection.

## Locked (from step 56 carry-over)

| Removed in 56 | Replacement |
|---------------|-------------|
| War GUI **Switch sides** (independence rebellion) | Subject rebellion via **movement system** only |

War participants: main attacker/defender, auto subjects, ally call-to-arms. No mid-war side switching.

## Batches

| Batch | Summary | Status |
|-------|---------|--------|
| [57.01 planning lock](./01-planning-lock.md) | Pathfinder inputs/outputs, three-pass rules, WATER vs SEA, neutral, border start, Step B v1 | **done** (2026-08-20) |
| [57.02 `ProvincePathfinder`](./02-pathfinder.md) | Graph + Dijkstra, land/sea/neutral routing | **done** (2026-08-20) |
| [57.03 campaign line](./03-campaign-line.md) | Polyline storage on `War`, objective province pick | **done** (2026-08-20) |
| [57.04 integration](./04-integration.md) | Declare hook, `/faction warpath`, persist | **done** (2026-08-20) |
| [57.05 docs verify](./05-docs-verify.md) | Tests + staging checklist | **done** (2026-08-20) |

## Status

**Step 57 complete** (2026-08-20). **Next build:** [58 — Initiative & occupation](../step-58/00-index.md).
