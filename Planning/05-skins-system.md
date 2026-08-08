# 05 — Skins system (codes, website, API)

End-to-end design for donator texture submissions on **ProvinceSystem** (store + review state).  

**See also:** [10-armourshop-itemsadder.md](./10-armourshop-itemsadder.md) (MC apply), [11-discord-bot.md](./11-discord-bot.md) (staff UI), [07-naming-conventions.md](./07-naming-conventions.md) (Item name vs IGN-derived id), [12-end-to-end-flows.md](./12-end-to-end-flows.md) (full journey), [step-11](./batches/step-11/00-index.md) (IGN ids + multi-tier armor).

## Goals

- Donators submit **armor sets** (2D) or **weapon/tool skins** (`handheld` / `large_handheld` / `bow` / `large_bow` / `crossbow`; `item` disabled for now; 3D + shields later).
- No website logins; codes from ArmourShop bound to player UUID.
- Staff approve/deny in Discord (deny includes reason); MVP attaches **raw submission PNGs** in `#bot-feed` (review-sheet later).
- ArmourShop writes ItemsAdder namespace **`tfmc_submissions`**, shop YAML, LP permission; reloads when safe. ArmourShop owns IA `display` / model templates.

## Upload kinds

| Kind | Multipart fields (server writes fixed stems; filenames ignored) | Exact sizes | IA approach |
|------|----------------------|-------------|-------------|
| `armor_set` | Per tier (`tiers` JSON, 1–6 of `iron\|steel\|abyssalite\|mythril\|mage\|infantry`): `{tier}_helmet`, `{tier}_chestplate`, `{tier}_leggings`, `{tier}_boots`, `{tier}_layer_1`, `{tier}_layer_2` | Icons **16×16**; layers **64×32** | Like `tfmc_armor`, one SkinSet **per tier**: `generate: true` icons + `armors_rendering` with two layers |
| `handheld` | `texture` | **16×16** | Sword-style handheld parent (`generate: true`) |
| `large_handheld` | `texture` | **32×32** | `generate: false` + thin model parenting ArmourShop **grip template** JSON (`bottom` / `middle` / `top`) |
| `bow` | `texture`, `pull_0`, `pull_1`, `pull_2` | **16×16** | BOW + `generate: true` pull frames |
| `large_bow` | same four fields | **32×32** | Large bow thin models + locked display |
| `crossbow` | bow four + `charged` | **16×16** | CROSSBOW + `generate: true` |
| `item` | — | — | **Disabled** for upload (no use yet) |
| `item_3d` (later) | texture + JSON | Texture + JSON size caps (tiered); JSON must include required `display` keys | Cooking-style: `generate: false` + `model_path` |
| `shield` (later) | model + texture (one mesh) | Same 3D caps; required `display` keys | ArmourShop clones model + locked **blocking** display |

**Enabled upload kinds:** `armor_set`, `handheld`, `large_handheld`, `bow`, `large_bow`, `crossbow`.  
**`base_set` pairing** (type/tier → kind, non-armor only): see [step-8/00-index](./batches/step-8/00-index.md). Armor uses `tiers` instead — see [step-11](./batches/step-11/00-index.md).  
**Deferred:** guns (`rifles`/`pistols`/`shotguns`/`launchers`), `shields`, `helmets` BaseSets.  
**Track B4:** `item_3d` + `shield`.  
**Apply:** Pack writer [step-7](./batches/step-7/00-index.md) (armor/handheld/large); live apply + bow writers [step-8](./batches/step-8/00-index.md); multi-tier armor apply [step-11/04](./batches/step-11/04-pack-shop.md).

Upload **filenames are ignored** for identity (Step 11) — the API validates PNG size/dimensions only and writes fixed stems from the submission id (and tier, for armor) under the submission folder. See [07-naming-conventions.md](./07-naming-conventions.md).

### Grip presets (`large_handheld` only)

| `grip_preset` | Meaning | Who expands to `display` |
|---------------|---------|---------------------------|
| `bottom` | Hold near bottom of art (hammer/staff-like) | Shared grip **template** model JSON (ArmourShop ships three); thin per-skin model parents the template |
| `middle` | Hold mid-art | Same |
| `top` | Hold toward top (longsword-like) | Same |

Store preset id on the submission / `meta.json`. Do not put grip in filenames.

## High-level flow

