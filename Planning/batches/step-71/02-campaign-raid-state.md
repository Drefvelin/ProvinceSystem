# Step 71.02 — Campaign raid state

**Depends on:** [71.01](./01-planning-lock.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-25)

## Goal

Persist campaign raid lifecycle on the war: side quota, global mutex, active raid record, repair-lock map shell.

## Shipped

1. `CampaignRaid`, `CampaignRaidState`, `CampaignRaidResults` under `War/campaign/raid`
2. `CampaignRaidData` Gson POJO; war fields `campaignRaidsUsed`, `activeCampaignRaid`, `raidRepairLockUntil`
3. `CampaignRaidService` — `canLaunch`, `beginMuster`, `transitionToFighting`, `endRaid`, `clearForNewBattleDay`, repair-lock shell
4. `war.campaign_raid` config (`muster_seconds`, `duration_seconds`, `repair_lock_hours`)
5. Hooks in `BattleScheduleService.postpone` / `skipBattleDay` and `WarManager.endWar`
6. `CampaignRaidServiceTest`, `ConfigLoaderCampaignRaidTest`, `WarMapperTest.roundTrip_campaignRaidFields`

## Files (expected)

| Area | Path |
|------|------|
| Model | `War/campaign/raid/CampaignRaid.java`, `CampaignRaidState.java` |
| Service | `War/campaign/raid/CampaignRaidService.java` |
| Mapper | `War/core/WarMapper.java` (new fields) |

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=CampaignRaidServiceTest,WarMapper*"
cd simplefactions; mvn test
```
