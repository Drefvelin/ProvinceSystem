# Step 70 — Per-side battle caps & initiative

**Repo:** SF · [war-build-order.md](../../war-build-order.md)  
**Depends on:** [64](../step-64/00-index.md) (schedule + trim), [65](../step-65/00-index.md) (naval slots), [62](../step-62/00-index.md) (coalition initiative)  
**Supersedes:** symmetric fuel from [64.05](../step-64/05-trim-initiative.md) (partial)  
**Next:** [66](../step-66/00-index.md) (war campaign map)

## Goal

Replace the single invasion schedule cap and symmetric initiative fuel with **per-direction battle budgets** and **asymmetric starting fuel** derived from each coalition's march length on its leg of the campaign axis.

| In scope | Out of scope |
|----------|--------------|
| Invasion leg schedule (border → objective), cap per config | Pathfinder / axis geometry changes |
| Counter leg schedule (border → aggressor capital), cap per config | Re-siege fuel recompute (stays declare-time only) |
| Per-coalition initiative at declare | New war goals |
| Dual schedule indices; counter-push uses counter leg | Map export route (66) |
| Route GUI for both legs (70.05; route row superseded by [70b.03](../step-70b/03-schedule-only-gui.md)) | Inter-battle raids (71) |
| Docs + tests (70.06) | Migrating live wars (re-declare) |

## Target behavior

```text
axis: [ atk_cap … … border(cursor) … … objective ]

invasion_leg:  border → objective   (max N battles per leg, default 4; first battle at border counts)
counter_leg:   border-1 → atk_cap   (max N battles per leg, default 4; required field at capital)

initiative_attacker = ceil(invasion_leg_slot_count × initiative_factor)
initiative_defender = ceil(counter_leg_slot_count × initiative_factor)
```

Example: invasion leg has 4 slots → attacker **6** fuel; counter leg has 2 slots → defender **3** fuel (factor 1.5).

## Batches

| Batch | Doc | Status |
|-------|-----|--------|
| **70.01** | [01-planning-lock.md](./01-planning-lock.md) | **done** (2026-08-23) |
| **70.02** | [02-counter-leg-builder.md](./02-counter-leg-builder.md) | **done** (2026-08-23) |
| **70.03** | [03-per-side-initiative.md](./03-per-side-initiative.md) | **done** (2026-08-23) |
| **70.04** | [04-counter-push-progression.md](./04-counter-push-progression.md) | **done** (2026-08-23) |
| **70.05** | [05-route-gui.md](./05-route-gui.md) | **done** (2026-08-23) |
| **70.06** | [06-docs-verify.md](./06-docs-verify.md) | **done** (2026-08-23) |

## Status

**Step 70 complete** (2026-08-23). **Follow-up:** [70b campaign schedule simplicity](../step-70b/00-index.md) **done** (2026-08-23): schedule-only route row supersedes 70.05 axis-walk entries. **Next map work:** [66 war campaign map](../step-66/00-index.md).