```mermaid
sequenceDiagram
  participant Player
  participant AS as ArmourShop
  participant API
  participant Web
  participant Discord
  participant IA as ItemsAdder

  Player->>AS: /linkdiscord then /armourshop token create
  AS->>API: POST link/start then POST /skins/codes
  API-->>AS: link code / skins code once (click-to-copy in chat)
  Note over Player,Discord: Discord /linkdiscord CODE binds UUID
  AS-->>Player: show skins code
  Player->>Web: redeem code
  Web->>API: POST /skins/redeem
  Player->>Web: Item name + kind + tier(s) + any PNG files
  Web->>API: POST /skins/submissions
  API->>API: require Discord link stamp discord_user_id
  API->>Discord: notify pending plus raw PNG files
  Discord->>Player: DM submitted then approve or deny outcome
  Discord->>API: approve or deny
  AS->>API: GET /skins/plugin/approved
  API-->>AS: payload
  AS->>IA: write tfmc_submissions from templates
  AS->>AS: shop YAML LP deferred reload
```

## Code rules

| Rule | Behavior |
|------|----------|
| Bound to UUID | Issued with `player_uuid`; cosmetic always granted to that UUID |
| Share resistance | Submission stores issuer UUID; ArmourShop only grants that UUID |
| Storage | Hash of code (SHA-256); plaintext shown once in-game |
| Lifetime | Expiry (e.g. 24–72h); single redeem for upload session |
| Revocation | Staff/plugin can invalidate a code row |
| Tier limits (later) | Optional higher 3D byte caps from code / donator tier |

Eligibility (donator rank) is enforced **in ArmourShop** via permission `armourshop.token.create` (assigned with LP for donator ranks later). Command: `/armourshop token create`.

Upload requires a prior **Discord link** for that UUID ([step-5](./batches/step-5/00-index.md)).

## Discord link (MC ↔ Discord)

Durable bind so the bot can DM the player. No OAuth; no Discord fields on the website.

| Step | Who | What |
|------|-----|------|
| 1 | Player in game | `/linkdiscord` → ArmourShop `POST /skins/discord/link/start` with online UUID |
| 2 | Player in Discord | `/linkdiscord <code>` → bot `POST /skins/discord/link/complete` with their Discord user id |
| 3 | API | Stores `discord_links` row (`player_uuid` ↔ `discord_user_id`) |
| Unlink | Player | In-game `/unlinkdiscord` → `POST …/link/unlink` (plugin); or Discord `/unlinkdiscord` → `POST …/link/unlink-discord` (staff) |

Relink replaces the row for the same UUID. A Discord id already linked to another UUID is rejected. Skin upload codes are **one-time** (`redeemed_at`).

### SQLite — `discord_links` / `discord_link_codes`

| Table | Notes |
|-------|-------|
| `discord_links` | `player_uuid` unique, `discord_user_id` unique, `linked_at`, optional `minecraft_name` |
| `discord_link_codes` | one-time code hash, UUID, expiry (~10–15m), `used_at` |

### Player DMs

| Event | How |
|-------|-----|
| Submitted | Outbox `skin_notifications` (`type=submitted`); bot polls + ack |
| Approved / denied | Cog DMs after successful staff API call (deny includes reason) |

## Storage

### SQLite — `codes`

| Column | Notes |
|--------|-------|
| `id` | PK |
| `code_hash` | unique |
| `player_uuid` | issuer |
| `created_at` / `expires_at` | |
| `redeemed_at` | nullable |
| `revoked` | bool |

### SQLite — `submissions`

| Column | Notes |
|--------|-------|
| `id` | Human submission id: `{sanitized_ign}_{slugify(display_name)}` — public id for Discord, disk, pack/shop, delete/tab-complete |
| `player_uuid` | from code |
| `code_id` | FK |
| `kind` | `armor_set` \| `handheld` \| `large_handheld` \| `bow` \| `large_bow` \| `crossbow` \| later `item_3d` \| `shield` (`item` disabled) |
| `slug` | Same string as `id` (no separate field — kept as a column alias for older call sites) |
| `display_name` | human string (plain text; colours/styles are separate) |
| `add_name` | bool; when true, applying the skin keeps the base item’s display name on the result (independent of colours) |
| `name_colours` | JSON array of `#RRGGBB` or legacy `§c` / `&c` (1 = solid, 2+ = gradient); SkinSet shop look — not gated on `add_name` |
| `name_styles` | JSON array: `bold` / `italic` / `underline` / `strikethrough` |
| `grip_preset` | nullable; required when `kind=large_handheld` (`bottom` \| `middle` \| `top`) |
| `base_set` | ArmourShop BaseSet id; required for non-armor kinds, must match kind allowlist ([step-8](./batches/step-8/00-index.md)); **null/unused for `armor_set`** |
| `tiers` | JSON array of 1–6 armor tier ids (`iron\|steel\|abyssalite\|mythril\|mage\|infantry`); only set for `armor_set` |
| `status` | `pending` \| `approved` \| `denied` \| `applied` \| `revoked` |
| `deny_reason` | nullable |
| `dir_path` | relative folder under `data/skins/` |
| `created_at` / `reviewed_at` / `applied_at` | |
| `discord_message_id` | nullable |
| `discord_user_id` | from `discord_links` at submit; required for new uploads |

