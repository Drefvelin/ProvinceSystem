# Step 70d.09 — Siege chronology (nothing after objective)

**Depends on:** 70d.08  
**Status:** **done** (2026-08-23)

## Problem

Off-axis fort homes (e.g. Lan_Airfield at **704**) caused siege slots to sort after defender capital (**705**) because `fightOrderKey` used `provinceId` (fort home) instead of the axis tile where ZOC fired.

## Goal

- Siege `provinceId` stays fort **home** (battle location).
- Sort key and GUI geographic position use **trigger tile** when home is off-axis (`chronologyProvinceId`).
- Invasion leg never schedules `FORT_ZOC` past DT.
- Validator + tests lock Brume acceptance.

## Scope

| File | Change |
|------|--------|
| `ScheduledCampaignBattle` | `chronologyProvinceId`, `sortProvinceId()` |
| `ScheduledCampaignBattleData` / `WarMapper` | Optional JSON field |
| `CampaignScheduleBuildContext` | `objectiveAxisIndex` |
| `CampaignBattlePlacer` | Chronology on siege; invasion past-DT guard; sort by `sortProvinceId()` |
| `CampaignRouteRenderer` | Geographic sort uses `sortProvinceId()` |
| `CampaignScheduleValidator` | Invasion terminal + no slot past DT |

## Acceptance

Brume axis `452, 782, 758, 757, 672, 709, 713, 705`:

- Invasion: `709 FIELD` → `713 SIEGE` → `705 required`
- No Lan_Airfield siege when Greenfort covers overlapping ZOC at **705**
- No invasion slot sorts after **705**
- GUI: `452 - 782 - 672 - [709] - 713 siege - 705`

## Verify

```bash
cd simplefactions
mvn test -Dtest="CampaignBattlePlacerTest,CampaignScheduleBuilderTest,CampaignRouteRendererTest,FortZocIndexTest,WarMapperTest"
mvn test -Dtest="me.Plugins.SimpleFactions.War.**"
```

Manual: deploy, `/faction warpath` on Brume-Lantan per [08-docs-verify.md](./08-docs-verify.md).
