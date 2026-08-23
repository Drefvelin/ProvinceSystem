# Step 64.05 — Trim & dynamic initiative

**Repos:** `Workspace/simplefactions`  
**Depends on:** [64.03 schedule builder](./03-schedule-builder.md), [64.04 fort control](./04-fort-control.md)  
**Touches:** `ConfigLoader`, `config.yml`, `Cache`, `WarCampaignService`, new `CampaignScheduleTrimmer`

## Goal

Trim natural schedule to per-goal `max_battles`. Set both coalitions' initiative fuel from **final** slot count.

## Scope

### Config

- Remove `war.initiative_per_side`
- Add `war.initiative_factor` (default `1.5`)
- Add `war.goals.<WarGoalType>.max_battles` (default `4` each)

### `CampaignScheduleTrimmer`

```text
trim(schedule, maxBattles) -> List<ScheduledCampaignBattle>
```

Drop order (first out):

1. Non-required `FIELD` (farthest from objective / tail-first — document choice in code)
2. `NAVAL_INVASION` (none in 64)
3. `NAVAL` (none in 64)
4. `SIEGE`
5. Never drop `required` objective slot

If still over max after dropping all droppable slots, keep objective + sieges + as many fields as fit (should not happen with max 4 and sane routes; log warning if so).

### Initiative

```text
fuel = (int) Math.ceil(trimmed.size() * Cache.warInitiativeFactor)
war.setInitiativeFuelAggressor(fuel)
war.setInitiativeFuelDefender(fuel)
```

Replace `Cache.warInitiativePerSide` usage at declare.

### Declare pipeline

```text
natural = CampaignScheduleBuilder.build(...)
trimmed = CampaignScheduleTrimmer.trim(natural, maxBattles(war.getGoal()))
war.setCampaignBattleSchedule(trimmed)
applyInitiativeFromSchedule(war, trimmed)
FortControlService.initializeAtDeclare(war)
```

## Tasks

1. Config + loader + remove old key.
2. Trimmer with priority tests (6 natural → 4 trimmed drops fields first).
3. Initiative formula tests.
4. Update any tests hardcoding `initiative_per_side: 4`.

## Done when

Declare sets trimmed schedule and fuel from `ceil(n * 1.5)` on representative wars.
