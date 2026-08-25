# Step 78.09 — Pick eligibility (kind + control)

**Depends on:** [78.04](./04-campaign-gui-picks.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Limit installation picks to **ports and airports** in provinces your coalition still controls.

## Shipped

1. **`BattleInstallationPickEligibility`** — `isPickableKind`, `isUnderSideControl`, `isPickable`, `listPickableInstallations`
2. **`BattleInstallationPickService`** — reject ineligible adds in `togglePick`; `pruneIneligiblePicks` on read (`getPicks`, `getAllPicks`)
3. **`CampaignInstallationPickView`** — lists only pickable installations
4. **Tests** — `BattleInstallationPickEligibilityTest`, updated `BattleInstallationPickServiceTest`, `RaidTargetServiceTest` ownership stubs

## Rules

| Rule | Detail |
|------|--------|
| Pickable kinds | `PORT`, `AIRPORT` only |
| Territory | Province not in enemy occupation bulge AND (in our occupation OR de jure on our side) |
| Fort picks | Not pickable; legacy fort picks pruned on read; remove via toggle still works |
| Fort raids | Not via picks — step **71** will wire fort raids separately |

## Control logic

For attacker-side faction at province `P`:

- Reject if `P` in `occupiedByDefender`
- Accept if `P` in `occupiedByAttacker` or de jure attacker (`BelligerentTerritory`)

Defender-side: occupation lists swapped.

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=BattleInstallationPickEligibilityTest,BattleInstallationPickServiceTest"
cd simplefactions; mvn test
```
