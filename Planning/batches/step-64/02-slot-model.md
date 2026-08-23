# Step 64.02 — Campaign battle slot model

**Repos:** `Workspace/simplefactions`  
**Depends on:** [64.01 planning lock](./01-planning-lock.md)  
**Touches:** `War.java`, `WarData.java`, `WarMapper.java`, new `War/schedule/` or `War/campaign/` types

## Goal

Introduce `CampaignBattleKind` and `ScheduledCampaignBattle` with JSON persistence on `War`. No schedule building yet.

## Scope

### New types

- `CampaignBattleKind` enum: `FIELD`, `SIEGE`, `NAVAL`, `NAVAL_INVASION`
- `ScheduledCampaignBattle` record/class:
  - `provinceId`, `kind`, `required`, optional `fortInstallationId`
  - `battleType()` derived: `SIEGE` iff kind == `SIEGE`, else `FIELD`

### `War` fields

- `List<ScheduledCampaignBattle> campaignBattleSchedule` (empty default for old saves)
- `int campaignScheduleIndex` — index of next slot to fight (or derive from `campaignBattlesFought` if 1:1; lock one approach in PR)

### Persistence

- `WarMapper` / `WarData` round-trip
- Old wars without schedule: empty list; declare path will populate in 64.03

## Tasks

1. Add enum + slot type with unit tests for `battleType()` derivation.
2. Add fields to `War`, `WarData`, mapper.
3. Migration: missing schedule → empty list, index 0.

## Tests

- Serialize/deserialize war with 3 slots (field, siege with fort id, required objective).
- Old JSON without `campaignBattleSchedule` loads with empty schedule.

## Done when

Types compile, persist, and tests pass. Schedule list still unused by progression.
