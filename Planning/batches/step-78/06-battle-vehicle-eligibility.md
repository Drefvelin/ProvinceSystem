# Step 78.06 — Battle vehicle eligibility

**Depends on:** [78.05](./05-post-lock-intel.md), [step 77](../step-77/06-berthable-helper.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Enforce step 77 battle-prep rule at campaign battle join/spawn using committed installation sets.

## Rule

```text
eligible iff NOT isBerthableType(type)
         OR (registry INSTALLATION at installationId IN committedSet(faction))
```

## Shipped

1. `BattleVehicleEligibilityService` + `BattleVehicleEligibilityResult`
2. `BattleVehicleEligibilityMessages` (player-facing deny strings)
3. `BattleVehicleEligibilityListener` on `VehiclePreInteractEvent` and `VehicleSpawnEvent`
4. Registered in `SimpleFactions.registerVehicleIntegration()`

## Tasks

1. ~~`BattleVehicleEligibilityService`~~ — done
2. ~~Hook at vehicle interact/spawn during war-linked battles~~ — done
3. ~~Deny message for ineligible berthable vehicles~~ — done
4. ~~Unit tests: train always OK; cloudskimmer at uncommitted airport denied; at committed airport OK~~ — done

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=BattleVehicleEligibilityServiceTest"
cd simplefactions; mvn test
```
