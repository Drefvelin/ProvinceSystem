# Step 76.07 — Tests, docs, and verify

**Depends on:** [76.06](./06-owner-consent.md)  
**Repos:** `simplefactions` + `vehicleframework`  
**Status:** done (2026-08-24)

## Goal

Close step 76 with full chat-message test coverage, player-facing documentation, agent guide updates, and green test suites in both repos.

## Tests added / confirmed

| Test class | Coverage |
|------------|----------|
| `VehicleTransferMessagesTest` | All locked `CanRegisterResult` mappings + static helpers (`notLeader`, `unknownInstallation`, `noPendingSession`, consent strings); no em dashes |
| `VehicleTransferConsentServiceTest` | `notifyExpired` sends locked expiry message |
| `InstallationBoundsTest` | Consent proximity boundary at 20 / 21 blocks |
| `InstallationConfigLoaderTest` | Root timeout/proximity + per-kind `radius` (76.03) |
| `InstallationVehicleServiceTest` | `canRegister` / `register` (76.04) |
| `VehicleTransferConsentRequestTest` | Config-based timeout (76.06) |

VF automated interact tests remain deferred per [02-vf-pre-interact-event.md](./02-vf-pre-interact-event.md).

## Docs updated

| File | Changes |
|------|---------|
| [`Installations.md`](../../../../simplefactions/Documentation/Installations.md) | Vehicle berth section, config keys (`radius`, consent, timeout), package layout, step 76 planning link |
| [`AGENTS.md`](../../../../simplefactions/AGENTS.md) | `vehicles/` package layout, where-new-code-goes rows, verify hint |

## Verify

```powershell
cd simplefactions; mvn test
cd vehicleframework; mvn test
```

Focus: `me.Plugins.SimpleFactions.vehicles.**`, `VehicleTransferMessagesTest`, `InstallationBoundsTest`.

## Done when

- [x] All locked chat messages have unit test coverage (no em dashes)
- [x] `Installations.md` documents berth command, validation, consent, config, VF owner rules
- [x] `AGENTS.md` documents `vehicles/` package placement
- [x] `mvn test` green in `simplefactions` and `vehicleframework`
- [x] Step 76 done-when items in [00-index.md](./00-index.md) checked

## Out of scope

- Installation GUI berth list
- Un-berth
- VF MockBukkit interact test harness
