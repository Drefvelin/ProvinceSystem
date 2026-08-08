# Step 15 — Gun skins via IA ids (no CMD dual-write)

**Repos:** `Workspace/gunsandgadgets` + `Workspace/armourshop` + ProvinceSystem Planning  
**Depends on:** [step-14](../step-14/00-index.md)

## Goal

GaG resolves `ia.…` skin paths; ArmourShop writes STONE_HOE (carry/reload) + CROSSBOW (aim) IA items and appends `skins.yml` with IA ids — no CMD registry or vanilla override patching.

## Locked rules

| Piece | Choice |
|-------|--------|
| GaG `skins.yml` | Dual format: stock `material.CMD`; submissions `ia.tfmc_submissions:{id}_carry\|reload\|aim` |
| IA materials | carry/reload = `STONE_HOE`; aim = `CROSSBOW` |
| ArmourShop | 3 IA items + shared PNG; append GaG `skins.yml` with `ia.…` only |
| Removed | `GunCmdRegistry`, stone_hoe/crossbow override patching |
| Shop | `gunskin({id})` |

**Out of step:** migrating stock skins off CMD; scoped options; multi-view bake.

## Batches

1. [01-planning-lock](./01-planning-lock.md) — docs  
2. [02-gag-ia](./02-gag-ia.md) — GaG pom + parseModel + applyModel  
3. [03-gun-writer](./03-gun-writer.md) — ArmourShop IA writer; strip CMD  
4. [04-docs-verify](./04-docs-verify.md) — checklist  

## Checkpoint

```text
docs → GaG IA → ArmourShop rewrite → verify
```

**Status:** Step 15 implemented — GaG `ia.` skins; ArmourShop GunWriter writes STONE_HOE/CROSSBOW IA items + `ia.` skins.yml; CMD dual-write removed. Pack harness green.
