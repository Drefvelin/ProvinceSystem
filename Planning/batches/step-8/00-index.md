# Step 8 — Plugin integrate (batch index)

**Repos:** `Workspace/armourshop` + ProvinceSystem API/frontend + live ItemsAdder  
**Depends on:** [step-7](../step-7/00-index.md) pack writer harness green

Parent: [../../10-armourshop-itemsadder.md](../../10-armourshop-itemsadder.md), [../../05-skins-system.md](../../05-skins-system.md).

## Goal

Wire Step 7 pack writers into live apply: player picks **kind** + **`base_set`** (armor tier or filtered type) at upload → Discord approve → ArmourShop pull → `tfmc_submissions` + shop YAML + LuckPerms → deferred IA reload → `POST /plugin/applied` → usable in ArmourShop.

## Where Step 8 leaves us

```text
Upload (kind + base_set + PNGs) → Discord approve
→ ArmourShop pull → pack + ps_armor/ps_items + LP
→ deferred reload → applied ack → player applies skin
```

**Done when:** Flow 2 steps 9–11 complete for armor + handheld + large_handheld ([12-end-to-end-flows.md](../../12-end-to-end-flows.md)). Bow/crossbow kinds need [07](./07-bow-crossbow-writers.md) before live apply.

## Locked rules — kinds + `base_set`

Player-picked `base_set` becomes SkinSet `set:` (ArmourShop BaseSet id). Must match the kind allowlist (pairing enforced).

**Enabled upload kinds:** `armor_set`, `handheld`, `large_handheld`, `bow`, `large_bow`, `crossbow`  
**Disabled (not selectable):** `item` (no need yet; future BaseSet `item` later)  
**Deferred (not in dropdowns):** `rifles`, `pistols`, `shotguns`, `launchers`, `shields`, `helmets`  
**Not in MVP allowlists yet:** `longswords`, `greataxes`

| `base_set` | Pack kind | Notes |
|------------|-----------|--------|
| `iron`, `steel`, `abyssalite`, `mythril`, `mage`, `infantry` | `armor_set` | Tier picker; one tier per skin |
| `swords`, `battleaxes`, `daggers`, `warhammers`, `shortswords`, `hatchets`, `hoes`, `knives` | `handheld` | 16×16; Step 7 `FlatItemWriter` |
| `spears`, `polearms`, `greathammers`, `staffs` | `large_handheld` | 32×32 + grip; Step 7 `LargeHandheldWriter` |
| `shortbows` | `bow` | New kind — draw/pull; writer in [07](./07-bow-crossbow-writers.md) |
| `longbows` | `large_bow` | New kind — large bow + pull; writer in 07 |
| `crossbows` | `crossbow` | New kind — pull/charged; writer in 07 |

**UI:** Kind picker lists only enabled kinds (no `item`). Type/tier dropdown is **filtered by kind**. Grip only for `large_handheld`.

**Apply:** Pack write applies all enabled kinds with writers (`armor_set`, `handheld`, `large_handheld`, `bow`, `large_bow`, `crossbow`).

## Shop layout

| Category id | `is-item` | Kinds |
|-------------|-----------|-------|
| `ps_armor` | false | `armor_set` |
| `ps_items` | true | `handheld`, `large_handheld`, `bow`, `large_bow`, `crossbow` |

Each SkinSet: id=`{slug}`, `set: {base_set}`, `permission: armourshop.submission.{slug}`, **no scroll**, IA paths `ia.tfmc_submissions:…`.

**Ack:** `POST /plugin/applied` after deferred IA reload completes (or restart reload), not only when files are written.

## Scope

| In | Out |
|----|-----|
| `base_set` API + UI (filtered allowlists) | `item` kind; guns; shields; helmets |
| Pull + pack for armor / handheld / large | Pack template design for melee (Step 7) |
| `ps_armor` / `ps_items` + LP grant | Ban-role mute; scrolls for player skins |
| Deferred reload + applied ack | Grip display tuning; per-slug categories |
| Bow / large_bow / crossbow writers (07) | `item_3d` / `shield` (B4) |

## Batch order

1. [01-base-set-api](./01-base-set-api.md) — DB + validation + approved payload  
2. [02-base-set-ui](./02-base-set-ui.md) — `/skins` dropdowns (no `item`)  
3. [03-pull-and-write](./03-pull-and-write.md) — pull + pack write (existing writers)  
4. [04-shop-and-lp](./04-shop-and-lp.md) — shop YAML + LP + config merge  
5. [05-reload-and-ack](./05-reload-and-ack.md) — deferred IA reload + applied  
6. [06-docs-e2e](./06-docs-e2e.md) — docs + staging Flow 2 (melee/armor)  
7. [07-bow-crossbow-writers](./07-bow-crossbow-writers.md) — bow / large_bow / crossbow pack writers + harness + wire apply  

**Process:** one batch = one plan + implement; stop after verify; start the next only when asked.

## Config (ArmourShop)

| Key | Purpose |
|-----|---------|
| `skins-api.base-url` / `plugin-key` | ProvinceSystem plugin API |
| `pack-apply.ia-contents-path` | ItemsAdder `contents/` (live or Copy dry-run) |
| `pack-apply.categories-path` | ArmourShop `Categories/` folder |
| `start-points` / `item-start-points` | GUI slot lists — merge `item-start-points` from server drop; do not commit live secrets |

## Final checkpoint

```text
Approve → pull → pack + shop + LP → reload → applied
→ issuer sees set in ps_armor / ps_items and can apply
(+ after 07: bow / large_bow / crossbow same path)
```

**Status:** batches **01–05** + **07** (bow writers) implemented. **06** = operator STAGING Flow 2 ([STAGING.md](../../../STAGING.md) Step 8).