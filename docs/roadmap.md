# Roadmap

Branch: **`dev`**.

## Shipped

- **Hub** - TFMC landing, shared shell, nav into modules
- **Skins** - code → upload → Discord approve → ArmourShop `tfmc_submissions` apply (all enabled kinds including guns and books)
- **Drinks** - code → `/drinks` → Discord approve → DrinkBuilder `tfmc_drinks` + BreweryX
- **Characters** - web creator, kits, lore customise, wardrobe (MineSkin)
- **TFMCWeb gateway** - Discord link, scoped tokens, Survival gate, warn/ban mirror, realm isolation
- **Map platform** - parchment terrain, muted political layers, nation labels, pan/zoom, settlements, installations, fort ZOC, staff map gates
- **Map title editor** - staff web editor for county → empire hierarchy
- **Wars on map (partial)** - campaign route line + battle pins from SimpleFactions export
- **Auth hardening** - production startup guard, localhost internal routes, staff-gated code inspect

## Planned

| Feature | Description |
|---------|-------------|
| **Map chronicle** | Daily composited snapshot + structured event log (war declared, province taken, capital moved, …) |
| **Wealth charts** | Nation and global wealth time series over the season |
| **Occupation tint** | Contested/occupied province overlay on the web map (blocked on SimpleFactions war export) |

War gameplay and export schema live in SimpleFactions: see [`../../simplefactions/docs/wars.md`](../../simplefactions/docs/wars.md).

## Map platform detail

Goals, layer model, and SF contract summary: [map/overview.md](./map/overview.md).

Technical pipeline: [map/generation.md](./map/generation.md), [map/viewer.md](./map/viewer.md).

## Product areas (reference)

| Area | Doc |
|------|-----|
| Skins | [cosmetics/skins.md](./cosmetics/skins.md) |
| Drinks | [cosmetics/drinks.md](./cosmetics/drinks.md) |
| Characters | [characters/creator.md](./characters/creator.md) |
| Identity | [identity/tfmcweb.md](./identity/tfmcweb.md) |
| Map wars overlay | [map/wars-on-map.md](./map/wars-on-map.md) |

## Success criteria (platform)

**Map**

- Borders update from SimpleFactions without manual image editing.
- Parchment terrain + muted political layers; nation detail modals; staff map gates.
- Daily chronicle snapshots + wealth charts over the season (planned).

**Skins**

- Link Discord → code → upload → Discord approve → ArmourShop writes pack → player can apply skin.
- Naming enforced; no shareable codes granting another UUID the cosmetic.

**Drinks**

- `/token create drink` → `/drinks` → Discord approve → DrinkBuilder → BreweryX.
- Shared mint cooldown with skins on TFMCWeb.

**Bot**

- Staff review skins and drinks in Discord.
- Ban/warn notifies via DM; Banned role add/clear; MC bans remain Essentials.

**TFMCWeb**

- Single plugin HTTP gateway for domain plugins; Survival Discord gate; scoped tokens.

**Ops**

- Local demo of website without live plugins.
- Deferred pack/map regen when the server is empty or on restart where required.
