# Step 59.04 — Schedule orchestration

**Step:** 59 · **Repo:** SF  
**Spec:** [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

Orchestrate vote close, postpone, dual-leader autoresolve, and defender-choice deadline auto-Hold via `BattleScheduleService`. No scheduler tick, GUI, or admin commands (59.05-59.06).

## Scope

- [x] `defenderChoiceResolved` on `War` / `WarData` (manual hold + auto-Hold tracking)
- [x] `BattleScheduleService` + `BattleScheduleCloseResult`
- [x] `closeVote`, `postpone`, `scheduleFromVotes`, autoresolve propose/enter
- [x] `applyDefenderChoiceDeadline` (auto-Hold at configured hour)
- [x] `applyDefenderHold` sets `defenderChoiceResolved`
- [x] Unit tests + `mvn test` green (120 tests)

## Out of scope (59.05+)

- Bukkit hourly tick ([59.06](./00-index.md))
- Campaign hour toggles + autoresolve GUI ([59.05](./00-index.md))
- `/faction warschedule` ([59.06](./00-index.md))
- Step 60 battle execution from `AUTORESOLVE_PENDING`

## Close flow (`closeVote`)

Only when `battleSchedulePhase == VOTING` and UTC hour >= `vote_close_hour` on `battleDay`:

1. If defender choice needed and unresolved: try auto-Hold; if still unresolved -> `BLOCKED_DEFENDER_CHOICE`
2. If both autoresolve flags -> `AUTORESOLVE_PENDING`
3. Else if quorum met and hour picked -> `SCHEDULED` (province from `resolveNextBattleNodes`)
4. Else -> `POSTPONED` (`battleDay+1`, votes persist, `postponementsThisCycle++`)

## Postpone (locked)

- `CampaignProgressionService.applyPostponedBattle` (no initiative/cursor spend)
- Votes persist; phase stays `VOTING`
- Clears scheduled targets; resets `defenderChoiceResolved`

## Persistence

| Field | Purpose |
|-------|---------|
| `defenderChoiceResolved` | Manual hold or auto-Hold before vote close when attacker initiative = 0 |

Reset in `initScheduleState`; legacy JSON defaults `false`.

## Files

| File | Role |
|------|------|
| `War/schedule/BattleScheduleService.java` | Orchestrator |
| `War/schedule/BattleScheduleCloseResult.java` | Close outcome enum |
| `War/War.java`, `Database/WarData.java`, `WarMapper.java` | `defenderChoiceResolved` |
| `War/progression/CampaignProgressionService.java` | Hold sets flag |
| `War/campaign/WarCampaignService.java` | Reset flag on schedule init |

## Tests

| Test | Cases |
|------|-------|
| `BattleScheduleServiceTest` | Schedule, postpone, autoresolve, auto-Hold, blocked close, skipped |
| `CampaignProgressionServiceTest` | Hold sets `defenderChoiceResolved` |
| `WarMapperTest`, `WarDataRoundTripTest` | Field round-trip |

## Status

**Done** (2026-08-20). **Next batch:** [59.05 Campaign GUI hour toggles](./05-campaign-gui.md) (TBD).
