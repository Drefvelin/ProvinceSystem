# TFMC Platform Planning

This folder is the **end-to-end playbook** for the TFMC platform: website (map + skins), Minecraft plugins, ItemsAdder packs, and the Discord bot. It is not website-only.

Docs live under `ProvinceSystem/Planning/` as the team hub. Code for other pieces sits in sibling paths under `D:\Documents\TFMC\`.

## Components

| Component | Path | Role |
|-----------|------|------|
| **ProvinceSystem** | `ProvinceSystem/` (`dev` branch) | Website + FastAPI: interactive maps, skins redeem/upload/status, SQLite |
| **SimpleFactions** | `Workspace/simplefactions/` | Map bridge: nation JSON upload, queue, regen, province lookup |
| **ArmourShop** | `Workspace/armourshop/` | Skins bridge: mint codes, pull approvals, write pack + shop YAML, LP |
| **ItemsAdder** | `Workspace/plugins/ItemsAdder/` (+ `ItemsAdder Copy/`) | Resource packs; player content goes in namespace **`tfmc_submissions`** |
| **tfmc_bot** | `tfmc_bot/` | [Red-DiscordBot](https://github.com/cog-creators/red-discordbot) on AMP: skins review (`#bot-feed`); ban/warn DMs; Discord banned-role mute (later) |

## Product lines

1. **Map** — Live borders on the web; SimpleFactions keeps the API fed; ProvinceSystem generates and serves images.  
2. **Skins** — Donator cosmetics: code → website upload → Discord approve → ArmourShop applies `tfmc_submissions`.  
3. **Discord moderation (side)** — Notify players of MC bans/warns; optional Discord role mute. In-game bans stay in-game.

Future tools (e.g. BreweryX helpers) plug into the same website shell.

## Locked decisions

- **Name:** **TFMC** = TF Minecraft. “TF” has no expansion — do not invent one (e.g. not “The Fallen”).
- **No site logins** — skins use ArmourShop-issued UUID-bound codes.
- **SQLite + disk** for skins metadata/files on the API.
- **SimpleFactions = map only**; **ArmourShop = skins pack writer**.
- **`tfmc_submissions`** pack; IA auto CMD (like armor/cooking), not legacy `tfmc_pack` CMD overrides.
- **Armor set** = 4 icons (16×16) + 2 layers (64×32); **item** / **handheld** = 16×16 PNG; **large_handheld** = 32×32 + grip preset; later **item_3d** / **shield**.
- **Naming:** `lowercase_snake_case` slugs; upload filenames ignored — [07-naming-conventions.md](./07-naming-conventions.md).
- **Staff review (Discord MVP):** posts to `#bot-feed` with **raw submission PNGs**; approve/deny via Red cog. Review-sheet attach later. Bot = [Red](https://github.com/cog-creators/red-discordbot) on AMP — [11](./11-discord-bot.md).
- **Bot** does not ban on Minecraft; Discord DMs + roles only.

## Threat model (intentional)

Public map data is low sensitivity. Still validate uploads, hash codes, and keep plugin/staff secrets server-side. Docker isolation matters more than auth theater on map endpoints.

## Reading order

**Orientation**

1. [01-current-state.md](./01-current-state.md) — ProvinceSystem `dev` baseline  
2. [02-target-architecture.md](./02-target-architecture.md) — platform shape  
3. [12-end-to-end-flows.md](./12-end-to-end-flows.md) — master player/staff journeys  

**Delivery**

4. [03-roadmap.md](./03-roadmap.md) — parallel tracks + repos  
5. [08-implementation-checklist.md](./08-implementation-checklist.md) — cross-repo build order  

**Map**

6. [09-map-system.md](./09-map-system.md) — SimpleFactions ↔ API ↔ web map  
7. [04-map-performance.md](./04-map-performance.md) — cropped overlays, hover, mobile  

**Skins**

8. [05-skins-system.md](./05-skins-system.md) — website/API contracts and kinds  
9. [07-naming-conventions.md](./07-naming-conventions.md) — slug and file stems  
10. [10-armourshop-itemsadder.md](./10-armourshop-itemsadder.md) — apply on the MC server  
11. [11-discord-bot.md](./11-discord-bot.md) — skins cog + ban role  

**Local**

12. [06-local-development.md](./06-local-development.md) — run website / bot / plugins locally  

**Build batches (plan + implement)**

13. [batches/README.md](./batches/README.md) — Step 2 API, Step 3 UI, Step 4 Discord (`tfmc_bot` + staff API)  

## Success criteria (full platform)

**Map**

- Borders update from SimpleFactions without manual image editing.
- Web map is responsive; realm size shows on hover; usable on mobile.

**Skins**

- Code → upload (armor_set / item / handheld / large_handheld) → Discord approve in `#bot-feed` (raw PNGs MVP) → ArmourShop writes pack → player can apply skin.
- Naming enforced; no shareable codes granting another UUID the cosmetic.

**Bot**

- Staff review skins in Discord.
- Ban/warn notifies via DM; banned role add/clear for channel mute; MC bans remain in-game commands.

**Ops**

- Local demo of website without live plugins.
- Deferred pack/map regen when the server is empty or on restart where required.
