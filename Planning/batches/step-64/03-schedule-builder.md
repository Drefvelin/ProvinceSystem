# Step 64.03 — Battle schedule builder

**Repos:** `Workspace/simplefactions`  
**Depends on:** [64.02 slot model](./02-slot-model.md)  
**Touches:** `WarCampaignService`, new `CampaignScheduleBuilder`, `ZocRealm`, installation registry

## Goal

At war declare, scan the campaign axis and produce the **natural** (pre-trim) battle slot list.

## Scope

### `CampaignScheduleBuilder`

```text
build(war, axis, borderStartIndex, objectiveIndex) -> List<ScheduledCampaignBattle>
```

1. Iterate axis provinces from `borderStartIndex` toward `objectiveIndex` (inclusive of objective).
2. For each province:
   - Resolve protecting fort via ZOC overlap (oldest fort wins).
   - If fort exists and `fortControllers` (at declare: owner coalition) is **defender** → insert **siege** at fort province if not already scheduled for that `fortInstallationId`.
   - If cadence matches (`provinces_between_battles`) → insert **field** at province (dedupe same province).
3. Append **required field** at objective if not already present.

### Fort lookup helper

- `FortZocIndex` or static helper: given all operational forts, map province → winning fort installation id.
- Reuse `ZocRealm.computeZocProvinces` per fort; sort forts by age for overlap resolution.

### Wire declare

- `WarCampaignService.populateCampaign` calls builder after axis is set.
- Store natural list temporarily or pass directly to trimmer in 64.05 (builder may return natural; trimmer in 64.05).

## Tasks

1. Implement fort ZOC index + oldest-fort-wins overlap.
2. Implement axis walk + cadence + siege insertion + dedupe.
3. Unit tests with mocked axis and 1–2 forts (no full pathfinder needed).
4. Integration test: declare war on test map with fort on route → schedule contains siege slot.

## Out of scope

- Trim (64.05)
- Fort controller updates (64.04 init only: all forts → defender at end of this batch or start of 64.04)
- `nextBattleProvince` switch (64.06)

## Done when

Declare populates `campaignBattleSchedule` (natural or trimmed per 64.05 wiring) on test wars crossing fort ZOC.
