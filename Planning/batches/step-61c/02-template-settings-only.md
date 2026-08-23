# Step 61c.02 — Battle template settings-only

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61c.01 planning lock](./01-planning-lock.md) · **Next:** [61c.05 docs verify](./05-docs-verify.md)

## Goal

Battle templates define **rule defaults only**. Campaign and staff template apply must not seed spawns, jails, or capture geometry from YAML.

## Files to change

| File | Change |
|------|--------|
| [`battle-templates.yml`](../../../../simplefactions/src/main/resources/battle-templates.yml) | Remove `spawn`, `jail`, `capture_points`, `contest_area` coords, `raid_target.location`; keep booleans, lives, durations, modes |
| [`BattleModeTemplate.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/template/BattleModeTemplate.java) | Layout fields optional / deprecated for YAML load; or keep fields but unused by apply path |
| [`BattleFactory.java`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/engine/BattleFactory.java) | Split `applyModeSettings` vs layout; `applyTemplate` / `applyCampaignDefault` call settings only |
| [`BattleFactoryTest.java`](../../../../simplefactions/src/test/java/me/Plugins/SimpleFactions/War/battle/engine/BattleFactoryTest.java) | Update: template apply sets FF/lives/type, **does not** add capture points or spawns |

## Implementation sketch

```java
public static void applyTemplate(Battle battle, String templateName) {
    // ... validate ...
    resetLayout(battle);
    applyModeSettings(battle, config);
    battle.setTemplateName(templateName);
    // DO NOT call seedTemplateLayout
    seedBaseSides(battle); // empty spawns, default side shells
}

public static void applyCampaignDefault(Battle battle) {
    // same settings-only path
}
```

Keep `seedTemplateLayout` / point seeding **private** for potential staff "import layout from saved battle" later, or delete if unused.

### Settings mapping (keep)

| Field | Applies to |
|-------|------------|
| `friendly_fire`, `keep_inventory` | All types |
| `life_type`, `lives` | Field (manual fallback) |
| `contest_duration_seconds` | Siege |
| `defender_respawn_mode`, `defender_lives` | Raid |
| `naval_variant` | Field/siege flag only (naval spawn still staff-placed) |

### Campaign battle create

[`CampaignBattleLaunchService.createCampaignBattle`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/campaign/CampaignBattleLaunchService.java): after `applyCampaignDefault`, battle has sides + rules, **no points**. Staff checklist in 61c.05 requires edit before meaningful field fight.

## Tests

| Test | Assert |
|------|--------|
| `applyCampaignDefault_field_noCapturePoints` | Field battle, 0 capture points after apply |
| `applyTemplate_siege_settingsOnly` | Contest duration set; no contest area bounds |
| `applyTemplate_preservesCampaignIds` | Still passes (unchanged) |
| `resetToBase_clearsLayout` | Unchanged behavior |

## Docs touch (minimal)

Note in 61c.05 only; optional one-line in [`BattleInventoryManager`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/battle/ui/BattleInventoryManager.java) template lore: "Applies battle rules only".

## Verification

- [x] YAML has no coordinate blocks  
- [x] New campaign battle has empty layout until staff edit  
- [x] `mvn test` green  

**Done when:** template apply is settings-only and tests prove no seeded geometry.

**Done** (2026-08-21). **Next:** [61c.03 warschedule output](./03-warschedule-output.md) or [61c.04 campaign warband signup](./04-campaign-warband-signup.md).
