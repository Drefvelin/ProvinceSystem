# Step 71.06 — Raid warbands

**Depends on:** [71.05](./05-muster-join-command.md)  
**Repo:** `simplefactions`  
**Status:** done

## Goal

Ephemeral attacker/defender raid warbands; leader promotion rules; defender auto-enroll.

## Tasks

1. `CampaignRaidWarbandService.createRaidWarbands(raid)` — ids `campaign_raid_<warId>_<battleDay>_atk|def`.
2. Muster joins add players to **attacker** raid warband; apply 61c leader rules on first join.
3. At fight start: auto-add **online** defender coalition players not in any warband to **defender** raid warband.
4. `PlayerJoinEvent` (or login): if active raid in `FIGHTING` and player on defender coalition and warband-free → add to defender raid warband.
5. On raid end: remove ephemeral warbands from `WarbandManager`; persist cleanup.
6. Leader disconnect during muster: promote next joiner per `CampaignWarbandSignupService` rules.
7. Unit tests: auto-add online defenders; login adds defender; warband deleted on end.

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=CampaignRaidWarband*"
cd simplefactions; mvn test
```
