# Step 70.02 — Counter leg builder

**Repos:** `Workspace/simplefactions`  
**Depends on:** [70.01 planning lock](./01-planning-lock.md), [64.03 schedule builder](../step-64/03-schedule-builder.md)  
**Touches:** `CampaignScheduleBuilder`, `CampaignScheduleTrimmer`, `ConfigLoader`, `War`, `WarCampaignService`

## Goal

At declare, build and trim a **counter leg** schedule from border toward aggressor capital, independently of the invasion leg.

## Shipped

### `CampaignScheduleBuilder`

- Refactored invasion `build(...)` to internal `buildSegment(...)` with advancing coalition, cadence origin, and directional sea scan.
- New `buildCounter(war, axis, borderStartIndex, aggressorCapitalIndex, fortIndex, portIndex)`:
  - Returns empty when `borderStartIndex <= 0` or no room left of border.
  - Walks `borderIndex - 1` down to capital index (or axis start when capital not on axis).
  - Coalition-flipped siege, port, and naval invasion landing rules for `DEFENDER` advancing.
- `ensureRequiredTerminalSlot` replaces invasion-only objective helper (shared by both legs).

### Trim + config

- `CampaignScheduleTrimmer.maxBattlesPerLegForGoal(goal)`; `maxBattlesForGoal` deprecated delegate.
- `ConfigLoader` reads `max_battles_per_leg` with fallback to `max_battles`.
- `config.yml` uses `max_battles_per_leg: 4` per goal.

### Declare pipeline

`WarCampaignService.populateCampaign` builds and trims both legs; sets `campaignCounterSchedule` and `campaignCounterScheduleIndex = 0`.

Initiative remains symmetric from invasion leg only until **70.03**.

### `War` fields (in-memory)

- `campaignCounterSchedule`
- `campaignCounterScheduleIndex`

JSON persistence deferred to **70.03**.

## Tests

- `CampaignScheduleBuilderTest`: counter cadence, empty at border capital, fort siege, naval sea run, no border slot.
- `CampaignScheduleTrimmerTest`: `maxBattlesPerLegForGoal`, independent leg trim.
- `ConfigLoaderWarGoalsTest`: `max_battles_per_leg` preference over alias.
- `WarCampaignServiceTest`: `populateCampaign_buildsCounterScheduleLeftOfBorder`.

## Done when

- [x] `buildCounter` at declare with dual independent trim
- [x] Config alias loaded
- [x] `mvn test` green

**Status:** **Done** (2026-08-23).
