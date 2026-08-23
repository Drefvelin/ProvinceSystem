# Step 61.04 — Collective lives at battle start

**Done** (2026-08-21). **Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61.03 battle pool](./03-battle-pool.md) · **Next:** [61.06 casualty apply](./06-casualty-apply.md)

## Goal

For **campaign** field and siege battles, set collective side lives from committed regiments at **`battle.start()`**, replacing template defaults from 60.05.

## Formula (locked 61.01)

```text
sideLives = max(minSideLives, livesPerRegiment * committedRegiments - playersAtStart)
```

| Input | Source |
|-------|--------|
| `committedRegiments` | `BattlePoolService.totalCommittedRegiments(...)` per side |
| `playersAtStart` | Unique online member UUIDs on that side's warbands at start |
| Config | `Cache.warBattleLivesPerRegiment`, `Cache.warBattleMinSideLives` |

## Integration

| Location | Change |
|----------|--------|
| `ConfigLoader` + `Cache` | Load new keys |
| `config.yml` | Defaults documented |
| `Battle.start()` or `CampaignBattleLaunchService` | If `warId != null` and type FIELD/SIEGE → call `BattleLivesService.applyCampaignLives(battle)` |
| `BattleSide` | Set collective `lives` + `maxLives`; refresh boss bar |

### Skip conditions

| Case | Behavior |
|------|----------|
| `warId == null` | Template lives (staff) |
| `BattleType.RAID` | 60.08 raid lives / elimination |
| Zero committed regiments on a side | `minSideLives` floor (log warning in staging) |

## Tests

`BattleLivesServiceTest`:

| Test | Assert |
|------|--------|
| `applyCampaignLives_invasionNode` | Attacker/defender lives match mocked pool totals − players |
| `applyCampaignLives_respectsMinFloor` | Small pool still ≥ `minSideLives` |
| `applyCampaignLives_skipsManualBattle` | No change when `warId` null |
| `applyCampaignLives_skipsRaid` | Raid battle unchanged |

Use mock boss bar pattern from `BattleFactoryTest`.

## Manual staging

1. War with known commitments → schedule campaign battle → at start, boss bar shows lives ≠ template default (e.g. not 25)  
2. More players join before start → lives decrease accordingly  

## Verification

- [x] `war.battle_military.lives_per_regiment` / `min_side_lives` in config, Cache, ConfigLoader
- [x] `BattleLivesService` with per-side formula via `BattlePoolService`
- [x] `Battle.start()` applies campaign lives for FIELD/SIEGE with `warId`
- [x] `PER_PLAYER` life mode removed; collective only
- [x] `BattleLivesServiceTest` + full `mvn test` pass

## Out of scope

- Casualty tracking (61.05)
