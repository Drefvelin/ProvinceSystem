# Step 59.03 — Vote tally services

**Step:** 59 · **Repo:** SF  
**Spec:** [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

Pure battle-schedule services: valid window hours, vote recording/tally, hour pick (`min` rule), and quorum check. No GUI, scheduler tick, postpone wiring, or admin commands (59.04+).

## Scope

- [x] `BattleWindowService` - valid hours, `computeScheduledBattleAt` (hour 24 -> next-day midnight UTC)
- [x] `BattleSideMembers` - participating factions, eligible member roster, `resolveSide`
- [x] `BattleVoteService` - toggle votes, per-hour tally, `pickHour`
- [x] `BattleQuorumService` + `QuorumResult` - `min_players` OR smallest-side-full
- [x] Unit tests (3 test classes)
- [x] `mvn test` green (111 tests)

## Out of scope (59.04+)

- `BattleScheduleService` orchestration, postpone, phase transitions
- Setting `scheduledBattleProvinceId` at vote close
- Campaign GUI hour toggles
- Scheduler tick, declare hook, `/faction warschedule`
- `dev_min_players` runtime override (test servers set `min_players: 1` in config)

## Services

| Class | Role |
|-------|------|
| `War/schedule/BattleWindowService.java` | `listValidHours`, `isValidHour`, `computeScheduledBattleAt` |
| `War/schedule/BattleSideMembers.java` | Roster helpers for vote + quorum |
| `War/schedule/BattleVoteService.java` | `toggleVote`, `buildHourTally`, `pickHour` |
| `War/schedule/BattleQuorumService.java` | `meetsQuorum`, `isSmallestSideFullyRepresented` |
| `War/schedule/BattleHourTally.java` | Per-hour `{attackerCount, defenderCount}` |
| `War/schedule/QuorumResult.java` | Quorum debug record |
| `War/schedule/BattleVoteToggleResult.java` | Toggle outcome enum |

### Hour pick

For each valid hour H: score = `min(attacker(H), defender(H))`. Pick max score; tie -> earliest hour. Ignore out-of-window stored hours.

### Quorum

```text
passMin = distinctVoters >= min_players
passSmallest = require_smallest_side_full && smallestSideFullyRepresented
passed = pass_if_either ? (passMin || passSmallest) : (passMin && passSmallest)
```

Smallest-side-full: side with fewer eligible members; every roster name must map to a UUID in `battleVotes` with a non-empty hour set.

### Side resolution (tests vs production)

Services accept injectable lookups:

- `Function<UUID, Faction> uuidToFaction` for tally/pick (production: resolve via online player + `FactionManager.getByMember`)
- `Function<String, UUID> memberNameToUuid` for quorum (production: online players + existing vote keys)

## Tests

| Test | Cases |
|------|-------|
| `BattleWindowServiceTest` | 20-24 window, hour 20 vs 24 instant math, invalid hour |
| `BattleVoteServiceTest` | Toggle add/remove, reject offline/non-participant/invalid hour, min-rule + tie, ignore stale hours |
| `BattleQuorumServiceTest` | Pass via min_players, pass via smallest-side-full, fail both, `pass_if_either: false`, called ally roster |

## Status

**Done** (2026-08-20). **Next batch:** [59.04 schedule orchestration](./04-schedule-orchestration.md) (**done**). See [59.05 Campaign GUI](./05-campaign-gui.md) (TBD).
