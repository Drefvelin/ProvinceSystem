# 10 — ArmourShop and ItemsAdder (skins apply)

How approved website submissions become **usable cosmetics** on the Minecraft server.

Website/API contracts and kinds: [05-skins-system.md](./05-skins-system.md).  
Naming: [07-naming-conventions.md](./07-naming-conventions.md).

## Role split

| Actor | Does |
|-------|------|
| ProvinceSystem | Codes, uploads, Discord review (players); staff auto-approve; catalog store |
| **TFMCWeb** | `/linkdiscord`, `/unlinkdiscord`, `/token create skin\|character\|skin staff`, notice poller, Survival Discord gate |
| **ArmourShop** | Catalog sync on load; pull approved; write IA + shop YAML; LP for **player** submissions only |
| ItemsAdder | Loads `tfmc_submissions` (players) and `tfmc_armorshop` (staff curated) |
| SimpleFactions | Nothing here |

ArmourShop is the **only** writer into live `contents/tfmc_submissions/` (player) and `contents/tfmc_armorshop/` (staff). Legacy hand-edited `tfmc_armor` stays as-is.

## Two lanes

| Lane | Token | Pack | Shop | Unlock | Review |
|------|-------|------|------|--------|--------|
| Player | `/token create skin` | `tfmc_submissions` | `ps_armor` / `ps_items` | LP `armourshop.submission.*` | Discord approve |
| Staff | `/token create skin staff` | **`tfmc_armorshop`** | Chosen `a_*` / `i_*` + **scroll** | Scroll consume | **Auto-approve** (no bot) |

Catalog (categories, skin-set keys, scrolls from AS config) syncs ArmourShop → API on load so website dropdowns stay honest — [step-18](./batches/step-18/00-index.md).

**Ops:** list scrolls under `scrolls:` in ArmourShop `config.yml`. On enable/reload ArmourShop pushes `PUT /skins/plugin/catalog` (fail-soft). Force refresh: `/armourshop catalog sync`. Staff pack pulls write **`tfmc_armorshop`** and upsert the chosen category YAML (not `ps_*`); no submission LP.

## Paths

| Piece | Location |
|-------|----------|
| Plugin source | `Workspace/armourshop/` |
| Live shop YAML | `Workspace/plugins/ArmourShop/Categories/` |
| IA contents (live) | `Workspace/plugins/ItemsAdder/contents/` |
| IA reference copy | `ItemsAdder Copy/ItemsAdder/contents/` |
| Curated armor example | `…/tfmc_armor/` (`generate: true` + layers) |
| Model-style example | `…/tfmc_cooking/` (`generate: false` + `model_path`) |
| Legacy CMD (avoid) | `…/tfmc_pack/` (vanilla overrides) |

## Apply flow

```mermaid
sequenceDiagram
  participant TW as TFMCWeb
  participant AS as ArmourShop
  participant API as ProvinceSystem
  participant IA as tfmc_submissions
  participant LP as LuckPerms
  participant Player

  Player->>TW: /linkdiscord then /token create skin
  TW->>API: POST link/start then POST /skins/codes
  Note over Player,API: Discord /linkdiscord CODE completes bind; token is click-to-copy
  AS->>API: GET /skins/plugin/approved
  API-->>AS: metadata plus files
  AS->>IA: write configs and textures
  AS->>AS: write category set YAML
  AS->>LP: grant armourshop.submission.slug
  AS->>API: POST applied
  AS->>AS: queue IA reload when safe
  Player->>AS: open shop apply skin
```

## ItemsAdder: `tfmc_submissions`

Create namespace once (scaffold empty pack), then ArmourShop appends per submission.

**Scaffold layout** (in both Copy and live `contents/`):

```text
tfmc_submissions/
  configs/
    namespace.yml              # info.namespace: tfmc_submissions
  resourcepack/assets/tfmc_submissions/
    textures/
      armor_icons/
      armor_layers/
      item/
    models/
      item/                   # grip templates in step-7.04
```

Keep Copy and live in sync when changing scaffold. Dry-run writers should target Copy (or a temp contents root) via `pack-apply.ia-contents-path`.

