# Step 58.04 — Occupation zone service

**Step:** 58 · **Repo:** SF  
**Spec:** [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

On campaign battle win, compute and persist the winner's **occupation zone** (battle province + qualifying graph neighbors) into `occupied_by_*` and `last_battle_occupied`. Pure service + tests; no GUI or battle-engine wiring yet.

## Scope

- [x] Rename config/cache: `war.occupation.include_enemy_neighbors`, `Cache.warOccupationIncludeEnemyNeighbors` (no `bulge` in code)
- [x] `OccupationZone` immutable result type
- [x] `OccupationService` with `computeOccupationZone` + `applyBattleWin`
- [x] Neighbor rules: campaign line, existing occupation, enemy-owned (config)
- [x] `OccupationServiceTest` (10 cases)
- [x] `mvn test` — **74 tests**, 0 failures

## Occupation zone rule

On battle win:

1. Always include battle province.
2. Include each graph neighbor if **any** of:
   - On `campaignProvinces[]`
   - Already in `occupiedByAttacker` or `occupiedByDefender`
   - Owned by enemy belligerent coalition and `include_enemy_neighbors: true`
3. Merge into winner's list without duplicates.
4. Set `lastBattleOccupied` to provinces **newly added** this battle.

## Files

| File | Role |
|------|------|
| `War/progression/OccupationZone.java` | Zone result type |
| `War/progression/OccupationService.java` | Compute + apply |
| `Cache.java`, `ConfigLoader.java`, `config.yml` | Renamed occupation config |
| `War/pathfinder/BelligerentTerritory.java` | Enemy ownership checks (unchanged) |

## Config

```yaml
war:
  occupation:
    include_enemy_neighbors: true
```

## Out of scope (58.05+)

- `WhitePeaceService` (58.05)
- Wire `applyBattleWin` into battle engine / `WarManager` (58.06 / 59)
- Map `wars[]` export (67)

## Status

**Done** (2026-08-20). **Next batch:** [58.05 Campaign GUI](./05-campaign-gui.md) (TBD).
