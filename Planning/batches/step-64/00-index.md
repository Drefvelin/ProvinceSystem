# Step 64 — Campaign battle schedule & fort sieges

**Repo:** SF · [war-build-order.md](../../war-build-order.md)  
**Depends on:** [63](../step-63/00-index.md), [57](../step-57/00-index.md), [60](../step-60/00-index.md) · **Next:** [65](../step-65/00-index.md) (naval & invasions)

## Goal

At war declare, build a **trimmed battle schedule** along the campaign axis: objective, field cadence, and fort ZOC sieges. Track **war-time fort control** (who holds the ZOC gate). Set **initiative fuel** from the final battle count. Show **battle kind** on the campaign GUI. Remove **battle province zone** limits.

| In scope | Out of scope (step 65) |
|----------|------------------------|
| `CampaignBattleKind` slot model + persistence | Port ZOC naval battles |
| Schedule builder (field cadence + fort ZOC sieges) | Naval invasion detection |
| War-time fort controller per installation | Naval invasion → siege override |
| Trim to per-goal `max_battles` | War ZOC export filter (`ZocRealm`) |
| Initiative = `ceil(final_count × initiative_factor)` | Coastal fort rules removal |
| `CampaignBattleTypeResolver` → FIELD / SIEGE | Per-battle installation pick |
| Campaign GUI battle kind icons & lore | |
| Remove allowed-province / leave-penalty enforcement | |

## Batches

| Batch | Doc | Status |
|-------|-----|--------|
| **64.01** | [01-planning-lock.md](./01-planning-lock.md) | **done** (2026-08-22) |
| **64.02** | [02-slot-model.md](./02-slot-model.md) | **done** (2026-08-23) |
| **64.03** | [03-schedule-builder.md](./03-schedule-builder.md) | **done** (2026-08-23) |
| **64.04** | [04-fort-control.md](./04-fort-control.md) | **done** (2026-08-23) |
| **64.05** | [05-trim-initiative.md](./05-trim-initiative.md) | **done** (2026-08-23) |
| **64.06** | [06-resolver-launch.md](./06-resolver-launch.md) | **done** (2026-08-23) |
| **64.07** | [07-campaign-gui.md](./07-campaign-gui.md) | **done** (2026-08-23) |
| **64.08** | [08-remove-battle-zones.md](./08-remove-battle-zones.md) | **done** (2026-08-23) |
| **64.09** | [09-docs-verify.md](./09-docs-verify.md) | **done** (2026-08-23) |

## Status

**Step 64 done** (2026-08-23). **Next:** [step 65 naval & invasions](../step-65/00-index.md).

## Note on build order

Step 64 was previously "Forts & sieges" only. Naval gates and naval invasion move to [step 65](../step-65/00-index.md). Step 64 now covers the shared **schedule + fort siege** foundation both land and naval paths depend on.
