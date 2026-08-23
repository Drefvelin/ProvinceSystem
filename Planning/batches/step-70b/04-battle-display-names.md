# Step 70b.04 — Battle display names & ordinals

**Repos:** `Workspace/simplefactions`  
**Depends on:** [70b.03](./03-schedule-only-gui.md)  
**Touches:** `BattleNamingService`, `CampaignCreator`, optional `ScheduledCampaignBattle` helper, tests

## Goal

GUI titles match real battle names with correct **first / second / third** ordinals per location **before** battles are fought.

## Tasks

### 1. Schedule ordinal helper

Add package-private helper (location in `BattleNamingService` or `CampaignScheduleService`):

```text
resolveScheduledOrdinal(War war, ScheduleLeg leg, int slotIndex, ScheduledCampaignBattle slot)
  → int ordinal >= 1
```

Algorithm:

```text
key = locationKey(slot)   // fort:id for siege, else province location key
fought = war.getLocationBattleCount(key)
prior  = count slots in scheduleListForLeg(war, leg)[0..slotIndex-1] with same key
return fought + prior + 1
```

### 2. `CampaignCreator.resolveRouteDisplayName`

Use helper for all slotted entries:

- Siege → `buildDisplayName(SIEGE, fortOrProvinceName, ordinal)`
- Field / naval / invasion → `buildDisplayName(slot.battleType(), locationDisplay, ordinal)`

### 3. Launch / outcome (sanity)

Confirm `BattleNamingService.applyCampaignName` at battle start still uses `locationBattleCounts + 1` so fought battle name matches what GUI showed for that slot.

### 4. Tests

- `BattleNamingServiceTest` or new `CampaignScheduleDisplayTest`:
  - Two field slots same province → `Battle of X`, `Second Battle of X`
  - Siege + field at capital → `Siege of Greenfort`, `Battle of Lanbury` (different keys)
- `CampaignRouteRendererTest` or creator test: display name on mocked item meta

## Done when

- [x] Brume GUI: `Siege of Greenfort` then `Battle of Lanbury` (not `Battle of Greenfort` on axis tile 713)
- [x] Ordinals stable across reload (derived from schedule + counts, not random)
- [x] Tests green
