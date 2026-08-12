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
| **RPCharacters** | `Workspace/rpcharacters/` | Characters + freeze loop; Discord gate via new freeze reason |
| **ItemsAdder** | `Workspace/plugins/ItemsAdder/` (+ `ItemsAdder Copy/`) | Resource packs; player **`tfmc_submissions`**; staff curated **`tfmc_armorshop`**; legacy `tfmc_armor` hand-edited |
| **tfmc_bot** | `tfmc_bot/` | [Red-DiscordBot](https://github.com/cog-creators/red-discordbot) on AMP: skins review; link; guild leave/join; ban/warn DMs + Banned role |

## Product lines

1. **Map** — Live borders on the web; SimpleFactions keeps the API fed; ProvinceSystem generates and serves images.  
2. **Skins** — Donator cosmetics: code → website upload → Discord approve → ArmourShop applies `tfmc_submissions`. Staff curated: staff token → auto-approve → `tfmc_armorshop` + category/scroll ([step-18](./batches/step-18/00-index.md)).  
3. **Identity / TFMCWeb** — Discord link + guild membership required to play Survival; scoped tokens; warn/ban mirror — [13-tfmcweb.md](./13-tfmcweb.md).  
4. **Characters** — Web creator Phase 1 **shipped + staging verified**: [14-character-creator.md](./14-character-creator.md) / [step-19](./batches/step-19/00-index.md). Kits Phase 2–3 **code+docs done**: [step-20](./batches/step-20/00-index.md) / [step-21](./batches/step-21/00-index.md). Web sheet parity **done**: [step-22](./batches/step-22/00-index.md). Kit editor polish **done**: [step-23](./batches/step-23/00-index.md). Sheet traits/attrs/background polish **done**: [step-24](./batches/step-24/00-index.md).  
5. **Discord moderation** — Notify players of MC bans/warns; guild leave grace; optional Discord role mute. In-game bans stay Essentials.

Future tools (BreweryX helpers, character Phases 2–4) plug into the same website shell + TFMCWeb.

## Locked decisions

- **Name:** **TFMC** = TF Minecraft. “TF” has no expansion — do not invent one (e.g. not “The Fallen”).
- **No site logins** — skins and characters use TFMCWeb-issued UUID-bound codes (`/token create skin` / `character`); redeem → API session (character Remember me = 30d).
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

6. [09-map-system.md](./09-map-system.md) — SimpleFactions ↔ API ↔ web map  
7. [04-map-performance.md](./04-map-performance.md) — cropped overlays, hover, mobile  

**Skins**

8. [05-skins-system.md](./05-skins-system.md) — website/API contracts and kinds  
9. [07-naming-conventions.md](./07-naming-conventions.md) — Item name vs filename-derived skin id  
10. [10-armourshop-itemsadder.md](./10-armourshop-itemsadder.md) — apply on the MC server  
11. [11-discord-bot.md](./11-discord-bot.md) — skins cog + ban role  

**Identity / TFMCWeb**

12. [13-tfmcweb.md](./13-tfmcweb.md) — TFMCWeb plugin, Discord gate, tokens, warn/ban mirror  
13. [batches/step-17](./batches/step-17/00-index.md) — build order to stand it up  

**Characters**

14. [14-character-creator.md](./14-character-creator.md) — web creator Phase 1 + kit / lore phases  
15. [batches/step-19](./batches/step-19/00-index.md) — Phase 1 batches  
15b. [batches/step-20](./batches/step-20/00-index.md) — Phase 2 starter kits  
15c. [batches/step-21](./batches/step-21/00-index.md) — Phase 3 kits + lore customise  

**Local**

16. [06-local-development.md](./06-local-development.md) — run website / bot / plugins locally  

**Build batches (plan + implement)**

17. [batches/README.md](./batches/README.md) — Step 2–21: API, UI, Discord, pack writer, plugin apply, 3D/guns, TFMCWeb, staff skins, character creator, starter kits, lore-item editor

## Success criteria (full platform)

**Map**

- Borders update from SimpleFactions without manual image editing.
- Web map is responsive; realm size shows on hover; usable on mobile.

**Skins**

- Link Discord → code → upload (armor_set / item / handheld / large_handheld) → Discord approve in `#bot-feed` (raw PNGs MVP) → ArmourShop writes pack → player can apply skin.
- Naming enforced; no shareable codes granting another UUID the cosmetic; player DMs for submit / approve / deny.

**Bot**

- Staff review skins in Discord.
- Ban/warn notifies via DM; banned role add/clear for channel mute; MC bans remain Essentials.
- Guild leave/join drives 1h grace + Survival Discord gate ([13](./13-tfmcweb.md)).

**TFMCWeb**

- Single plugin key / HTTP client for identity + tokens; ArmourShop/Factions/characters consume it.
- Survival unlinked (or past grace) → RPCharacters freeze; characters untouched.

**Ops**

- Local demo of website without live plugins.
- Deferred pack/map regen when the server is empty or on restart where required.
