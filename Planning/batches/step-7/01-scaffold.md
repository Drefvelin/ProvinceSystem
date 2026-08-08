# Batch 7.01 — `tfmc_submissions` scaffold + paths

**Plan + build:** Empty ItemsAdder namespace layout; document ArmourShop config keys for contents root.

**Repo:** `Workspace/armourshop` + ItemsAdder contents (`ItemsAdder Copy` and/or live)

**Depends on:** [00-index](./00-index.md)

## Plan

1. Define namespace **`tfmc_submissions`** folder layout under `contents/` (mirror other TFMC packs):
   - `configs/` (placeholder or empty category stub if IA requires)
   - `resourcepack` / textures / models dirs as needed for later writers
2. Scaffold once in **`ItemsAdder Copy`** (reference) and document deploy to live (`Workspace/plugins/ItemsAdder/contents/`).
3. Document ArmourShop `config.yml` keys for:
   - IA contents absolute path (dry-run → Copy or temp; live → server contents)
   - Optional categories path (used in Step 8; mention only)
4. No submission files yet — writer comes in 02+.

## Build

| File / path | Action |
|-------------|--------|
| `…/contents/tfmc_submissions/…` | create empty scaffold |
| ArmourShop `config.yml` (+ loader/Cache if implementing) | path keys |
| [10-armourshop-itemsadder.md](../../10-armourshop-itemsadder.md) | confirm layout |

## Verify

- Namespace folder exists in Copy (and live if deploying scaffold now)  
- Config key documented; plugin still builds if keys added with defaults  

**Implemented:** scaffold under Copy + `Workspace/plugins/ItemsAdder/contents/tfmc_submissions/`; ArmourShop `pack-apply.ia-contents-path` / `categories-path`.

## Out of scope

Writing armor/item YAML; grip models; API pull.
