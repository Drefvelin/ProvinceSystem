# Step 60.05 — Named YAML templates + battle create

**Code batch.** Replace 60.04 JSON province templates with named YAML battle templates; create typed battles via `/battle create`; apply templates optionally from Battle View GUI.

**Repos:** `Workspace/simplefactions`  
**Depends on:** [60.04 battle domain](./04-battle-domain.md)  
**Next:** [60.06 field runtime](./06-field-runtime.md)

> **Supersedes 60.04 persistence:** JSON files under `BattleTemplates/` are removed. Templates are authored in `battle-templates.yml` instead. See [superseded note on 60.04](./04-battle-domain.md#superseded-by-605).

## Delivered

| Component | Path |
|-----------|------|
| YAML config | `src/main/resources/battle-templates.yml` |
| Template loader | `Loaders/BattleTemplateLoader.java` |
| Lookup service | `War/battle/template/BattleTemplateService.java` (name-keyed) |
| Battle factory | `War/battle/engine/BattleFactory.java` (`createBlank`, `applyTemplate`, `resetToBase`, `applyCampaignDefault`) |
| Create command | `/battle create <type> <battleId>` in `BattleCommandManager` |
| Template picker GUI | Battle View slot 7 → `Template Selection` inventory |
| Tab completion | `BattleTabCompletion` (type, battle id) |
| Campaign defaults | `battle.campaign_template.{field,siege,raid}` in `config.yml` (consumed in 60.09) |
| Runtime metadata | `templateName`, siege/raid/naval fields on `Battle.java` |

**Removed:** `BattleTemplateData`, `BattleTemplateMapper`, `BattleTemplateStore`, `Database.saveBattleTemplate()` / `loadBattleTemplates()`, `BattleTemplates/` folder.

## YAML schema

File: `plugins/SimpleFactions/battle-templates.yml`

Top-level keys are template names (e.g. `raid_template`, `field_default`). Each template has a single `type` (`field`, `siege`, or `raid`) and one mode block.

```yaml
raid_template:
  type: raid
  attacker:
    spawn: { x: 0, y: 64, z: 0 }
  defender:
    spawn: { x: 10, y: 64, z: 10 }
  defender_respawn_mode: infinite
  raid_target:
    id: target
    location: { x: 50, y: 64, z: 50 }
  friendly_fire: true
  keep_inventory: true
```

Blank `world` on locations resolves to `Cache.worldName`.

Optional campaign mapping in `config.yml` (for 60.09):

```yaml
battle:
  campaign_template:
    field: field_default
    siege: siege_default
    raid: raid_template
```

## Commands

| Command | Description |
|---------|-------------|
| `/battle create <type> <battleId>` | Admin: create blank typed battle, open Battle View |
| `/battle edit <id>` | Unchanged: open Battle View for live instance |
| `/battle setspawn`, `setjail`, `addpoint` | Unchanged: configure battle after create |

Fixed side ids: **`attacker`** and **`defender`**.

No `/battle template` commands. No template editor GUI.

## Template picker (Battle View slot 7)

- Opens **Template Selection** inventory
- **None (base):** resets layout to blank typed battle (`resetToBase`)
- **Template items:** filtered by battle type; applies YAML preset (`applyTemplate`)
- **Wipe rule:** any template change clears sides, points, warband assignments, and layout metadata, then re-applies selection. Preserves `id`, `battleType`, `provinceId`, `warId`.
- Blocked after battle start (same as other Battle View edits)

Campaign battles (60.09) call `BattleFactory.applyCampaignDefault()` on create; staff can override via the same GUI before start.

## BattleFactory behavior

| Method | Purpose |
|--------|---------|
| `createBlank(type, battleId)` | Typed base battle, no template, empty attacker/defender sides |
| `applyTemplate(battle, templateName)` | Wipe layout, seed from YAML template |
| `resetToBase(battle)` | Wipe layout, restore base defaults |
| `applyCampaignDefault(battle)` | Apply config template for battle type (60.09) |

Win/end logic is out of scope for 60.05.

## Tests

| Test class | Coverage |
|------------|----------|
| `Loaders/BattleTemplateYamlLoaderTest` | YAML parse, world fallback, invalid type skipped |
| `War/battle/template/BattleTemplateServiceTest` | Name lookup, defaults |
| `War/battle/engine/BattleFactoryTest` | createBlank, apply/reset, wipe on switch, campaign default |
| `Loaders/ConfigLoaderBattleTemplateDefaultsTest` | Config defaults + campaign template keys |

Run: `mvn test` in `simplefactions/`.

## Manual staging checklist

- [ ] `/battle create raid test_raid` opens Battle View with template **None**
- [ ] Click Template (slot 7) → pick `raid_template` → spawns/raid target appear
- [ ] Switch to **None** → layout wiped back to base
- [ ] Switch to another template → previous manual overrides gone
- [ ] Start battle → template picker blocked
- [ ] Toggle settings + `/battle setspawn` / `addpoint` still work after template apply

## Status

**Done** (2026-08-20). **Next:** [60.06 field runtime](./06-field-runtime.md).
