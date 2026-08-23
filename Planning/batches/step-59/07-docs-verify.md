# Step 59.07 — Docs verify

**Step:** 59 · **Repo:** SF + Planning

## Goal

Close step 59 with tests, manual checklist, and hub doc updates.

## Tests

```bash
cd simplefactions
mvn -q test
mvn -q package
```

**Result (2026-08-20):** `mvn test` — **145 tests**, 0 failures. `mvn package` — **pass**.

### Step 59 unit tests

| Class | Cases | Covers |
|-------|-------|--------|
| `BattleSchedulePhaseTest` | 4 | Phase enum JSON round-trip |
| `BattleWindowServiceTest` | 5 | Valid hours, `computeScheduledBattleAt` (hour 24 = next-day midnight) |
| `BattleVoteServiceTest` | 6 | Toggle, `pickHour` min-rule + earliest tie |
| `BattleQuorumServiceTest` | 8 | Min players, smallest-side-full, `pass_if_either`, `dev_min_players` override |
| `BattleScheduleServiceTest` | 12 | Close/postpone/autoresolve, defender auto-Hold, admin close flags |
| `BattleScheduleTickServiceTest` | 5 | UTC hour gate, deadline at 12, close at 16, catch-up |
| `WarScheduleAdminServiceTest` | 8 | All `warschedule` subcommands |
| `BattleVoterEligibilityTest` | 4 | Voter gate, hour slot layout (28-32), autoresolve gate |
| `CampaignScheduleInfoTest` | 2 | Info book schedule lines |
| `ConfigLoaderBattleScheduleTest` | 3 | Hour order validation, `dev_min_players` key presence |
| `WarMapperTest` | 2 | Schedule field serialization incl. `forceQuorumNextClose` |
| `WarDataRoundTripTest` | 1 | Schedule fields incl. `defenderChoiceResolved` |
| `WarPersistenceFileTest` | 1 | File round-trip schedule fields |
| `WarCampaignServiceTest` | 6 | Full axis + `initScheduleState` at declare (`VOTING`, `battleDay+1`, empty votes) |
| `WarDebugFormatterTest` | 4 | `warstatus` JSON schedule fields |

### Step 58 carry-over (still in suite)

- [x] `CampaignProgressionServiceTest` — 16 cases
- [x] `OccupationServiceTest` — 12 cases
- [x] `WhitePeaceServiceTest` — 6 cases
- [x] `CampaignRouteRendererTest` — 6 cases
- [x] `WarManagerCampaignTest` — 6 cases
- [x] `ProvincePathfinderTest`, `ObjectiveProvincePickerTest`, `WarGoalValidatorTest`, etc.

## Manual checklist (staging verify)

Run on a test server before production declare codes (step 68).

Prerequisites: `war.require_declare_code: false`, admin permission for war commands, active test war, optional shortened `war.battle_schedule.*` hours and `war.battle_voting.dev_min_players: 1` per [DEV-SHORTCUTS.md](../../DEV-SHORTCUTS.md).

- [ ] **Declare** - `/faction warstatus <id>` shows `battleSchedulePhase: voting`, `battleDay` = declare UTC date +1, empty `battleVotes`
- [ ] **Restart** - `war_{id}.json` retains schedule fields (phase, day, votes map, autoresolve flags, `postponementsThisCycle`, `defenderChoiceResolved`, `forceQuorumNextClose`)
- [ ] **Campaign GUI** - slots 28-32 hour toggles during `VOTING`; info book shows battle day / vote close / selections; slots 49-51 autoresolve propose when eligible
- [ ] **Player vote** - eligible online member toggles hour; persist + reopen GUI shows selection
- [ ] **Defender deadline** - attacker initiative 0 and two nodes: no click by `defender_choice_deadline_hour` Zulu -> auto Hold (`defenderChoiceResolved: true` in `warstatus`)
- [ ] **Vote close** - at `vote_close_hour` on battle day: quorum ok -> `SCHEDULED` + `scheduledBattleAt` / `scheduledBattleHour` / `scheduledBattleProvinceId`; fail -> postpone (`battleDay+1`, votes persist, `postponementsThisCycle`++)
- [ ] **Autoresolve** - both leaders propose -> close sets `AUTORESOLVE_PENDING` (Step 60 executes fight)
- [ ] **Admin `warschedule`** - smoke: `opencvote`, `castvote`, `forcequorum`, `closevote`, `skipday`, `setscheduled`; confirm persist + JSON dump
- [ ] **Legacy war** - old JSON without schedule fields loads with `IDLE` / empty defaults (no crash)

**Out of scope for staging:** battle start at scheduled hour (Step **60**).

## Post-59 follow-up

- [ ] Battle runtime from `SCHEDULED` / `AUTORESOLVE_PENDING` - Step **60**
- [ ] Map `wars[]` export - Step **67**
- [ ] Declare codes + remove `warschedule` / `dev_min_players` before prod - Step **68**

## Docs

- [x] [Wars.md](../../../../simplefactions/Documentation/Wars.md) - step 59 shipped in build order banner + scheduling section
- [x] [war-build-order.md](../../war-build-order.md) - step 59 status
- [x] [08-implementation-checklist.md](../../08-implementation-checklist.md) - M7 step 59 batches
- [x] [01-current-state.md](../../01-current-state.md) - step 59 done, next 60

## Status

**Done** (2026-08-20). **Next step:** [60 - Warbands merge & battle runtime](../step-60/00-index.md).
