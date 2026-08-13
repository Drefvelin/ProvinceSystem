# Step 31 — Drink Builder (BreweryX donator drinks)

**Repos:** `Workspace/drinkbuilder` (new) · `Workspace/tfmcweb` · `ProvinceSystem` · `tfmc_bot` · ItemsAdder `tfmc_drinks` · BreweryX  
**Depends on:** TFMCWeb tokens ([step-17](../step-17/00-index.md)) · skins review pattern ([step-4](../step-4/00-index.md)) · Discord link  
**Playbook:** [15-drink-builder.md](../../15-drink-builder.md)

## Goal

Ship end-to-end donator drinks: shared skin↔drink mint cooldown on TFMCWeb, `/token create drink`, website brew editor, Discord review, DrinkBuilder pack + BreweryX recipe write, texture reuse/delete.

## Locked rules

See [15-drink-builder.md](../../15-drink-builder.md). Short form:

| Piece | Choice |
|-------|--------|
| Cooldown | **TFMCWeb only**; shared `skin`+`drink`; retire PS/AS mint cooldown |
| Noble | Drink yes · texture **no** |
| Gilded+ | Texture upload or reuse |
| Ingredients | Curated DrinkBuilder allowlist → catalog sync |
| IA | `tfmc_drinks` + potion `model_id` / CMD |
| Brewery | Native `itemsadder:ns:id` · `MMOItems:ID` · `customModelData` |
| Review | One submission (recipe + texture/color sheet) |
| Delete | Recipe always; texture iff refcount 0 |

## Batches (implement in order)

1. **[01-planning-lock](./01-planning-lock.md)** — Hubs + locked table (this step)  
2. **[02-tfmcweb-shared-cooldown](./02-tfmcweb-shared-cooldown.md)** — TW token cooldown config; `/token create drink`; remove PS skin mint cooldown **done**  
3. **[03-ps-drink-api](./03-ps-drink-api.md)** — Scope redeem, submissions, textures, staff approve **done**  
4. **[04-drinkbuilder-scaffold](./04-drinkbuilder-scaffold.md)** — Plugin + ingredients draft + catalog sync + CMD range **done**  
5. **[05-web-drinks-ui](./05-web-drinks-ui.md)** — `/drinks` redeem + brew form **done**  
6. **[06-bot-review](./06-bot-review.md)** — Discord pending/approve/deny for drinks **done**  
7. **[07-pack-and-brewery](./07-pack-and-brewery.md)** — `tfmc_drinks` write + `recipes.yml` merge + reload **done**  
8. **[08-delete-reuse](./08-delete-reuse.md)** — Staff delete + texture refcount + web reuse **done**  
9. **[09-docs-verify](./09-docs-verify.md)** — Docs + STAGING checklist + cutover **done**  

## Checkpoint

```text
/token create drink (ranked) → redeem /drinks
  → submit color-only (Noble) or textured (Gilded+)
  → Discord approve
  → DrinkBuilder pack (if texture) + recipes.yml
  → brewable in BreweryX with correct look
/token create skin then drink blocked by shared cooldown
staff delete drink; shared texture kept if still referenced
```

## Ingredient seed

Copy [drink-ingredients-draft.yml](../../assets/drink-ingredients-draft.yml) into DrinkBuilder `ingredients.yml` in batch 04; prune on staging.
