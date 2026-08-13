# Step 31.04 — DrinkBuilder plugin scaffold + ingredients

**Repos:** `Workspace/drinkbuilder` (new Paper plugin)

## Goal

Scaffold plugin; ship first-draft `ingredients.yml`; catalog sync to PS; CMD range + paths config.

## Plan

1. Create plugin (TLibs/Paper pattern like ArmourShop lite): config, API client, reload command.
2. Seed `ingredients.yml` from [drink-ingredients-draft.yml](../../assets/drink-ingredients-draft.yml).
3. `effects-blacklist.yml` (port old DrinkBuilder list).
4. Config keys: PS base URL + plugin key; BreweryX data folder; IA `contents/tfmc_drinks` path; CMD min/max; reserved prefix.
5. `PUT` catalog endpoint on PS (ingredients + maybe version); `/drinkbuilder catalog sync`.
6. Player join optional: push `allow_drink_texture` from LP (Gilded+) for redeem/submit.
7. Empty `tfmc_drinks` IA namespace scaffold (configs + textures folder).

## Verify

- [x] Sync → website/API can list ~70 ingredients (full draft seeded; prune in ops).
- [x] Reload picks pruned YAML.
- [x] Plugin loads; catalog sync works; CMD allocator stub exists.

## Done when

- [x] Plugin loads; catalog sync works; CMD allocator stub exists.