**Armor set** (2D, multi-tier) — mirror `tfmc_armor`, **once per tier** in the submission's `tiers` list (1–6 from `iron|steel|abyssalite|mythril|mage|infantry`):

- `armors_rendering.{id}_{tier}` with `layer_1` / `layer_2`
- Four items per tier: `{id}_{tier}_helmet|chestplate|leggings|boots` with `generate: true`, icon textures, `custom_armor: {id}_{tier}`
- Expect icons 16×16 and layers 64×32 (API already enforced)
- Shared item name / apply-name / colours across all tiers of a submission; no "amend applied set" MVP — new tiers require a new submission

**2D / weapon skins** — single item id `{slug}`, texture `{slug}`:

| Kind | Resource | Model JSON |
|------|----------|------------|
| `handheld` | `generate: true` + `parent: item/handheld` | None (IA generates) |
| `large_handheld` | `generate: false` + `model_path` | Thin per-skin JSON parenting one of **3 grip templates** (`bottom` / `middle` / `top`) |
| `bow` / `large_bow` / `crossbow` | TBD — [8.07](./batches/step-8/07-bow-crossbow-writers.md) | Pull/draw (and crossbow charged) frames |
| `book` | **BookWriter:** textures `item/{slug}_unsigned` + `item/{slug}_signed`; IA `{slug}` (`WRITABLE_BOOK`, unsigned) + `{slug}_signed` (`WRITTEN_BOOK`, signed); `generate: true` + `parent: item/generated`; shop lists `{slug}` only; sign → replace with `{slug}_signed` ([step-28](./batches/step-28/00-index.md)) | None (IA generates) |
| `item` | — | **Disabled** for player upload |

`base_set` → SkinSet `set:` mapping: [step-8/00-index](./batches/step-8/00-index.md).

Donor never hand-edits JSON for these kinds. Staff review art + preset via Discord PNG sheet.

**Item 3D / helmet 3D** ([step-13](./batches/step-13/00-index.md)) — `generate: false`, `model_path`, ship donor JSON (API-merged display) under namespace models. Missing required keys → reject at upload (API), not at apply.

**Shield** — one model + texture from donor; ArmourShop **clones** model to `{slug}_blocking` and applies locked **round** blocking `display` Δ + overrides. Do not require a second mesh upload.

**Armor 3D helmet** — per-tier flag `helmet_3d_tiers`; that tier’s helmet item uses `generate: false` + model/texture (no 16×16 icon); other pieces unchanged.

Never add new skins via manual `custom_model_data` lists in `tfmc_pack`.

### Step 7 vs Step 8

| Step | What |
|------|------|
| [step-7](./batches/step-7/00-index.md) | Pack writer + fixture harness → files on disk |
| [step-8](./batches/step-8/00-index.md) | `base_set` + pull + shop + LP + reload; bow writers in 8.07 |

## Discord link (before skins upload)

Players must bind Minecraft ↔ Discord before a website upload is accepted. **TFMCWeb** owns this after [step-17.06](./batches/step-17/06-armourshop-cutover.md).

| Command | Where | API |
|---------|-------|-----|
| `/linkdiscord` | In game (TFMCWeb) | `POST /skins/discord/link/start`; click-to-copy code |
| `/linkdiscord <code>` | Discord (tfmc_bot) | `POST /skins/discord/link/complete` |
| `/token create skin` | In game (TFMCWeb) | `POST /skins/codes` scope=skin; perm `tfmcweb.token.create` |
| `/token create skin staff` | In game (TFMCWeb) | `POST /skins/codes` scope=skin_staff; perm `tfmcweb.token.create.staff` |
| `/armourshop catalog sync` | In game (ArmourShop admin) | Push categories + scrolls → API |
| `/armourshop listtokens` / `token delete` | In game (ArmourShop admin) | List/revoke unused codes |

Batches: [step-5](./batches/step-5/00-index.md) (link), [step-6](./batches/step-6/00-index.md) (token), [step-17](./batches/step-17/00-index.md) (TFMCWeb ownership), [step-18](./batches/step-18/00-index.md) (staff curated), [step-7](./batches/step-7/00-index.md) (pack writer), [step-8](./batches/step-8/00-index.md) (live apply).

