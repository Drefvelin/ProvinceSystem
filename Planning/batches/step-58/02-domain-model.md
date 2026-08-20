# Step 58.02 — Domain model + full campaign axis

**Step:** 58 · **Repo:** SF  
**Spec:** [01-planning-lock.md](./01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

Persistence and generation for step 58 progression: **full axis** (`attacker capital … B … objective`), **`cursorIndex` at border B**, initiative/phase/occupation/proposal fields initialized at declare. No `CampaignProgressionService`, GUI, or battle logic yet (58.03+).

## Scope

- [x] `CampaignPhase`, `ObjectiveHolder` enums; expand `WarEndReason` (`WHITE_PEACE`, `AUTO_WHITE_PEACE`)
- [x] `War` / `WarData` progression fields (initiative, occupation lists, phase, holder, white peace flags)
- [x] `WarMapper.fromData` defaults for legacy saves (schemaVersion stays **2**)
- [x] `WarDebugFormatter` — real initiative/phase/proposal fields
- [x] `WarCampaignService` — full axis, capital-closer rule, `initProgressionState`, package-visible helpers
- [x] Config keys: `war.battle_cadence`, `war.occupation.include_enemy_neighbors`
- [x] Unit tests + persistence round-trip fixtures
- [x] `mvn test` — **48 tests**, 0 failures

## Full axis generation

1. Regional objective via `ObjectiveProvincePicker` (unchanged).
2. Border **B** via `pathfinder.computeCampaignLine`.
3. **Capital-closer:** compare path cost `B → defender capital` vs `B → regional objective`; use capital when strictly closer.
4. Right segment `B → objective`; left segment `attackerCapital → B` (attacker capital required).
5. Merge paths (dedupe **B**); `cursorIndex` = index of **B**.

**Regen:** `WarManager.regenerateCampaign` calls `populateCampaign` — progression fields reset. **Raid:** still skips campaign populate.

## Files

| File | Role |
|------|------|
| `War/enums/CampaignPhase.java` | `INVASION`, `RETAKE`, `COUNTER_PUSH` |
| `War/enums/ObjectiveHolder.java` | `ATTACKER`, `DEFENDER` |
| `War/enums/WarEndReason.java` | White peace end reasons |
| `War/War.java` | Progression fields |
| `Database/WarData.java` | Gson DTO (nullable initiative for legacy) |
| `War/WarMapper.java` | Round-trip + defaults |
| `War/WarDebugFormatter.java` | Debug JSON |
| `War/campaign/WarCampaignService.java` | Full axis + `initProgressionState` |
| `resources/config.yml` | Battle cadence + occupation config |
| `Cache.java`, `Loaders/ConfigLoader.java` | Load new keys |

## Tests

| Test | Cases |
|------|-------|
| `WarCampaignServiceTest` | Full axis, capital-closer, fail no atk capital, `mergeAxisPaths` |
| `WarManagerCampaignTest` | Declare hook expects `[5,10,20,30]`, `cursorIndex=1`, initiative 4/4 |
| `WarMapperTest`, `WarDataRoundTripTest`, `WarPersistenceFileTest`, `WarDebugFormatterTest` | New fields in fixtures |

## Out of scope (58.03+)

- `CampaignProgressionService`, cursor move, initiative spend
- `OccupationService` (58.04)
- `CampaignView` GUI
- White peace recalc logic
- `schemaVersion` bump / migration tool

## Brume/Lantan note

Existing wars with step 57 geometry (`[706,705]`, `cursorIndex: 0`) load with mapper defaults; `/faction warpath` regen upgrades to full axis with cursor at border **706**.

## Status

**Done** (2026-08-20). **Next batch:** [58.03 progression core](./03-progression-core.md) (TBD).
