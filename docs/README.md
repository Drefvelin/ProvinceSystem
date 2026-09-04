# ProvinceSystem documentation

**tfminecraft.net** is the TFMC web hub: interactive political maps, donator cosmetics (skins and drinks), character creation, and identity services backed by a FastAPI backend and Next.js frontend.

This `docs/` folder is the product and technical reference for the **ProvinceSystem** repository. Sibling repos maintain their own docs (SimpleFactions, tfmc_bot, ArmourShop, etc.).

## Reading order

1. [architecture.md](./architecture.md) - stack, routes, data layout
2. [roadmap.md](./roadmap.md) - shipped vs planned
3. Product areas (pick what you need):
   - [map/overview.md](./map/overview.md) - map platform goals and layers
   - [cosmetics/skins.md](./cosmetics/skins.md) - skins upload and review
   - [cosmetics/drinks.md](./cosmetics/drinks.md) - BreweryX drink builder
   - [characters/creator.md](./characters/creator.md) - web character creator
   - [identity/tfmcweb.md](./identity/tfmcweb.md) - Discord link, tokens, gate
4. [flows/journeys.md](./flows/journeys.md) - end-to-end player and staff journeys
5. [ops/local-dev.md](./ops/local-dev.md) - run the site locally
6. [ops/sheet-render.md](./ops/sheet-render.md) - 3D review-sheet renderer (prod deploy + smoke)
7. [ops/dev-config.md](./ops/dev-config.md) - dev-only flags and shortcuts

Schema assets: [assets/map-export-schema.json](./assets/map-export-schema.json) (SF map export contract).

## Components

| Component | Path | Role | Docs |
|-----------|------|------|------|
| **ProvinceSystem** | `ProvinceSystem/` (`dev` branch) | Website + FastAPI: maps, skins, drinks, characters, identity | This folder |
| **TFMCWeb** | `Workspace/tfmcweb/` | MC ↔ web gate: Discord link, scoped tokens, Survival Discord freeze, warn/ban mirror | [identity/tfmcweb.md](./identity/tfmcweb.md) |
| **SimpleFactions** | `Workspace/simplefactions/` | Map bridge: nation JSON upload, queue, regen, province lookup | [integrations/simplefactions.md](./integrations/simplefactions.md) |
| **ArmourShop** | `Workspace/armourshop/` | Skins pack writer + apply | [integrations/armourshop.md](./integrations/armourshop.md) |
| **DrinkBuilder** | `Workspace/drinkbuilder/` | Donator BreweryX drinks + `tfmc_drinks` IA | [cosmetics/drinks.md](./cosmetics/drinks.md) |
| **RPCharacters** | `Workspace/rpcharacters/` | Characters + freeze loop; Discord gate via freeze reason | [characters/creator.md](./characters/creator.md) |
| **ItemsAdder** | `Workspace/plugins/ItemsAdder/` | Resource packs: `tfmc_submissions`, `tfmc_armorshop`, `tfmc_drinks` | [integrations/armourshop.md](./integrations/armourshop.md) |
| **tfmc_bot** | `tfmc_bot/` | Red-DiscordBot: skins/drinks review, link, ban/warn DMs | [integrations/discord-bot.md](./integrations/discord-bot.md) |

## Locked platform decisions

- **Name:** TFMC = TF Minecraft. "TF" has no expansion.
- **No site logins** - skins, drinks, and characters use TFMCWeb-issued UUID-bound codes; redeem → API session (8h default; character Remember me = 30d).
- **Shared cosmetic mint cooldown** - skin + drink share one clock on **TFMCWeb** (not ProvinceSystem).
- **Discord link** - in-game `/linkdiscord` + Discord `/linkdiscord <code>`; required before upload.
- **SQLite + disk** for skins/drinks metadata and pending files on the API.
- **SimpleFactions = map only**; **ArmourShop = skins pack writer**; **TFMCWeb = identity + web transport**.

## Ops references

- Deployment and QA checklists: [STAGING.md](../STAGING.md)
- Release notes: [UPDATE.md](../UPDATE.md)
