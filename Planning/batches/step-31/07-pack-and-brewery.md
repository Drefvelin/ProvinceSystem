# Step 31.07 — Pack write + BreweryX merge

**Repos:** `Workspace/drinkbuilder` · ItemsAdder · BreweryX · ProvinceSystem

## Goal

On approve (and pack-ready): write `tfmc_drinks` potion+CMD; merge recipe into BreweryX `recipes.yml`; reload.

## Plan

1. Pull approved / `pending_pack` drinks from PS.
2. New texture: allocate CMD; write IA YAML + PNG under `contents/tfmc_drinks/`; persist CMD; deferred IA reload.
3. Build recipe YAML key = submission `id`.
4. Merge into `recipes.yml`; set `customModelData` or `color`; ingredients as allowlist tokens; **no** player commands.
5. Trigger BreweryX `/brew reload`.
6. Ack applied to PS (immediate for color-only; after IA zip for new textures).
7. Color-only: skip IA write; recipe uses `color` only.

## Verify

- Textured drink: potion in-game shows custom look after pack.  
- Color-only: Brewery recipe works with tint.  
- IA ingredient `itemsadder:tfmc_cooking:grape` accepted when cooking pack present.

## Done when

Approved drink is brewable end-to-end on staging.

## Status

**Done** (implementation):

### ProvinceSystem
- `GET /drinks/plugin/pending-apply`
- `GET /drinks/plugin/submissions/{id}/files/{filename}`
- `POST /drinks/plugin/textures/{id}/cmd`
- `POST /drinks/plugin/applied`

### DrinkBuilder
- `/drinkbuilder pack pull [force]`
- `IaDrinksWriter` · `RecipesYmlMerger` · `PackPullRunner` · `DeferredDrinkIaReload`
- Config: `ia-reload-delay-seconds`