## Display ownership

| Kind | Who authors `display` / models |
|------|--------------------------------|
| `armor_set`, `handheld` | IA auto-gen (`generate: true` + parent); no shipped per-skin JSON |
| `large_handheld` | ArmourShop **grip template** JSONs + thin per-skin model (`generate: false`) |
| `bow`, `large_bow`, `crossbow` | ArmourShop writers ([8.07](./batches/step-8/07-bow-crossbow-writers.md)); pull/draw templates |
| `item_3d`, `helmet_3d` | Donor Blockbench JSON (API autofill + validate); ArmourShop ships as-is |
| `book` | BookWriter: two 16×16 covers; IA `{slug}` / `{slug}_signed`; shop `{slug}` only; on sign, swap stack to `{slug}_signed` ([step-28](./batches/step-28/00-index.md)) |
| `shield` | Donor JSON + ArmourShop blocking clone (round Δ) |
| `armor_set` 3D helmet tier | Same as `helmet_3d` under `{id}_{tier}_helmet` |

## ArmourShop shop integration

Today categories point at `ia.tfmc_armor:…` or legacy `localmodel(…)`. Player submissions should only use:

```text
ia.tfmc_submissions:{id}_{tier}_helmet   # armor, per tier
ia.tfmc_submissions:{id}                 # non-armor
```

- Two categories: **`ps_armor`** (`is-item: false`) and **`ps_items`** (`is-item: true`)  
- Non-armor set key = `{id}`; SkinSet `set: {base_set}` from upload (filtered by kind — [step-8](./batches/step-8/00-index.md))  
- Armor: **one SkinSet per tier**, key `{id}_{tier}`, `set: {tier}` — a 2-tier submission writes 2 SkinSets under `ps_armor`; `base_set` is null/unused for armor  
- SkinSet display: plain `name`, separate `colour` (string or list of `#RRGGBB` / legacy codes), optional `add-name`, optional `styles` (`bold` / `italic` / `underline` / `strikethrough`). Runtime formatting via TLibs `applyColourGradient` (+ styles). Jar sources use `\u00A7` / UTF-8 to avoid GUI `Â` mojibake.  
- Staff: `/armourshop submission delete <submissionId>` removes **all** tier SkinSets + all `tfmc_submissions` pack files for that submission id family + LP node + API `revoked`, then **enqueues** a deferred IA refresh (no immediate `iareload`/`iazip` — see Deferred reload below). Tab-complete lists human ids (`drefvelin_blue_knight`), never UUIDs.  
- `ps_items` kinds: `handheld`, `large_handheld`, `bow`, `large_bow`, `crossbow`, `item_3d`, `shield`, `helmet_3d`, `book` (Step 28)  
- **`book` shop:** SkinSet / catalog entry for `{slug}` only (writable); `{slug}_signed` exists in pack for sign-time swap, not sold separately  
- Gate with `permission: armourshop.submission.{id}` (Bukkit `hasPermission`; LP grants the node once per submission, shared across all its tiers)  
- **No scroll** on player submission sets  

Apply path stays existing `ArmorMerger.merge` + IA id (inventory item must match the chosen BaseSet).

## LuckPerms

On apply: grant issuer UUID `armourshop.submission.{id}` — one shared node for the whole submission, covering every tier.  
On revoke/deny-after-apply (if ever): remove node and optionally disable IA permission.

## Deferred reload

Same policy as map regen when possible:

1. Write files immediately.  
2. If players online → mark pending reload (`pending-reload.yml`).  
3. When `onlineCount == 0` or on restart/enable → console **`iazip`** (reload configs + regenerate resourcepack).  
4. On `ItemsAdderPackCompressedEvent` → `POST /skins/plugin/applied` (not only when files are written).

**Delete is deferred-only** (Step 11): staff delete clears pack/shop/LP files and calls API revoke synchronously, then only **enqueues** into the same `PendingReloadQueue` / `DeferredIaReloadService` used above (`requestFlush(false)` — empty-server path) — it never dispatches `iareload`/`iazip` immediately, even with staff watching. The queued refresh flushes on the next empty-server tick, the daily `force-reload-time`, or a manual force pull, exactly like a normal approve/apply pack write.

