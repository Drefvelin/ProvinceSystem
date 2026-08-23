# Step 64.08 — Remove battle zone limitation

**Repos:** `Workspace/simplefactions`  
**Depends on:** [64.06 resolver](./06-resolver-launch.md) (can parallelize after 64.02)  
**Touches:** `BattlePlacementValidator`, `BattleBoundsService`, `BattleLeavePenaltyService`, `BattleSideSetupService`, `BattleContestSetup`, `Battle.java`, `SimpleFactions.java`, tests, `Wars.md` (preview for 64.09)

## Goal

Delete province-bound battle enforcement so staff can place spawns and objectives anywhere. Required for naval invasion layouts in step 65.

## Scope

### Remove or no-op

| Component | Action |
|-----------|--------|
| `BattlePlacementValidator.validatePlacementOrThrow` | Remove province checks; keep only world/dimension sanity if any |
| `BattlePlacementValidator.validateForStart` | Remove allowed-province requirement |
| `BattlePlacementValidator.resolveAllowedProvinces` | Delete or return empty always |
| `BattleBoundsService` | Stop populating `allowedProvinceIds` on battle create |
| `BattleLeavePenaltyService` | Remove listener / countdown for field+siege; delete class or stub no-op |
| `SimpleFactions` | Unregister leave penalty listener |

### Keep

- Raid unbounded behavior (unchanged)
- Province presence tracker (used elsewhere)
- Capture point / contest area mechanics (only placement validation removed)

### Persistence

- Stop writing `allowedProvinceIds` on new battles; ignore on load.

## Tasks

1. Remove placement validation calls or make them pass-through.
2. Remove leave penalty service registration and tests (update or delete `BattleLeavePenaltyServiceTest`).
3. Update `BattlePlacementValidatorTest` for new behavior.
4. Remove `BattleBoundsService` usage from campaign launch if present.

## Tests

- Battle starts with spawn in distant province: success.
- Player changes province during field battle: no countdown/death.

## Done when

All tests pass; no province-leave penalty in runtime.
