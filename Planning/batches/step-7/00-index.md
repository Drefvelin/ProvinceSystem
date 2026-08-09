# Step 7 — Pack writer (batch index)

**Repos:** `Workspace/armourshop` (pure pack writer + fixtures)  
**Depends on:** Steps 2–6 (API kinds + mint/link exist; Discord not required for harness)

Parent: [../../10-armourshop-itemsadder.md](../../10-armourshop-itemsadder.md), [../../05-skins-system.md](../../05-skins-system.md).

## Goal

Given a fixture submission (kind, slug, display name, optional grip, PNGs), write a valid ItemsAdder **`tfmc_submissions`** tree (YAML + textures + grip models where needed). Verify with a local harness — **no Discord, no live API poll, no LP, no IA reload**.

## Where Step 7 leaves us

```text
Fixture / harness → armor_set | item | handheld | large_handheld files OK
→ (Step 8) pull → shop + LP → reload → applied → usable in ArmourShop
```

**Done when:** Harness writes all four MVP kinds to an output dir; YAML/models match locked IA rules below.

**Not in Step 7:** `GET /plugin/approved`, shop category YAML, LuckPerms, deferred reload, `POST /plugin/applied`, live MC E2E — see [step-8](../step-8/00-index.md) (plugin integrate).

## Locked IA rules

| Kind | Resource | Model JSON |
|------|----------|------------|
| `armor_set` | `generate: true` + `armors_rendering` (like `tfmc_armor`) | None (IA generates) |
| `item` | `generate: true` + `parent: item/generated` (or equiv.) | None |
| `handheld` | `generate: true` + `parent: item/handheld` | None |
| `large_handheld` | `generate: false` + `model_path` | Thin per-skin JSON parenting one of **3 grip templates** (`bottom` / `middle` / `top`) with locked `display` |
| `item_3d` / `shield` | Out of Step 7 | Later (B4 / S5) |

## Scope

| In | Out |
|----|-----|
| Empty `tfmc_submissions` scaffold | Live poll / applied ack |
| Pure Java pack writer (no Bukkit in core) | Shop YAML + LP |
| Grip template JSONs + large_handheld writer | Deferred IA reload |
| Fixture harness + sample PNGs | `item_3d` / `shield` |
| Planning / STAGING dry-run note | Discord review changes |

## Batch order

1. [01-scaffold](./01-scaffold.md) — namespace layout + config path keys  
2. [02-armor-writer](./02-armor-writer.md) — `armor_set` YAML + textures  
3. [03-flat-item-writers](./03-flat-item-writers.md) — `item` + `handheld`  
4. [04-grip-templates](./04-grip-templates.md) — grip JSONs + `large_handheld`  
5. [05-harness-verify](./05-harness-verify.md) — CLI/main + fixtures  
6. [06-docs](./06-docs.md) — parent docs + dry-run checklist  

**Process:** one batch = one plan + implement; stop after verify; start the next only when asked.

## Config (documented in 01; used by harness / later plugin)

| Key | Purpose |
|-----|---------|
| `ia.contents-path` (name TBD) | Absolute path to `ItemsAdder/contents` (or Copy / temp out dir) |
| Existing `skins-api.*` | Not required for harness; used in Step 8 |

## Final checkpoint

```bash
cd Workspace/armourshop
mvn -DskipTests package
java -cp target/classes net.tfminecraft.ArmourShop.pack.PackHarnessMain
```

Harness OK → inspect YAML/PNG/(grip) models under `tfmc_submissions` → optional: point IA at that folder locally → Step 8 wires live apply.
