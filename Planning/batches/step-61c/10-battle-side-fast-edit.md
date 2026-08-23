# Step 61c.10 - Battle side fast edit GUI

**Repo:** SF · [00-index](./00-index.md) · **Depends on:** [61c.09 battle warband persistence](./09-battle-warband-persistence.md) · **Next:** [62 war end & goals](../step-62/00-index.md)

## Goal

Replace repetitive `/battle setspawn`, `setjail`, and `addpoint` commands with one-click GUI actions at the player's current location during battle setup.

## Changes

| Area | Detail |
|------|--------|
| **Side Edit GUI** | Battle edit -> Sides -> click side -> Set spawn / Set jail / Add point buttons |
| **Auto point names** | Global A, B, C... via `BattleCapturePoints.createAtPlayer` + `compressGlobalLetters` / `syncLinearChain` when sequential capture is on |
| **capture_points_enabled** | New battle + template flag; `field_default` YAML default true; siege/raid false |
| **BattleSideSetupService** | Shared logic for commands and GUI |
| **Side PDC** | `battle_side_id` on side items for reliable click handling |
| **UI gating** | Points button (slot 23) and capture tick use `capturePointsEnabled` |

## Side Edit layout

| Slot | Action |
|------|--------|
| 4 | Side info (spawn/jail coords in lore) |
| 10 | Set spawn at player location |
| 12 | Set jail at player location |
| 14 | Add capture point (when `capture_points_enabled`) |
| 26 | Back to Side View |

## Verification

- [x] `BattleSideSetupServiceTest`, `BattleMapperTest`, `BattleTemplateYamlLoaderTest`
- [x] `mvn test` green

Manual:

- [ ] `/battle edit` -> Sides -> attacker -> Set spawn/jail/add point at feet
- [ ] Points named global A, B, C (both sides share one letter sequence)
- [ ] Siege battle hides Add point; field shows it
- [ ] Restart restores layout (61c.09 persistence)

**Done** (2026-08-21). **Next:** [62 war end & goals](../step-62/00-index.md).
