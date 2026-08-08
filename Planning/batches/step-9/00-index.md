# Step 9 — Name colour, encoding, website (batch index)

**Repos:** `Workspace/armourshop` + `Workspace/tlibs` + `ProvinceSystem` backend/frontend  
**Depends on:** [step-8](../step-8/00-index.md)

Parent: plan locked decisions — plain `name` + separate `colour` / styles / `add-name`; TLibs gradients; website Apply name UX.

## Goal

Fix GUI encoding (`Â`), restore lost ArmourShop config, split name/colour in shop YAML, wire website add-name + colours/styles through API → shop writer → SkinSet.

## Batches

1. [01-encoding](./01-encoding.md) — Maven UTF-8 + `\u00A7` in Java  
2. [02-config-yaml](./02-config-yaml.md) — restore config + migrate YAML name/colour  
3. [03-skinset-colour](./03-skinset-colour.md) — SkinSet/SkinCategory + TLibs resolve  
4. [04-shop-writer](./04-shop-writer.md) — ShopSubmissionWriter + approved payload  
5. [05-api](./05-api.md) — DB/API fields  
6. [06-website](./06-website.md) — UploadForm UX  
7. [07-docs-verify](./07-docs-verify.md) — docs + checklist  

## Checkpoint

```text
encoding fixed → configs migrated → SkinSet colour → shop write → API → website preview → docs
```
