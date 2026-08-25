# Step 71.08 — Campaign warband signup lock

**Depends on:** [71.07](./07-raid-battle-runtime.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-25)

## Goal

Block campaign warband signup during the raid call window (19-20); allow signup 20-21 before main battle.

## Tasks

1. `CampaignWarbandSignupService.signupMember`: if war on battle day and `BattleScheduleService.isRaidWindowOpen(war, now)` → return blocked message ([71.01](./01-planning-lock.md)).
2. Optional helper `CampaignWarbandSignupService.isSignupOpen(war, now)` — true when not in raid window on battle day (or always true off battle day).
3. `/warband list` lore hint when blocked.
4. Unit tests: signup rejected at 19:xx; allowed at 20:xx on battle day.

## Note

Raid warband join (`/raid join`) remains separate and allowed during 19-20.

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=WarbandCampaignSignup*,CampaignWarbandSignup*"
cd simplefactions; mvn test
```
