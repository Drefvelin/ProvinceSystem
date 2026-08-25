# Step 76.04 — Installation berth service

**Depends on:** [76.01](./01-planning-lock.md), [76.03](./03-installation-radius-config.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Add `InstallationVehicleService` with `canRegister` / `register`, `CanRegisterResult` enum, and registry slot queries for installation vehicle berthing. Used by 76.05+ transfer command and consent flow.

Authority: [01-planning-lock.md](./01-planning-lock.md#berth-service-7604).

## Tasks

1. `CanRegisterResult` enum (8 values)
2. `PlayerVehicleRegistry.getByInstallationId` + `usedCategorySize`
3. `InstallationVehicleService.canRegister` / `register`
4. Unit tests: `InstallationVehicleServiceTest`, extended `PlayerVehicleRegistryTest`

## `CanRegisterResult`

| Value | Meaning |
|-------|---------|
| `OK` | May register |
| `NOT_IN_REGISTRY` | No SF record or uuid mismatch |
| `ALREADY_BERTHED` | Record already `INSTALLATION` mode |
| `UNKNOWN_TYPE` | Type id not in `vehicles.yml` categories |
| `UNSUPPORTED_CATEGORY` | Kind has `slots.<category>` capacity 0 or missing |
| `NO_CAPACITY` | `usedSize + vehicleSize > capacity` |
| `OUT_OF_RADIUS` | Vehicle XZ distance from installation center `> radius` |
| `WRONG_PROVINCE` | `provinceAt(vehicleLoc) != installation.getProvince()` |

Checks run in that order (early exit). Chat mapping deferred to 76.05.

## Slot accounting

`usedCategorySize(installationId, categoryId)` = sum of `VehiclesConfigLoader.getSize(typeId)` for all registry records with matching `installationId` and category.

## API

```java
InstallationVehicleService service = new InstallationVehicleService(registry);

CanRegisterResult result = service.canRegister(installation, activeVehicle, record);
service.register(installation, activeVehicle, record, faction);
```

`register` updates registry (`INSTALLATION` + `installationId`), sets VF owner via `InstallationVehicleOwnerSync` (see [01-planning-lock](./01-planning-lock.md): `player_<leaderName>`, not `faction_<id>`), calls `SimpleFactions.saveVehicleRegistry()`.

**Amendment (76.05):** 76.04 initially shipped `faction_<factionId>` in `register`; 76.05 replaces this with leader-based owner + spawn sync helper.

Package-private `VehicleBerthTarget` interface supports unit tests without mocking `ActiveVehicle`.

## Verify

```powershell
cd simplefactions; mvn test
```

Focus: `InstallationVehicleServiceTest`, `PlayerVehicleRegistryTest`.

## Done when

- [x] `CanRegisterResult` enum with all 8 values
- [x] `PlayerVehicleRegistry` exposes installation/category slot queries
- [x] `InstallationVehicleService.canRegister` enforces registry, type, capacity, radius, province
- [x] `register` updates registry + VF owner + persists
- [x] Tests green; [00-index](./00-index.md) updated

## Out of scope

- `/faction transfervehicle`, `VehicleTransferListener`, chat messages (76.05)
- `VehicleTransferConsentRequest`, `RequestManager` branch (76.06)
- `SimpleFactions` service field registration (76.05)
- Bump `pom.xml` to `vehicleframework-1.1.8` (76.05)
