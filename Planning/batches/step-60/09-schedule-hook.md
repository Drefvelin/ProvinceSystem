# Step 60.09 — Schedule hook (campaign battle launch)

**Repo:** SF · [00-index.md](./00-index.md) · **Depends on:** [60.08](./08-raid-runtime.md) · **Next:** [60.10 docs verify](./10-docs-verify.md)

## Goal

Wire step **59** schedule phases to step **60.06-60.08** battle runtime: create campaign battles at schedule time, open join window until fight start, auto-start at `scheduledBattleAt`, apply step **58** progression on end, then reopen voting.

## Launch flow

| Phase | Action |
|-------|--------|
| `SCHEDULED` | `CampaignBattleLaunchService.prepareScheduledBattle` on vote close / admin `setscheduled` |
| Join window | `/battle join campaign_w{id}_p{prov} attacker\|defender` until `scheduledBattleAt` |
| Start | `BattleScheduleTickService` calls `tryStartScheduledBattle` every minute when `now >= scheduledBattleAt` |
| `AUTORESOLVE_PENDING` | `launchAutoresolveBattle` creates battle and calls `battle.start()` immediately |

### Battle creation

1. Resolve province from `scheduledBattleProvinceId` (fallback `BattleScheduleService.resolveScheduledProvinceId`)
2. Battle id: `campaign_w{warId}_p{provinceId}`
3. `BattleFactory.createBlank(FIELD, id)` + `applyCampaignDefault`
4. Set `warId`, `provinceId`, unlocked, teleport enabled
5. `CampaignBattleRosterService.enrollWarbands` auto-joins faction warbands (WarView slot 13 pattern)
6. Broadcast join message to online war participants

Idempotent: existing battle for war id is reused.

## Outcome flow

`CampaignBattleOutcomeService` listens to `BattleEndedEvent`:

| Condition | Action |
|-----------|--------|
| `warId == null` | Skip (manual staff battles) |
| Winner present | `CampaignProgressionService.applyFoughtBattleOutcome`, `OccupationService.applyBattleWin` |
| No winner | Skip progression/occupation |
| Always | `BattleScheduleService.openVote`, remove battle from `BattleManager`, persist war, broadcast result |

Casualty/regiment apply stays step **61**. Fort ZOC siege type stays step **63**. Raid war battles stay step **66**.

## Components

| Class | Role |
|-------|------|
| `CampaignBattleTypeResolver` | FIELD default for 60.09 |
| `CampaignBattleLaunchService` | prepare / autoresolve / scheduled start |
| `CampaignBattleRosterService` | Auto-enroll warbands |
| `CampaignBattleOutcomeService` | Post-battle campaign apply |
| `BattleManager.getByWarId` | Idempotent launch guard |

## Integration hooks

- `BattleScheduleService.scheduleFromVotes` / `applyScheduledInstant`
- `BattleAutoresolveService.acceptRequest`
- `BattleScheduleTickService.tick` (scheduled start every poll; vote close still hour-gated)
- `SimpleFactions.registerListeners` registers outcome listener

## Manual staging checklist

1. Active war with route: vote closes with quorum -> phase `SCHEDULED`, battle created, join message broadcast
2. `/battle join campaign_w{id}_p{prov} attacker` works before fight time
3. At `scheduledBattleAt` (or `warschedule setscheduled` + wait/tick) -> battle starts, 60.06-60.08 runtime applies
4. Autoresolve accept -> battle starts immediately
5. Fight to completion -> cursor/initiative/occupation update; phase returns to `VOTING`
6. Manual `/battle create` battles (no `warId`) do not touch campaign state on end

## Out of scope

| Item | Batch |
|------|-------|
| Fort ZOC -> siege mode | 63 |
| Raid war campaign battles | 66 |
| Regiment casualties | 61 |
| War goal / reparations apply | 62 |
| Full 60.10 staging pass | 60.10 |
