# Step 78.10 — Siege fort in-play (vehicles)

**Depends on:** [78.09](./09-pick-eligibility.md), [78.06](./06-battle-vehicle-eligibility.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Static emplacements berthed at the active siege fort are battle-eligible without an installation pick.

## Shipped

1. **`BattleSiegeFortService`** — `currentSiegeFortInstallationId`, `isSiegeFortInPlay`, `isSiegeFortInPlayForFaction`
2. **`BattleInstallationInPlayService`** — `isInPlay` (committed picks OR siege fort for owner faction)
3. **`BattleVehicleEligibilityService`** — uses `isInPlay` instead of picks-only check
4. **Tests** — `BattleSiegeFortServiceTest`, `BattleInstallationInPlayServiceTest`, extended `BattleVehicleEligibilityServiceTest`

## Rules

| Source | In play for vehicles |
|--------|----------------------|
| Committed pick (port/airport) | Owner faction, current battle day |
| Active schedule `SIEGE` slot | `fortInstallationId` for owning faction |

Current slot resolved via `CampaignScheduleService.slotAtActiveIndex` (read-only).

Fort raids remain step **71** (not wired here).

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=BattleSiegeFortServiceTest,BattleInstallationInPlayServiceTest,BattleVehicleEligibilityServiceTest"
cd simplefactions; mvn test
```
