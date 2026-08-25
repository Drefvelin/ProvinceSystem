# Step 77.05 — Fort land berths

**Depends on:** [77.02](./02-vehicles-config-loader.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Add `land_vehicles: 2` to fort installation slots so land vehicles can berth at forts. Capacity uses existing size-sum rules from step 76.

Authority: [01-planning-lock.md](./01-planning-lock.md#config-lock-installationsyml-amendment-7705).

## Tasks

1. Shipped [`installations.yml`](../../../../simplefactions/src/main/resources/installations.yml): `fort.slots.land_vehicles: 2`
2. `InstallationConfigLoaderTest` fixture + capacity assertion
3. `InstallationVehicleServiceTest`: fort OK, NO_CAPACITY at 2 size units, port unsupported

No production Java changes — `InstallationVehicleService` and `InstallationConfigLoader` already support arbitrary category slots.

## Config

```yaml
fort:
  slots:
    static_emplacements: 8
    land_vehicles: 2
```

| Rule | Detail |
|------|--------|
| Host | Fort only (no port/airport land slots) |
| Capacity | Sum of vehicle `size` for `land_vehicles` at fort `<= 2` |
| Example | 2 horse_carts (size 1 + 1) fills capacity; 3rd blocked |

## Live server merge

Add to existing `plugins/SimpleFactions/installations.yml` under `fort.slots`:

```yaml
land_vehicles: 2
```

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=InstallationConfigLoaderTest,InstallationVehicleServiceTest"
cd simplefactions; mvn test
```

## Done when

- [x] Shipped `installations.yml` has fort `land_vehicles: 2`
- [x] Loader and berth service tests cover land vehicle berthing
- [x] Full `mvn test` green
- [x] [00-index](./00-index.md) updated

## Out of scope

- `isBerthableCategory` (77.06)
- `Installations.md` / `AGENTS.md` (77.07)
