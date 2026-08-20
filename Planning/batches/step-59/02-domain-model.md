# Step 59.02 — Domain model + config

**Step:** 59 · **Repo:** SF  
**Spec:** [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

Persistence and config for battle scheduling: schedule fields on `War`, `BattleSchedulePhase`, config load + validation, `initScheduleState` at campaign populate. No vote services, GUI, or scheduler tick (59.03+).

## Scope

- [x] `BattleSchedulePhase` enum
- [x] `War` / `WarData` schedule fields + `battleVotes` map
- [x] `WarMapper` round-trip + legacy defaults (schemaVersion stays **2**)
- [x] `WarDebugFormatter` schedule JSON fields
- [x] `WarCampaignService.initScheduleState` at `populateCampaign`
- [x] Config: `war.battle_schedule.*`, `war.battle_voting.*` + hour-order validation
- [x] Unit tests + persistence round-trip fixtures

## Init at campaign populate

After `initProgressionState`, `initScheduleState` sets:

- `battleDay = UTC(startedAt) + 1 day` when `first_battle_day_after_declare: true`
- `battleSchedulePhase = VOTING`
- Clears votes, schedule targets, autoresolve flags, postponement counter

**Regen:** `/faction warpath` calls `populateCampaign` and resets schedule (same as progression reset).

**Raid wars:** skip `populateCampaign` — schedule stays `IDLE`.

## Files

| File | Role |
|------|------|
| `War/enums/BattleSchedulePhase.java` | Phase enum |
| `War/War.java` | Schedule fields |
| `Database/WarData.java` | Gson DTO |
| `War/WarMapper.java` | Round-trip + vote map serialization |
| `War/WarDebugFormatter.java` | Schedule debug JSON |
| `War/campaign/WarCampaignService.java` | `initScheduleState` |
| `resources/config.yml` | Battle schedule + voting config |
| `Cache.java`, `Loaders/ConfigLoader.java` | Load + validate |

## Tests

| Test | Cases |
|------|-------|
| `BattleSchedulePhaseTest` | JSON round-trip |
| `ConfigLoaderBattleScheduleTest` | Valid hours; invalid order throws |
| `WarMapperTest` | Schedule `toData`; legacy `fromData` defaults |
| `WarDataRoundTripTest`, `WarPersistenceFileTest` | Gson/file round-trip |
| `WarDebugFormatterTest` | Schedule keys in JSON |
| `WarCampaignServiceTest` | `VOTING`, `battleDay`, empty votes after populate |

## Out of scope (59.03+)

- `BattleWindowService`, `BattleVoteService`, `BattleQuorumService`
- Campaign hour toggles
- Scheduler tick, auto-Hold deadline
- `/faction warschedule`

## Status

**Done** (2026-08-20). **Next batch:** [59.03 vote tally](./03-vote-tally.md) (TBD).
