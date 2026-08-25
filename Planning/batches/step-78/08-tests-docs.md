# Step 78.08 — Tests & docs

**Depends on:** [78.10](./10-siege-fort-in-play.md)  
**Repo:** `simplefactions`  
**Status:** done (2026-08-24)

## Goal

Document battle installation picks, schedule windows, and raid prep; full test suite green.

## Shipped

1. [`Wars.md`](../../../../simplefactions/Documentation/Wars.md) — battle-day timeline, installation picks, raid window, vehicle in-play, step 78 in build table
2. [`Installations.md`](../../../../simplefactions/Documentation/Installations.md) — campaign vehicle eligibility and installation picks
3. [`AGENTS.md`](../../../../simplefactions/AGENTS.md) — step 78 service/GUI rows
4. Step 78 marked **done** in [00-index.md](./00-index.md) and [war-build-order.md](../../war-build-order.md)

## Test audit (78.02-78.10)

Unit coverage sufficient; no new integration test added:

| Area | Test class |
|------|------------|
| Schedule / raid window | `BattleScheduleServiceTest`, `RaidWindowServiceTest`, `ConfigLoaderBattleScheduleTest` |
| Picks | `BattleInstallationPickServiceTest`, `BattleInstallationPickEligibilityTest` |
| Siege in-play | `BattleSiegeFortServiceTest`, `BattleInstallationInPlayServiceTest` |
| Vehicles | `BattleVehicleEligibilityServiceTest` |
| Raids filter | `RaidTargetServiceTest` |

## Verify

```powershell
cd simplefactions; mvn test
```

## Done when

- [x] Docs reflect locked rules from [01-planning-lock.md](./01-planning-lock.md)
- [x] `mvn test` green
- [x] Step 78 index marked done
