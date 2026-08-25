# Step 78.04 — Campaign GUI installation picks

**Depends on:** [78.03](./03-installation-pick-service.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Campaign view **Installations** button (slot 33, march icon) opens leader-only multi-select pick GUI.

## Shipped

1. `SFGUI.CAMPAIGN_INSTALLATION_PICK_VIEW`
2. `CampaignInstallationPickView` — list operational installations; click toggles commit (glint + lore)
3. `CampaignView` slot 33 entry button
4. `CampaignCreator` entry/summary/pick item builders
5. `InventoryManager` routing for pick view clicks
6. Player messages per planning lock

## UX

| State | Behavior |
|-------|----------|
| Before lock, leader | Toggle picks |
| Before lock, non-leader | Deny message |
| After lock | Read-only list + "Locked at vote close" |

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=BattleInstallationPickServiceTest"
cd simplefactions; mvn test
```
