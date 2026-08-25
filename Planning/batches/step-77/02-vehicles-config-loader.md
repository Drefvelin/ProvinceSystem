# Step 77.02 — Vehicles config loader

**Depends on:** [77.01](./01-planning-lock.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Make [`vehicles.yml`](../../../../simplefactions/src/main/resources/vehicles.yml) the source of truth for personal-limit metadata. Downstream batches (77.03+) call new getters; this batch only loads and validates.

Authority: [01-planning-lock.md](./01-planning-lock.md).

## Tasks

1. Extend [`VehicleTypeConfig`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/vehicles/VehicleTypeConfig.java) with `perPersonLimit` and `ignoreLimit` + getters
2. Extend [`VehiclesConfigLoader`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/Loaders/VehiclesConfigLoader.java):
   - Root: `default-per-person` (default `1`, `>= 1`), optional `default-upkeep` (`>= 0`)
   - Per-type: `per-person` (default from root), `ignore-limit` (default `false`), `upkeep` fallback from `default-upkeep`
3. New public API: `getDefaultPerPerson`, `isKnownType`, `getPerPersonLimit`, `ignoresPersonalSlotLimit`
4. Unit tests in [`VehiclesConfigLoaderTest`](../../../../simplefactions/src/test/java/me/Plugins/SimpleFactions/Loaders/VehiclesConfigLoaderTest.java)

## Config keys

| Key | Location | Validation | Default if absent |
|-----|----------|------------|-------------------|
| `personal-slot-limit` | root | `>= 0` | `1` |
| `default-per-person` | root | `>= 1` | `1` |
| `default-upkeep` | root | `>= 0` | none (type must specify `upkeep`) |
| `upkeep` | per type | `>= 0` | `default-upkeep` if present; else fail |
| `size` | per type | `> 0` | required |
| `per-person` | per type | `>= 1` | `default-per-person` |
| `ignore-limit` | per type | bool | `false` |

## Public API

```java
int getDefaultPerPerson()
boolean isKnownType(String vehicleTypeId)
int getPerPersonLimit(String vehicleTypeId)           // default-per-person when unknown
boolean ignoresPersonalSlotLimit(String vehicleTypeId) // false when unknown
```

Unknown types: `isKnownType` returns `false`; `getPerPersonLimit` / `ignoresPersonalSlotLimit` return safe defaults so callers branch on `isKnownType` first (77.03).

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=VehiclesConfigLoaderTest"
cd simplefactions; mvn test
```

## Done when

- [x] `VehicleTypeConfig` stores `perPersonLimit` and `ignoreLimit`
- [x] Loader reads `default-per-person`, `default-upkeep`, `per-person`, `ignore-limit`
- [x] Public getters: `getDefaultPerPerson`, `getPerPersonLimit`, `ignoresPersonalSlotLimit`, `isKnownType`
- [x] `VehiclesConfigLoaderTest` covers defaults, overrides, ignore-limit, upkeep fallback, validation failures
- [x] Full `mvn test` green
- [x] [00-index](./00-index.md) updated

## Out of scope

- `VehicleSlotGuard.checkCanBuild` (77.03)
- `VehicleIntegrationListener` construction messages (77.04)
- `installations.yml` `land_vehicles` (77.05)
- `isBerthableCategory` (77.06)
- Enforcing limits at runtime
