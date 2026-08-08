# Step 11 — IGN ids, system stems, deferred delete, multi-tier armor

**Repos:** `ProvinceSystem` + `tfmc_bot` + `Workspace/armourshop`  
**Depends on:** [step-10](../step-10/00-index.md)

## Goal

Human submission ids from sanitized IGN + item name; ignore upload filenames; multi-tier armor (1–6); delete queues deferred IA only.

## Batches

1. [01-ign-id](./01-ign-id.md) — drop player_key; IGN+name ids; system stems  
2. [02-tiers-api](./02-tiers-api.md) — multi-tier armor API + storage + review sheet  
3. [03-website](./03-website.md) — Add tier UploadForm UX  
4. [04-pack-shop](./04-pack-shop.md) — pack/shop apply + delete multi-tier  
5. [05-delete-defer](./05-delete-defer.md) — delete queues IA (no force reload)  
6. [06-bot-smoke](./06-bot-smoke.md) — bot embeds + smoke  
7. [07-docs-verify](./07-docs-verify.md) — docs + checklist  

## Checkpoint

```text
IGN ids → tiers API → website → pack/shop → deferred delete → bot/smoke → docs
```