## Config (plugin)

| Key | Purpose |
|-----|---------|
| `skins-api.base-url` | ProvinceSystem (no trailing slash) |
| `skins-api.plugin-key` | `X-Plugin-Key` |
| `pack-apply.ia-contents-path` | Absolute path to ItemsAdder `contents/` (parent of namespaces). Dry-run: `ItemsAdder Copy/.../contents`; live: server `plugins/ItemsAdder/contents` |
| `pack-apply.categories-path` | Absolute path to ArmourShop `Categories/` |
| `start-points` | Armor category GUI slots |
| `item-start-points` | Item category GUI slots — **required** for item shop layout |

**Config merge note (server drop `config_new.yml`):** keep `item-start-points` from the live server config and merge into jar `config.yml` ([batch 8.04](./batches/step-8/04-shop-and-lp.md)). Keep `pack-apply.*` from the jar. Do **not** commit staging `base-url` / `plugin-key` as defaults — leave `change-me` + localhost in repo; put real values only on the server / STAGING docs.

Mirror the REST style of SimpleFactions `RestServer`, but **secrets in config.yml**, not hardcoded hashes in source.

## Local / dry run

Point ArmourShop at `ItemsAdder Copy` (or a temp contents dir), not production. Pull from local API with mock approved submissions. See [06-local-development.md](./06-local-development.md).

## Checklist

- [x] `/linkdiscord` → `link/start` (historically [step-5/04](./batches/step-5/04-armourshop-linkdiscord.md); now **TFMCWeb** [17.04](./batches/step-17/04-tfmcweb-scaffold.md))  
- [x] `/token create skin` → `POST /skins/codes` ([17.05](./batches/step-17/05-token-scopes.md); was `/armourshop token create` [step-6](./batches/step-6/00-index.md))  
- [x] ArmourShop cutover: no AS link/notice/player mint ([17.06](./batches/step-17/06-armourshop-cutover.md))  
- [x] Scaffold empty `tfmc_submissions` + `pack-apply` paths ([step-7/01](./batches/step-7/01-scaffold.md))  
- [x] Pack writer + harness ([step-7](./batches/step-7/00-index.md) 02–05)  
- [x] `base_set` API/UI + pull + shop + LP + reload + applied ([step-8](./batches/step-8/00-index.md) 01–06; live STAGING E2E boxes in [STAGING.md](../STAGING.md))  
- [x] Bow / large_bow / crossbow writers ([step-8/07](./batches/step-8/07-bow-crossbow-writers.md); staging apply unchecked)  
- [x] IGN-based submission ids; no `player_key`; upload filenames ignored ([step-11/01](./batches/step-11/01-ign-id.md))  
- [x] Multi-tier armor: 1–6 tiers per submission, one SkinSet + pack write per tier, shared LP node ([step-11/02](./batches/step-11/02-tiers-api.md), [step-11/04](./batches/step-11/04-pack-shop.md))  
- [x] Delete = deferred IA queue only, no immediate reload; tab-complete uses human ids ([step-11/05](./batches/step-11/05-delete-defer.md))  
- [x] `item_3d` + `shield` + `helmet_3d` (blocking auto; armor per-tier 3D helmet) — [step-13](./batches/step-13/00-index.md)
- [x] Guns carry/reload/aim — [step-14](./batches/step-14/00-index.md) (upload/apply); [step-15](./batches/step-15/00-index.md) (GaG IA ids; shop `gunskin({id})`)
- [x] Book: BookWriter + `{slug}` / `{slug}_signed` + shop `{slug}` only + sign swap — [step-28](./batches/step-28/00-index.md)
- [ ] Multi-view 3D review bake later

## See also

- [12-end-to-end-flows.md](./12-end-to-end-flows.md) — skin journey  
- [11-discord-bot.md](./11-discord-bot.md) — approval before pull  
- [08-implementation-checklist.md](./08-implementation-checklist.md) — Sprint / Pack track  
