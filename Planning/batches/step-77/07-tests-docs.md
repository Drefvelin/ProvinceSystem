# Step 77.07 — Tests, docs, and verify

**Depends on:** [77.06](./06-berthable-category.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Close step 77 with player-facing documentation, agent guide updates, confirmed test coverage, and green `mvn test`.

## Tests confirmed (77.02–77.06)

| Test class | Coverage |
|------------|----------|
| `VehiclesConfigLoaderTest` | `default-per-person`, `per-person`, `ignore-limit`, `default-upkeep`, validation |
| `VehicleSlotGuardTest` | per-type, total, ignore-limit, unlimited total, unknown type |
| `VehicleConstructionMessagesTest` | all `CanBuildResult` messages; no em dashes |
| `PlayerVehicleRegistryTest` | `countPersonalOfType`, `countPersonalExcludingIgnoreLimit` |
| `InstallationVehicleServiceTest` | land vehicle fort berth OK / NO_CAPACITY / port unsupported |
| `InstallationConfigLoaderTest` | fort `land_vehicles: 2` capacity |
| `VehicleCategoryRulesTest` | berthable categories; train false |

No new test classes in 77.07; coverage was added in prior batches.

## Docs updated

| File | Changes |
|------|---------|
| [`Installations.md`](../../../../simplefactions/Documentation/Installations.md) | Personal limits section, construction messages, category hosting, `land_vehicles` config, `vehicles.yml` keys, battle-prep note, package layout, step 77 link |
| [`AGENTS.md`](../../../../simplefactions/AGENTS.md) | `vehicles/` scope, where-new-code-goes rows, step 77 planning link |

## Verify

```powershell
cd simplefactions; mvn test "-Dtest=me.Plugins.SimpleFactions.vehicles.**"
cd simplefactions; mvn test
```

## Done when

- [x] All locked construction messages have unit test coverage (no em dashes)
- [x] `Installations.md` documents personal limits, land berths, config keys
- [x] `AGENTS.md` documents `vehicles/` placement for step 77 classes
- [x] Full `mvn test` green
- [x] Step 77 done-when items in [00-index.md](./00-index.md) checked

## Out of scope

- Battle/raid vehicle selection (step 78+)
- Installation GUI berth list
- Un-berth
