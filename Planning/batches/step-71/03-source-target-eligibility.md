# Step 71.03 — Source & target eligibility

**Depends on:** [71.02](./02-campaign-raid-state.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-25)

## Goal

Validate campaign raid source and target installations per [71.01](./01-planning-lock.md). **Supersedes** committed-pick filtering from [78.07](../step-78/07-raid-target-filter.md) for campaign raids only.

## Tasks

1. `CampaignRaidEligibilityService`:
   - `listValidSources(war, factionId, now)` — own operational port/airport.
   - `listValidTargets(war, attackerFactionId, sourceInstallationId, now)` — enemy operational installations matching `RaidKind` derived from source/target kinds.
   - `validateLaunch(war, launcherFactionId, sourceId, targetId, now)` — window, quota, mutex, ownership, kinds.
2. Deprecate or branch `RaidTargetService`: campaign raid GUI calls **eligibility** service; keep `RaidTargetService` tests updated or migrate to new tests.
3. `RaidKind` inference: port→port `NAVAL`, airport→airport `AIR`, port/airport→fort `FORT`.
4. Unit tests: uncommitted enemy fort targetable; own uncommitted port valid source; cross-kind rejected; off-window rejected.

## Note

78 installation picks remain authoritative for **battle vehicle in-play** (`BattleInstallationInPlayService`), not raid targets.

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=CampaignRaidEligibilityServiceTest,RaidTargetServiceTest"
cd simplefactions; mvn test
```
