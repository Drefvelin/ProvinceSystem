# Step 71.07 — Raid battle runtime

**Depends on:** [71.06](./06-raid-warbands.md)  
**Repo:** `simplefactions`  
**Status:** done

## Goal

Start timer-only `BattleType.RAID` for campaign raids: no capture point, teleport attackers to source, defender alerts, early end if attackers eliminated.

## Tasks

1. `battle-templates.yml`: `campaign_raid_template` — `type: raid`, `defender_respawn_mode: infinite`, `keep_inventory: true`, flag `campaign_raid: true` (or dedicated field on `Battle`).
2. `CampaignRaidLaunchService.startFight(raid)`:
   - Create battle linked to `warId`; enroll atk/def raid warbands.
   - Set defender spawn/jail to **target** installation center; attacker spawn to **source** center.
   - **Do not** call `BattleRaidSetup.seedTargetPoint` for campaign raids.
   - Teleport attacker warband members to source.
   - Defender title + goat horn (`WarManager` declare-war pattern).
3. Fight timer: `duration_seconds`; on expiry `BattleEndSupport.endBattle(battle, null)` with new `BattleEndReason.TIMER` on `BattleEndedEvent`.
4. Early end: all attackers out → end with defender side id (cleanup only).
5. `CampaignBattleOutcomeService`: **ignore** campaign raid battles (no fuel/cursor/vote side effects).
6. Reuse `RaidAttackerEliminationService`, `RaidRespawnService` (defender → target center).
7. Unit tests: no capture points seeded; timer ends battle; outcome service skips raid.

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=CampaignRaidLaunch*,RaidWinServiceTest"
cd simplefactions; mvn test
```
