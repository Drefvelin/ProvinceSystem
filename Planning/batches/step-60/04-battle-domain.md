# Step 60.04 — Battle domain

**Code batch.** Campaign battle types, per-province reusable templates, JSON persistence, and lookup service.

**Repos:** `Workspace/simplefactions`  
**Depends on:** [60.03 warbands merge](./03-warbands-merge.md)  
**Next:** [60.05 named YAML templates](./05-template-gui.md)

> ## Superseded by 60.05
>
> Per-province JSON under `BattleTemplates/template_{provinceId}.json`, `BattleTemplateMapper`, `BattleTemplateStore`, and `Database` template IO were **removed** in [60.05](./05-template-gui.md). Templates are now named entries in `battle-templates.yml`. This doc remains as historical reference for the domain types introduced in 60.04.

## Delivered

| Component | Path |
|-----------|------|
| Battle type enum | `War/battle/enums/BattleType.java` |
| Defender respawn enum | `War/battle/enums/DefenderRespawnMode.java` |
| LifeType JSON helpers | `War/battle/enums/LifeType.java` |
| Template domain | `War/battle/template/*` |
| Gson DTO | `Database/BattleTemplateData.java` |
| Mapper | `War/battle/template/BattleTemplateMapper.java` |
| Store | `War/battle/template/BattleTemplateStore.java` |
| Loader | `Loaders/BattleTemplateLoader.java` |
| Lookup service | `War/battle/template/BattleTemplateService.java` |
| Database IO | `Database.saveBattleTemplate()` / `loadBattleTemplates()` |
| Config defaults | `battle.province_leave_countdown_seconds`, `battle.siege.contest_duration_seconds`, `battle.raid.defender_respawn_mode_default` |
| Runtime metadata | optional `provinceId`, `battleType`, `warId` on `Battle.java` |
| Plugin wiring | `BattleTemplates/` folder + load on enable |

## JSON schema (sketch)

File: `plugins/SimpleFactions/BattleTemplates/template_{provinceId}.json`

```json
{
  "schemaVersion": 1,
  "provinceId": 42,
  "terrainFallback": "hills",
  "field": {
    "attacker": { "spawn": { "world": "TFMC_Map", "x": 1, "y": 64, "z": 2 }, "jail": { "x": 3, "y": 64, "z": 4 } },
    "defender": { "spawn": { "x": 5, "y": 64, "z": 6 }, "jail": { "x": 7, "y": 64, "z": 8 } },
    "friendlyFire": true,
    "keepInventory": true,
    "lifeType": "COLLECTIVE",
    "lives": 25,
    "capturePoints": [{ "id": "alpha", "location": { "x": 100, "y": 70, "z": 200 } }]
  },
  "siege": {
    "contestDurationSeconds": 180,
    "navalVariant": false,
    "contestArea": { "min": { "x": 0, "y": 60, "z": 0 }, "max": { "x": 10, "y": 80, "z": 10 } }
  },
  "raid": {
    "defenderRespawnMode": "infinite",
    "raidTarget": { "id": "target", "location": { "x": 50, "y": 64, "z": 50 } }
  }
}
```

Blank `world` resolves to `Cache.worldName` on load.

## API

- `BattleTemplateService.getInstance().getTemplate(provinceId)`
- `getModeConfig(provinceId, BattleType)` - returns mode block with config defaults applied
- `hasTemplate(provinceId)`
- `SimpleFactions.getBattleTemplateService()`
- `BattleTemplateStore.persist(template, folder)` / `Database.saveBattleTemplate(template)`

## Tests

| Test class | Coverage |
|------------|----------|
| `War/battle/template/BattleTemplateMapperTest` | Domain ↔ DTO, enum JSON, world fallback |
| `War/battle/template/BattleTemplatePersistenceFileTest` | JSON file round-trip |
| `War/battle/template/BattleTemplateServiceTest` | Lookup, defaults, missing template |
| `Loaders/ConfigLoaderBattleTemplateDefaultsTest` | Config keys + validation |

Run: `mvn test` in `simplefactions/`.

**173 tests** passing (2026-08-20).

## Manual staging checklist

- [ ] Create `BattleTemplates/template_{id}.json` by hand with a field block (spawns + capture point)
- [ ] Restart server; log shows loaded battle template count
- [ ] Delete template file; restart; province lookup returns null
- [ ] Manual `/battle create` still works unchanged (60.03 regression check)

## Status

**Done** (2026-08-20). **Next:** [60.05 template GUI](./05-template-gui.md).
