# Character creator

Web + RPCharacters character creation, kits, lore customise, and wardrobe.

**Status:** Phases 1-4 **implemented** (staging verification ongoing).

**Repos:** `Workspace/rpcharacters/` · `ProvinceSystem` · `Workspace/tfmcweb/` · `frontend` · (kits) `Workspace/armourshop/`

**Depends on:** TFMCWeb identity + `/token create character` ([identity/tfmcweb.md](../identity/tfmcweb.md)).

## Why

Donators (and later all players) create and manage RP characters on the website with the **same rules as in-game** `/rpcharacter create` / menu. Creation stages sync from the server so YAML edits update the site after reload. Auth stays **in-game tokens** (no website accounts).

## Phases

| Phase | Name | In scope |
|-------|------|----------|
| **1** | Web character creator | Attribute point-buy; creation catalog sync; redeem + Remember me; create + list alive/dead; `/character` UI |
| **2** | Kits in RPCharacters | `kits.yml`; `KitService`; `/rpcharacter kit <id>`; per-kit cooldown + once-per-character |
| **3** | Kit item customise | Character → Kits → Edit editable items; player skins → `ps_items`; RPC lore; hold claim while `pending_skin` |
| **3b** | Web character sheet | Read-only identity sheet matching in-game summary |
| **3c** | Sheet parity polish | Personality/evil traits, merged attrs, profession EXP, writable-book background |
| **3d-f** | Kit UX polish | Submit/deny UX, asset sync, customise visibility, claim AS gate |
| **4** | Character skin wardrobe | Mojang-signed player skins (base + rank extras + masked); web manage / in-game swap |

## Locked decisions (Phase 1)

### Auth

| Decision | Choice |
|----------|--------|
| Proof of account | In-game `/token create character` (UUID-bound, Discord-eligible) |
| Code lifetime | Consumed **on successful create/submit**; may re-redeem until consumed |
| After redeem | API **session** Bearer - default **8h**; Remember me **30d** |
| Storage | sessionStorage if not remembered; localStorage if Remember me |
| Website accounts | **None** |

### Attribute point-buy

| Rule | Value |
|------|-------|
| Attributes | strength, dexterity, constitution, intelligence, wisdom, charisma |
| Pool | **12** points - must spend exactly 12 |
| Max rank per attribute at creation | **+2** |
| Cost for *n*-th rank in one attribute | **n** points (1st → 1, 2nd → 2) |
| Sync | Formula + caps exported in creation catalog |

Personality / physical / celestial / story traits stay **selection** stages.

### Creation catalog sync

RPCharacters on enable/reload **PUT**s a full-replace snapshot to ProvinceSystem (stage order, options, validation rules, slot limits, attribute formula). Web **GET**s snapshot for the wizard.

### Characters API + ownership

| Concern | Owner |
|---------|--------|
| Source of truth for living characters | **RPCharacters** |
| Web sessions / create requests | **ProvinceSystem** Characters API |
| Apply web creates into RPC | RPCharacters pull/ingest |
| Identity + mint | TFMCWeb + Discord link |

### Product / UI

| Decision | Choice |
|----------|--------|
| Nav | **Character** tab beside Map and Skins |
| Landing | Session → list characters (alive + dead); CTA to create if free slot |
| Create | Multi-step wizard from synced stages |
| Slots | Enforce synced limits (default 3; Gilded 4; Ascended/Legacy 5; hard cap 10) |
| Dual path | In-game `/rpcharacter create` remains; both paths share validation |

## Phase 2 - kits (summary)

Configurable kits in `plugins/RPCharacters/kits.yml`:

| Rule | Choice |
|------|--------|
| Claim command | `/rpcharacter kit <kitId>` with that character **active** |
| Cooldown | **Per kit** (player UUID × kit id) |
| Once per character | Per kit `once-per-character: true|false` |
| Sync | All kit defs + per-character status → ProvinceSystem |

Starter kit `starter` replaces legacy ConditionalEvents `/tfmc starter`.

## Phase 3 - kit item customise (summary)

Customise **editable** kit lines on the website (character detail → Kits → Edit). Texture via player skins pipeline → `ps_items`; lore via RPCharacters. Block claim while skin pending approval or slug missing on ArmourShop.

**Skin tokens:** uploading a new kit texture (or book covers / 3D model) requires a **skin mint token** redeemed on `/skins`, sent as `X-Skin-Session` alongside the character login token. Picking an already-**applied** skin from your account does not consume a new token. The character web code is login only.

Applied skins appear in the kit editor pick list and can be attached to any character with the same `base_set`.

Editable templates: `2d-template` (required), optional `3d-template`. Book journals use kind `book` (unsigned + signed PNGs).

## Phase 4 - wardrobe (summary)

| Concern | Choice |
|---------|--------|
| Slots | `base` + `masked` + up to 2 extras by rank |
| PNG | **64×64 only**; MineSkin v2 sign |
| Apply | Join + character switch; `/rpcharacterwardrobe` in-game |
| Web | Standing frames; modal preview |

Separate from item `/skins` and RP identity masks.

## Architecture

```mermaid
flowchart LR
  subgraph mc [Minecraft]
    TW[TFMCWeb]
    RPC[RPCharacters]
    TW -->|mint character code| API
    RPC -->|PUT catalog + kits| API
    RPC -->|pull / apply creates| API
  end
  subgraph web [ProvinceSystem]
    API[Characters + kits + sessions]
    FE["/character"]
    FE -->|Bearer session| API
  end
  Player -->|/token create character| TW
  Player -->|redeem| FE
```

## Out of scope

- Website passwords / OAuth
- Rewriting non-attribute selection stages into sheets (unless redesigned later)

Operator checklist: [STAGING.md](../../STAGING.md).
