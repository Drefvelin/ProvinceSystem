# Step 78.02 — Battle & raid schedule windows

**Depends on:** [78.01](./01-planning-lock.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Separate **raid window** (19-20 CET) from **campaign battle window** (21-24 CET) in config and services.

## Tasks

1. Add `raid_window_start_hour` / `raid_window_end_hour` under `war.battle_schedule` (defaults **19** / **20** CET).
2. Update `window_start_hour` default to **21** (`window_end_hour` stays **24**).
3. Extend `ConfigLoader` + `Cache` with raid window fields.
4. `ConfigLoader.validateBattleScheduleConfig` — ordering: `vote_close` < raid start <= raid end < battle start <= battle end.
5. New `RaidWindowService`: `listRaidHours()`, `isRaidHour(int)`.
6. `BattleScheduleService`: `isRaidWindowOpen(war, now)`, `isBattleWindowOpen(war, now)`.

**Note:** All `war.battle_schedule` hours are **Europe/Paris (CET/CEST)**, not UTC — same as existing `BattleWindowService.SCHEDULE_ZONE`.

## Config (shipped defaults)

```yaml
war:
  battle_schedule:
    vote_close_hour: 16
    raid_window_start_hour: 19
    raid_window_end_hour: 20
    window_start_hour: 21
    window_end_hour: 24
```

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=ConfigLoaderBattleScheduleTest,BattleWindowServiceTest,RaidWindowServiceTest,BattleScheduleServiceTest"
cd simplefactions; mvn test
```
