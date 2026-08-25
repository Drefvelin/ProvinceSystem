# TFMCWeb (identity, tokens, Discord gate)

**Status:** Implemented.

**Repos:** `Workspace/tfmcweb/` (Bukkit plugin) · `ProvinceSystem` · `tfmc_bot` · soft-depends `Workspace/rpcharacters` · consumers `armourshop`, `drinkbuilder`, SimpleFactions

Companion: [integrations/discord-bot.md](../integrations/discord-bot.md) · [cosmetics/skins.md](../cosmetics/skins.md)

## Why

**TFMCWeb** is the single TFMC-specific gate to ProvinceSystem (like **TFMCCore** is TFMC-specific gameplay; **TLibs** stays portable). It owns identity + tokens; ArmourShop keeps pack apply; SimpleFactions has its own HTTP for map; character creation uses the same identity + scoped codes.

## Locked decisions

| Decision | Choice |
|----------|--------|
| Plugin name | **TFMCWeb** (`net.tfminecraft.TFMCWeb`) |
| Owns | HTTP client, plugin key, Discord **link**, scoped **tokens**, link **cache**, Discord **gate** (via RPCharacters freeze), ban/warn **mirrors**, admin `/web` |
| Does **not** own | Pack writing (ArmourShop/DrinkBuilder), map regen (SimpleFactions), character data (RPCharacters), Essentials ban execution |
| Discord required | Every player must link Discord **and** be in the TFMC guild to play Survival |
| Staff / helpers | Discord gate applies **only in Survival** |
| Alts | **None** - one Discord ↔ one Minecraft UUID |
| Leave Discord | **1 hour grace** - rejoin within 1h stays linked; after grace → unlink + freeze |
| Freeze | **RPCharacters** freeze reason `DISCORD_REQUIRED`; do not touch characters |
| Bans | Essentials `/tempban` / `/ban`; TFMCWeb mirrors to Discord bot |
| Warnings | `/warning` (TFMCWeb) → player chat + web store + bot DM |

## Ownership matrix

| Concern | Owner |
|---------|--------|
| Base URL, `X-Plugin-Key`, async HTTP | TFMCWeb (`ProvinceSystemGateway`) |
| UUID ↔ Discord link + guild membership + grace | ProvinceSystem identity + TFMCWeb cache + bot leave/join |
| Scoped feature codes (`skin`, `drink`, `character`, …) | ProvinceSystem + TFMCWeb `/token create <scope>` |
| Survival Discord gate freeze | TFMCWeb → RPCharacters API |
| Skin pack apply | ArmourShop (HTTP via TFMCWeb gateway) |
| Drink pack apply | DrinkBuilder (HTTP via TFMCWeb gateway) |
| Character ingest / roster | RPCharacters (HTTP via TFMCWeb gateway) |
| Essentials ban/unban | Essentials executes; TFMCWeb mirrors |
| Discord DMs / banned role / leave events | `tfmc_bot` |

Domain plugins **depend on TFMCWeb** for network/identity. They do not open raw HTTP to ProvinceSystem once migrated.

## Architecture

```mermaid
flowchart LR
  subgraph mc [Minecraft]
    TW[TFMCWeb]
    AS[ArmourShop]
    RPC[RPCharacters]
    SF[SimpleFactions]
    Ess[Essentials]
    TW --> RPC
    AS --> TW
    SF --> TW
    Ess -.->|ban events| TW
  end
  subgraph web [ProvinceSystem]
    ID[Identity API]
    SK[Skins API]
    CH[Characters API]
  end
  subgraph discord [tfmc_bot]
    Bot[Link leave join ban warn]
  end
  TW --> ID
  TW --> SK
  TW --> CH
  Bot --> ID
  Bot --> SK
```

## Identity

Link tables live under skins SQLite (`discord_links`, `discord_link_codes`) and routes under `/skins/discord/…` (identity module extraction to `/v1/identity/…` is a future cleanup).

| Route | Auth | Role |
|-------|------|------|
| `POST /skins/discord/link/start` | Plugin | Issue link code |
| `POST /skins/discord/link/complete` | Staff (bot) | Bind Discord id; reject if Discord already on another UUID |
| `POST /skins/discord/link/unlink` | Plugin | Explicit unlink |
| Guild leave/join | Staff (bot) | 1h grace on leave; clear on rejoin |

## Tokens

| Command | Scope | Redeems on |
|---------|--------|------------|
| `/token create skin` | `skin` | `/skins` |
| `/token create drink` | `drink` | `/drinks` |
| `/token create character` | `character` | `/character` |
| `/token create skin staff` | `skin_staff` | `/skins` (auto-approve) |

Rules:

- Must be Discord-linked and not past grace (Survival players).
- Codes bound to UUID.
- Session TTL: default **8h** after redeem; Remember me **30d** for character.
- Codes consumed on submit (skin/drink) or create (character).
- **Shared mint cooldown (`skin` + `drink`):** owned by **TFMCWeb** only. Character is not in the shared family.
- **Command gate:** LP `tfmcweb.token.create`; staff perm `tfmcweb.token.create.staff`.
- Skins **upload** entitlements remain ArmourShop → PS player-meta.

## Discord gate + RPCharacters freeze

1. Player in **Survival** and (not linked **or** grace expired after leave) → **freeze**.
2. Linked + in guild (or within 1h grace) → clear Discord freeze reason.
3. **Do not** change active character or delete characters.
4. Non-Survival → **no Discord gate**.

TFMCWeb on join / notice / grace tick: set or clear gate → `reevaluateFreeze(player)`.

## Bans and warnings

- **Bans:** Essentials executes; TFMCWeb enqueues moderation outbox → bot DM + **Banned** role; unban clears role.
- **Warnings:** `/warning <player> <reason>` → in-game chat + web store + bot DM.

Bot does **not** execute MC bans.

## Commands (TFMCWeb)

### Player

| Command | Action |
|---------|--------|
| `/linkdiscord` | Issue link code |
| `/unlinkdiscord` | Explicit unlink |
| `/token create skin\|drink\|character` | Scoped code |
| `/token resetcooldowns <player>` | Clear shared skin+drink mint cooldown |

### Staff

| Command | Action |
|---------|--------|
| `/web status` | API reachability, link cache stats |
| `/web reload` | Reload config |
| `/web lookup <player>` | UUID ↔ Discord / grace |
| `/web unlink <player>` | Force unlink |
| `/warning <player> <reason>` | Warn + mirror |

## Realm gateway

Per-realm HTTP gateway, `rpc_player_meta` sync, realm-scoped token policy, and scoped data queues are **shipped**. Map staff permission `tfmc.map.staff` arrives via player meta for staff map and editor gates.

## Success criteria

- Survival player without Discord link (or past leave grace) is frozen via RPCharacters; characters untouched.
- Staff in non-Survival are not Discord-gated.
- Leave Discord → 1h grace → rejoin OK; after 1h → freeze.
- No alts (one Discord ↔ one UUID).
- `/token create skin`, `drink`, and `character` work from TFMCWeb.
- Shared skin↔drink mint cooldown enforced on TFMCWeb.
- `/tempban` mirrors to Discord; `/warning` hits chat + Discord.
- ArmourShop no longer owns link/HTTP identity.

Staging verify: [STAGING.md](../../STAGING.md).