**No `player_key`** (Step 11 removed the mint/backfill/`player_keys` table and `discord_links.player_key`; a leftover unused column may remain on disk since SQLite can't cleanly `DROP COLUMN`). Status may be `revoked` after staff delete.

### Disk (API pending)

```text
backend/src/data/skins/{submission_id}/
  meta.json          # id, slug, kind, display_name, grip_preset?, base_set, tiers, add_name, name_colours, name_styles
  …fixed stems per kind (per-tier for armor)…
```

Compose: mount `backend/src/data` like `input` / `output`.

## Validation

- Id: see [07-naming-conventions.md](./07-naming-conventions.md) — reject before storing files. Filenames are **not** part of validation identity, only PNG bytes/dimensions are checked.
- PNG: magic bytes `\x89PNG`; max bytes (e.g. 2MB each); **exact** pixel sizes below — wrong size → **400**.
- `armor_set`: 1–6 tiers from the allowlist, each with six PNGs (fields `{tier}_helmet`, …); icons 16×16; layers 64×32; duplicate/invalid/missing tiers → **400**.
- `handheld`: one PNG (`texture`), 16×16.
- `large_handheld`: one PNG (`texture`), 32×32 + non-empty `grip_preset` in allowed set.
- `bow` / `large_bow`: four fields (`texture`, `pull_0`, `pull_1`, `pull_2`); sizes 16×16 / 32×32.
- `crossbow`: five fields (bow four + `charged`), all 16×16.
- `base_set`: required for enabled **non-armor** kinds; must match kind allowlist ([step-8](./batches/step-8/00-index.md)); reject `kind=item`. Armor uses `tiers` instead (`base_set` ignored/null).
- `item_3d` / `shield` (later): PNG + JSON; JSON parseable; required `display` keys present; combined size capped (default &lt; 30KB json+texture unless tier raises it); no path traversal in strings.
- Never accept zip archives in MVP.

## Review preview (PNG sheets)

Staff must see submissions visually without opening Blockbench.

| Phase | What the API serves | Who consumes |
|-------|---------------------|--------------|
| **Step 4 Discord MVP** | Individual on-disk PNGs via staff file download | Bot attaches raw files to `#bot-feed` |
| Step 2+ / curl | Staff-auth **contact sheet** PNG (`review-sheet`): armor = six labeled tiles; item kinds = texture + kind/grip caption | curl / later Discord when render system ships |
| Later (3D / shield) | Multi-view bake: `gui`, `ground`, first/third person hands; shield also **blocking** | Discord + site view-only viewer |

- Discord does **not** embed interactive WebGL — only static images (raw files now; pre-baked sheets later).
- Interactive orbit viewer is website-only and deferred.
- Endpoints: `GET /skins/submissions/{id}/review-sheet` (staff); staff file GET under `/skins/staff/...` (Step 4.01).

## ItemsAdder shape (ArmourShop writes)

Namespace: **`tfmc_submissions`**.

Armor set YAML mirrors `tfmc_armor`, **once per tier** (`{id}_{tier}` root key), example for one tier:

```yaml
info:
  namespace: tfmc_submissions
armors_rendering:
  {id}_{tier}:
    color: '#ffffff'
    layer_1: armor_layers/{id}_{tier}_layer_1
    layer_2: armor_layers/{id}_{tier}_layer_2
    use_color: false
items:
  {id}_{tier}_helmet:
    display_name: '{display_name} Helmet'
    permission: {id}
    resource:
      generate: true
      textures:
      - armor_icons/{id}_{tier}_helmet
    specific_properties:
      armor:
        slot: head
        custom_armor: {id}_{tier}
  # chestplate / leggings / boots likewise
```

A 2-tier submission (e.g. `iron` + `steel`) writes two independent `armors_rendering` roots and eight items, sharing one LP grant on the bare `{id}`.

`handheld`: single item; `generate: true` + `parent: item/handheld`.  
`large_handheld`: `generate: false`; thin model parents a shipped grip template (`bottom` / `middle` / `top`).  
`bow` / `large_bow` / `crossbow`: writers in [step-8/07](./batches/step-8/07-bow-crossbow-writers.md). Donor does not edit JSON for these kinds.

Do **not** add manual `custom_model_data` overrides under `minecraft` (legacy `tfmc_pack` style).

## ArmourShop apply

Full checklist and IA layout: **[10-armourshop-itemsadder.md](./10-armourshop-itemsadder.md)**. Do not duplicate long apply steps here.

## HTTP contracts

### ArmourShop → API (`X-Plugin-Key`)

| Method | Purpose |
|--------|---------|
| `POST /skins/discord/link/start` | `{ "player_uuid", "minecraft_name?" }` → `{ "code", "expires_at" }` |
| `POST /skins/discord/link/unlink` | `{ "player_uuid" }` → clear link for that UUID |
| `POST /skins/codes` | `{ "player_uuid" }` → `{ "code", "expires_at" }` |
| `GET /skins/plugin/approved?since=…` | New approvals + file URLs or multipart manifest (includes `kind`, `grip_preset`, `base_set`) |
| `POST /skins/plugin/applied` | Ack submission ids |

### Web → API (after redeem)

| Method | Purpose |
|--------|---------|
| `POST /skins/redeem` | `{ "code" }` → session |
| `POST /skins/submissions` | Multipart: `kind`, `display_name` (Item name, plain); non-armor: `base_set` (tier/type) + optional `grip_preset`; armor: `tiers` (JSON array, 1–6) + per-tier prefixed fields (legacy: unprefixed fields + `base_set` select one tier); optional `add_name`, `name_colours` / `name_styles` (JSON arrays); id is server-computed from IGN + item name (**not** a request field); filenames ignored; **requires Discord link**; rejects same-player active display_name conflict |
| `GET /skins/submissions/check` | Session: `display_name` only → `{ ok, conflicts }` |
| `GET /skins/plugin/submissions/{id}` | Plugin: metadata for delete |
| `POST /skins/plugin/submissions/{id}/revoke` | Plugin: mark `revoked` (frees slug) |
| `GET /skins/submissions/{id}` | Status for owner session |

### Discord bot → API (`X-Staff-Key`)

| Method | Purpose |
|--------|---------|
| `POST /skins/discord/link/complete` | `{ "code", "discord_user_id" }` → durable link |
| `POST /skins/discord/link/unlink-discord` | `{ "discord_user_id" }` → clear link for that Discord id |
| `GET /skins/staff/pending` | List `status=pending` (includes `discord_user_id` when set) |
| `GET /skins/staff/notifications` | Undelivered player notify rows (`submitted`, …) |
| `POST /skins/staff/notifications/{id}/ack` | Mark notification delivered |
| `GET /skins/staff/submissions/{id}/files/{filename}` | Download one PNG under that submission dir |
| `GET /skins/submissions/{id}/review-sheet` | Contact sheet (optional for Discord later) |
| `POST /skins/submissions/{id}/approve` | |
| `POST /skins/submissions/{id}/deny` | `{ "reason" }` |

### API → Discord

Bot poll: pending metadata + **raw file** downloads; buttons in `#bot-feed`; notification poll for **submitted** DMs; approve/deny handlers send outcome DMs.

## Frontend (`/skins`)

1. Enter code → redeem  
2. Choose kind (no `item`) → **fixed slots** (armor: 6 per tier; handheld/large: 1; bow/large_bow: 4; crossbow: 5)  
3. Armor: **Add tier** flow — pick from remaining allowlist tiers, one 6-slot panel per tier, ≥1 required, ≤6 total; non-armor: pick **`base_set`** filtered by kind; large also picks grip  
4. Enter **Item name** (plain text stored as `display_name`, shared across all tiers); set **colours** / **styles** / live preview anytime; optional **Apply name** is separate (keep base item name when equipped)  
5. Client-side size hints; server still enforces exact pixels + tier/`base_set` allowlists + colour/style allowlists (filenames themselves are never checked)  
6. Submit → **Submitting…** spinner until create finishes (composite `review_sheet.png` written); status page shows that sheet plus id, tiers/base set, name look, apply-name  
7. No accounts; no Discord id fields on the form  

## Discord bot

Skins review + `/linkdiscord` + player DMs: **[11-discord-bot.md](./11-discord-bot.md)** · [batches/step-5](./batches/step-5/00-index.md). In-game bans stay on the MC server.

## SimpleFactions

Unchanged for skins — map only ([09-map-system.md](./09-map-system.md)).

## Local MVP without live integrations

Seed hashed codes; upload **correct-size** fixtures; approve via curl; pull endpoint with httpie; fetch review-sheet PNG. See [06-local-development.md](./06-local-development.md).

## Security (skins-specific)

- Plugin and staff secrets only in server env  
- Rate-limit redeem and upload  
- Review sheets and previews for staff only  
- No public list-all-submissions endpoint  
