# TFMC Platform Planning

This folder is the **end-to-end playbook** for the TFMC platform: website (map + skins), Minecraft plugins, ItemsAdder packs, and the Discord bot. It is not website-only.

Docs live under `ProvinceSystem/Planning/` as the team hub. Code for other pieces sits in sibling paths under `D:\Documents\TFMC\`.

## Components

| Component | Path | Role |
|-----------|------|------|
| **ProvinceSystem** | `ProvinceSystem/` (`dev` branch) | Website + FastAPI: interactive maps, skins redeem/upload/status, identity, SQLite |
| **TFMCWeb** | `Workspace/tfmcweb/` | Single MC ↔ web gate: Discord link, scoped tokens, Survival Discord freeze, warn/ban mirror — [13-tfmcweb.md](./13-tfmcweb.md) |
| **SimpleFactions** | `Workspace/simplefactions/` | Map bridge: nation JSON upload, queue, regen, province lookup |
| **ArmourShop** | `Workspace/armourshop/` | Skins pack writer + apply (identity/tokens owned by TFMCWeb) |
| **DrinkBuilder** | `Workspace/drinkbuilder/` | Donator BreweryX drinks + `tfmc_drinks` IA — [15-drink-builder.md](./15-drink-builder.md) / [step-31](./batches/step-31/00-index.md) (**code done**; staging [STAGING](../STAGING.md) Step 31) |
| **RPCharacters** | `Workspace/rpcharacters/` | Characters + freeze loop; Discord gate via new freeze reason |
| **ItemsAdder** | `Workspace/plugins/ItemsAdder/` (+ `ItemsAdder Copy/`) | Resource packs; player **`tfmc_submissions`**; staff curated **`tfmc_armorshop`**; drinks **`tfmc_drinks`**; legacy `tfmc_armor` hand-edited |
| **tfmc_bot** | `tfmc_bot/` | [Red-DiscordBot](https://github.com/cog-creators/red-discordbot) on AMP: skins review; link; guild leave/join; ban/warn DMs + Banned role |

## Product lines

1. **Map** — Live borders on the web; **map platform** (parchment, ink, labels, chronicle) in progress — [16-map-platform.md](./16-map-platform.md) / [step-36](./batches/step-36/00-index.md)–[46](./batches/step-46/00-index.md). **Map title editor** (staff county → empire setup) **shipped** — [17-map-title-editor.md](./17-map-title-editor.md) / [step-72](./batches/step-72/00-index.md).  
2. **Skins** — Donator cosmetics: code → website upload → Discord approve → ArmourShop applies `tfmc_submissions`. Staff curated: staff token → auto-approve → `tfmc_armorshop` + category/scroll ([step-18](./batches/step-18/00-index.md)).  
2b. **Drinks** — Donator BreweryX recipes: `/token create drink` → `/drinks` → Discord approve → DrinkBuilder writes `tfmc_drinks` + `recipes.yml` ([15](./15-drink-builder.md) / [step-31](./batches/step-31/00-index.md); **code done**). Shared mint cooldown with skins on TFMCWeb.  
3. **Identity / TFMCWeb** — Discord link + guild membership required to play Survival; scoped tokens; warn/ban mirror — [13-tfmcweb.md](./13-tfmcweb.md).  
4. **Characters** — Web creator Phase 1 **shipped + staging verified**: [14-character-creator.md](./14-character-creator.md) / [step-19](./batches/step-19/00-index.md). Kits Phase 2–3 **code+docs done**: [step-20](./batches/step-20/00-index.md) / [step-21](./batches/step-21/00-index.md). Web sheet parity **done**: [step-22](./batches/step-22/00-index.md). Kit editor polish **done**: [step-23](./batches/step-23/00-index.md). Sheet traits/attrs/background polish **done**: [step-24](./batches/step-24/00-index.md). Kit submit/deny UX **done**: [step-25](./batches/step-25/00-index.md). Kit asset sync + status **done**: [step-26](./batches/step-26/00-index.md).
5. **Discord moderation** — Notify players of MC bans/warns; guild leave grace; **Banned role add/clear done** ([step-17.07](./batches/step-17/07-warn-and-ban-mirror.md)). In-game bans stay Essentials.

**Realm / gateway (done):** Steps 32–35 — `rpc_player_meta`, realm token policy, scoped data, TFMCWeb HTTP gateway.

## Locked decisions

- **Name:** **TFMC** = TF Minecraft. “TF” has no expansion — do not invent one (e.g. not “The Fallen”).
- **No site logins** — skins, drinks, and characters use TFMCWeb-issued UUID-bound codes (`/token create skin` / `drink` / `character`); redeem → API session (**8h** default; character Remember me = 30d). Codes consumed **on submit** (skin/drink reusable until submit).
- **Shared cosmetic mint cooldown** — skin + drink share one clock on **TFMCWeb** (not ProvinceSystem).
- **Discord link** — in-game `/linkdiscord` + Discord `/linkdiscord <code>` bind UUID ↔ Discord id; required before upload; player DMs for submitted / approved / denied — [batches/step-5](./batches/step-5/00-index.md). **Owner: TFMCWeb** ([13](./13-tfmcweb.md) / [step-17](./batches/step-17/00-index.md)).
- **Discord gate** — Survival players must be linked + in guild; **1h grace** on leave; freeze via RPCharacters (characters untouched); no alts; staff/helpers non-Survival not gated — [13](./13-tfmcweb.md).
- **SQLite + disk** for skins metadata/files on the API.
- **SimpleFactions = map only**; **ArmourShop = skins pack writer**; **TFMCWeb = identity + web transport**.
- **`tfmc_submissions`** pack; IA auto CMD (like armor/cooking), not legacy `tfmc_pack` CMD overrides.
- **Armor set** = 4 icons (16×16) + 2 layers (64×32); optional per-tier **3D helmet**; **item** / **handheld** = 16×16 PNG; **large_handheld** = 32×32 + grip preset; **item_3d** / **shield** / **helmet_3d** — [step-13](./batches/step-13/00-index.md).
- **Naming:** Item name for ArmourShop; id from IGN + display name — [07-naming-conventions.md](./07-naming-conventions.md).
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

6. [16-map-platform.md](./16-map-platform.md) — map platform north star (steps 37–45)  
6b. [17-map-title-editor.md](./17-map-title-editor.md) — staff web title hierarchy editor ([step-72](./batches/step-72/00-index.md))  
7. [09-map-system.md](./09-map-system.md) — SimpleFactions ↔ API ↔ web (technical)  
8. [04-map-performance.md](./04-map-performance.md) — overlays, hover, mobile (technical)  

**Skins**

9. [05-skins-system.md](./05-skins-system.md) — website/API contracts and kinds  
10. [07-naming-conventions.md](./07-naming-conventions.md) — Item name vs filename-derived skin id  
11. [10-armourshop-itemsadder.md](./10-armourshop-itemsadder.md) — apply on the MC server  
12. [11-discord-bot.md](./11-discord-bot.md) — skins cog + ban role  

**Identity / TFMCWeb**

13. [13-tfmcweb.md](./13-tfmcweb.md) — TFMCWeb plugin, Discord gate, tokens, warn/ban mirror  
14. [batches/step-17](./batches/step-17/00-index.md) — build order to stand it up  

**Characters**

15. [14-character-creator.md](./14-character-creator.md) — web creator Phase 1 + kit / lore phases  
15. [batches/step-19](./batches/step-19/00-index.md) — Phase 1 batches  
15b. [batches/step-20](./batches/step-20/00-index.md) — Phase 2 starter kits  
15c. [batches/step-21](./batches/step-21/00-index.md) — Phase 3 kits + lore customise  

**Drinks**

15d. [15-drink-builder.md](./15-drink-builder.md) — BreweryX donator drinks  
15e. [batches/step-31](./batches/step-31/00-index.md) — Drink Builder batches  

**Local**

16. [06-local-development.md](./06-local-development.md) — run website / bot / plugins locally  

**Build batches (plan + implement)**

17. [batches/README.md](./batches/README.md) — Step 2–45: API, UI, Discord, characters, drinks, realm gateway, **map platform**

## Success criteria (full platform)

**Map**

- Borders update from SimpleFactions without manual image editing.
- Parchment terrain + muted political layers; nation detail modals; staff map gates ([16](./16-map-platform.md)).
- Daily chronicle snapshots + wealth charts over the season.

**Skins**

- Link Discord → code → upload (armor_set / item / handheld / large_handheld) → Discord approve in `#bot-feed` (raw PNGs MVP) → ArmourShop writes pack → player can apply skin.
- Naming enforced; no shareable codes granting another UUID the cosmetic; player DMs for submit / approve / deny.

**Drinks** — **code done** ([15](./15-drink-builder.md) / [step-31](./batches/step-31/00-index.md))

- `/token create drink` → `/drinks` → Discord approve → DrinkBuilder → BreweryX + optional `tfmc_drinks` texture.
- Shared mint cooldown with skins on TFMCWeb.

**Bot**

- Staff review skins and drinks in Discord.
- Ban/warn notifies via DM; **banned role add/clear done**; MC bans remain Essentials.
- Guild leave/join drives 1h grace + Survival Discord gate ([13](./13-tfmcweb.md)).

**TFMCWeb**

- Single plugin HTTP gateway for domain plugins; Survival Discord gate; scoped tokens.
- Steps 32–35 realm isolation **done** (code).

**Ops**

- Local demo of website without live plugins.
- Deferred pack/map regen when the server is empty or on restart where required.
