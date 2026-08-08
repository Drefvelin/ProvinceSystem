# Step 10 — Player key, prefixed ids, collision, delete, bot names

**Repos:** `ProvinceSystem` + `tfmc_bot` + `Workspace/armourshop`  
**Depends on:** [step-9](../step-9/00-index.md)

## Goal

Mint stable `player_key` on Discord link (backfill on API startup), prefix skin ids `{player_key}_{base_id}`, block same-player collisions, staff delete shop+pack, bot embeds show names.

## Batches

1. [01-player-key](./01-player-key.md) — column, mint, startup backfill  
2. [02-slug-check](./02-slug-check.md) — prefixed slug + collision API + pending names  
3. [03-website](./03-website.md) — UploadForm pre-submit check  
4. [04-bot-embeds](./04-bot-embeds.md) — names not raw ids  
5. [05-submission-delete](./05-submission-delete.md) — ArmourShop delete + API revoke  
6. [06-docs-verify](./06-docs-verify.md) — docs + checklist  

## Checkpoint

```text
player_key → prefixed slug + check → website → bot names → delete → docs
```
