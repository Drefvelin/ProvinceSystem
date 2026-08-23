# Step 70.03 — Per-side initiative at declare

**Repos:** `Workspace/simplefactions`  
**Depends on:** [70.02 counter leg builder](./02-counter-leg-builder.md)  
**Touches:** `WarCampaignService`, `WarData`, `WarMapper`, tests

## Goal

Replace symmetric declare-time initiative with **per-leg asymmetric fuel** and persist counter schedule fields to war JSON.

## Shipped

### Initiative at declare

`WarCampaignService.applyInitiativeFromLegs(war, invasion, counter)`:

```text
initiativeAttacker = ceil(invasion_leg_slot_count × war.initiative_factor)
initiativeDefender = ceil(counter_leg_slot_count × war.initiative_factor)
```

- `initiativeFuelForLegCount(slotCount)` public helper (empty counter → **0**; empty invasion with fallback flag → **6** for legacy mapper defaults).
- `applyInitiativeFromSchedule` deprecated; delegates with same list for both legs.

`populateCampaign` calls `applyInitiativeFromLegs` after both legs are built and trimmed.

### JSON persistence

**`WarData`**

- `campaignCounterSchedule`
- `campaignCounterScheduleIndex`

**`WarMapper`**

- `toData`: serializes counter schedule and index via existing `serializeSchedule`.
- `fromData`: deserializes counter schedule; legacy fuel defaults:

| Field missing | Default |
|---------------|---------|
| `initiativeAttacker` null | `ceil(invasionSchedule.size × factor)` (empty invasion schedule → **6**) |
| `initiativeDefender` null + `campaignCounterSchedule` **absent** (pre-70 JSON) | Same as attacker default (symmetric backward compat) |
| `initiativeDefender` null + `campaignCounterSchedule` **present** | `ceil(counterSchedule.size × factor)` (empty list → **0**) |

Persisted fuel values are not recomputed when both initiative fields are present.

## Tests

- `WarCampaignServiceTest`: `applyInitiativeFromLegs_asymmetricFuel`; fuel assertions on `populateCampaign_*`.
- `WarManagerCampaignTest`: per-leg fuel from schedule sizes on regenerate.
- `WarMapperTest`: round-trip counter schedule + asymmetric fuel; pre-70 symmetric defaults; empty counter → defender 0.
- `WarPersistenceFileTest`: file round-trip preserves counter schedule, index, and asymmetric fuel.

## Deferred (70.04+)

- `CampaignScheduleService` active-leg resolution (counter-push reads counter schedule at runtime).
- Re-siege fuel recompute.
- `Wars.md` gameplay summary (70.06).

## Done when

- [x] `applyInitiativeFromLegs` at declare with asymmetric fuel
- [x] Counter schedule + index in `WarData` / `WarMapper`
- [x] Legacy load defaults for missing counter field and fuel
- [x] Tests + planning doc
