# Step 71.12 — Vehicle repair and berth embargo

**Depends on:** [71.09](./09-damage-repair-embargo.md)  
**Repo:** `simplefactions` + `vehicleframework`  
**Status:** done (2026-08-25)

## Goal

Berthed vehicles cannot be repaired while their installation is in any battle or raid. After a campaign raid, the **target** keeps a 48h vehicle repair + berth lock. Personal-to-installation berth is blocked for those installations.

## Tasks

1. VF `VehicleRepairStartEvent` (cancellable) fired from `RepairManager.repair` before GUI.
2. `VehicleInstallationLockService.isVehicleLocked`: vulnerable (in raid/battle) **or** 48h target `isRepairLocked`.
3. `VehicleRepairEmbargoListener`: cancel repair for `INSTALLATION` registry rows when locked.
4. `InstallationVehicleService.canRegister` + `/faction transfervehicle`: `REPAIR_LOCKED` / do not arm session.
5. Tests: lock predicate; canRegister; messages; listener.

## Verify

```powershell
cd vehicleframework; mvn test
cd simplefactions; mvn test "-Dtest=VehicleInstallationLock*,InstallationVehicleServiceTest,VehicleTransferMessagesTest,VehicleRepairEmbargoListenerTest,InstallationRepairEmbargo*"
cd simplefactions; mvn test
```
