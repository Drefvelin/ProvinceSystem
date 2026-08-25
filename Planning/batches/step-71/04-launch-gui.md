# Step 71.04 — Launch GUI

**Depends on:** [71.03](./03-source-target-eligibility.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-25)

## Goal

Campaign view **Start raid** entry and two-page picker: source installations → target installations.

## Tasks

1. Campaign view button (slot TBD; disabled when outside call window, side quota spent, or global mutex).
2. `CampaignRaidLaunchView` (or extend `CampaignView`): page 1 sources from `listValidSources`, page 2 targets from `listValidTargets(selectedSource)`.
3. Leader-only clicks; lore for quota / window / in-progress raid.
4. Confirm calls `CampaignRaidService.beginMuster` with selected ids.
5. `SFGUI` constant for sub-view if needed.
6. Player-facing messages from [71.01](./01-planning-lock.md) chat table.

## Verify

Manual: leader on battle day during raid window sees sources/targets; non-leader blocked.

```powershell
cd simplefactions; mvn test
```
