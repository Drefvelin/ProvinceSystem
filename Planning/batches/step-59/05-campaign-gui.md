# Step 59.05 — Campaign GUI hour toggles

**Step:** 59 · **Repo:** SF  
**Spec:** [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

Hour vote toggles, schedule info on the campaign book, and dual-leader autoresolve propose buttons in the existing Campaign view. Wires to [`BattleVoteService`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/schedule/BattleVoteService.java) and [`BattleScheduleService`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/schedule/BattleScheduleService.java).

## Scope

- [x] `BattleVoterEligibility` - voter/autoresolve gates + hour slot layout
- [x] `CampaignCreator` - schedule info lines, hour toggles, autoresolve items
- [x] `CampaignView` - render slots 28-32, 49-51; click handlers; persist on vote/autoresolve
- [x] Hold/counter-push **route clicks** unchanged; slot 49-50 hold/counter **buttons removed** (59.01 layout)
- [x] Unit tests + `mvn test` green (126 tests)

## Out of scope (59.06+)

- UTC hourly scheduler tick
- `/faction warschedule` admin commands
- Step 60 battle execution

## GUI layout

| Slot | Content |
|------|---------|
| 4 | Info book: initiative/phase + battle day, vote close, your hours, tally, scheduled fight |
| 28-32 | Hour toggles (lime = selected, gray = unselected; disabled when not eligible) |
| 48 | Accept white peace (58) |
| 49-50 | Attacker / defender autoresolve propose (main leaders, `VOTING` only) |
| 51 | Autoresolve status when either flag set |

## Click flow

| Action | Service | Persist |
|--------|---------|---------|
| Hour toggle | `BattleVoteService.toggleVote` | `WarManager.persist` + refresh view |
| Autoresolve propose | `BattleScheduleService.proposeAutoresolve` | `WarManager.persist` + refresh view |
| Hold / counter (route) | Unchanged confirm flow (58) | Unchanged |

Eligible voters: online member of a participating war faction while `battleSchedulePhase == VOTING`.

## Files

| File | Role |
|------|------|
| `War/schedule/BattleVoterEligibility.java` | Eligibility + slot mapping |
| `Managers/Inventory/CampaignCreator.java` | Items + `buildScheduleInfoLines` |
| `Managers/Inventory/CampaignView.java` | Render + click handlers |

## Tests

| Test | Cases |
|------|-------|
| `BattleVoterEligibilityTest` | Voter gate, hour layout, autoresolve gate |
| `CampaignScheduleInfoTest` | Info lines: battle day, vote close, selections, scheduled fight |

## Status

**Done** (2026-08-20). **Next batch:** [59.06 scheduler + warschedule](./06-scheduler-integration.md) (TBD).
