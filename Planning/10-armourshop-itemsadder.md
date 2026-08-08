# 10 — ArmourShop and ItemsAdder (skins apply)

How approved website submissions become **usable cosmetics** on the Minecraft server.

Website/API contracts and kinds: [05-skins-system.md](./05-skins-system.md).  
Naming: [07-naming-conventions.md](./07-naming-conventions.md).

## Role split

| Actor | Does |
|-------|------|
| ProvinceSystem | Codes, uploads, Discord review state, file store |
| **ArmourShop** | `/linkdiscord`; `/armourshop token create`; pull approved; write IA + shop YAML; LP; deferred reload |
| ItemsAdder | Loads `tfmc_submissions` after files exist / pack rebuild |
| SimpleFactions | Nothing here |

ArmourShop is the **only** writer into live `contents/tfmc_submissions/` for player skins.

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
  participant AS as ArmourShop
  participant API as ProvinceSystem
  participant IA as tfmc_submissions
  participant LP as LuckPerms
  participant Player

  Player->>AS: /linkdiscord then /armourshop token create
  AS->>API: POST link/start then POST /skins/codes
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

**Armor set** (2D) — mirror `tfmc_armor`:

- `armors_rendering.{slug}` with `layer_1` / `layer_2`
- Four items: `{slug}_helmet|chestplate|leggings|boots` with `generate: true`, icon textures, `custom_armor: {slug}`
- Expect icons 16×16 and layers 64×32 (API already enforced)

**2D / weapon skins** — single item id `{slug}`, texture `{slug}`:

| Kind | Resource | Model JSON |
|------|----------|------------|
| `handheld` | `generate: true` + `parent: item/handheld` | None (IA generates) |
| `large_handheld` | `generate: false` + `model_path` | Thin per-skin JSON parenting one of **3 grip templates** (`bottom` / `middle` / `top`) |
| `bow` / `large_bow` / `crossbow` | TBD — [8.07](./batches/step-8/07-bow-crossbow-writers.md) | Pull/draw (and crossbow charged) frames |
| `item` | — | **Disabled** for player upload |

`base_set` → SkinSet `set:` mapping: [step-8/00-index](./batches/step-8/00-index.md).

Donor never hand-edits JSON for these kinds. Staff review art + preset via Discord PNG sheet.

**Item 3D** (later) — cooking style: `generate: false`, `model_path`, ship donor JSON under namespace models. JSON must already contain required `display` keys (`gui`, `ground`, `fixed`, `firstperson_*`, `thirdperson_*`, and `head` when relevant). Soft scale warnings optional; missing keys → reject at upload (API), not at apply.

**Shield** (later) — one model + texture from donor; ArmourShop **clones** model and applies locked **blocking** `display` (and any IA blocking override). Do not require a second mesh upload.

Never add new skins via manual `custom_model_data` lists in `tfmc_pack`.

### Step 7 vs Step 8

| Step | What |
|------|------|
| [step-7](./batches/step-7/00-index.md) | Pack writer + fixture harness → files on disk |
| [step-8](./batches/step-8/00-index.md) | `base_set` + pull + shop + LP + reload; bow writers in 8.07 |

## Discord link (before skins upload)

Players must bind Minecraft ↔ Discord before a website upload is accepted.

| Command | Where | API |
|---------|-------|-----|
| `/linkdiscord` | In game (player online) | `POST /skins/discord/link/start`; click-to-copy code |
| `/linkdiscord <code>` | Discord (tfmc_bot) | `POST /skins/discord/link/complete` |
| `/armourshop token create` | In game | `POST /skins/codes`; click-to-copy; perm `armourshop.token.create` |

Batches: [step-5](./batches/step-5/00-index.md) (link), [step-6](./batches/step-6/00-index.md) (token), [step-7](./batches/step-7/00-index.md) (pack writer), [step-8](./batches/step-8/00-index.md) (live apply).

## Display ownership

| Kind | Who authors `display` / models |
|------|--------------------------------|
| `armor_set`, `handheld` | IA auto-gen (`generate: true` + parent); no shipped per-skin JSON |
| `large_handheld` | ArmourShop **grip template** JSONs + thin per-skin model (`generate: false`) |
| `bow`, `large_bow`, `crossbow` | ArmourShop writers ([8.07](./batches/step-8/07-bow-crossbow-writers.md)); pull/draw templates |
| `item_3d`, `shield` | Donor Blockbench JSON (required keys); ArmourShop adds shield blocking clone only |

## ArmourShop shop integration

Today categories point at `ia.tfmc_armor:…` or legacy `localmodel(…)`. Player submissions should only use:

```text
ia.tfmc_submissions:{slug}_helmet
ia.tfmc_submissions:{slug}
```

- Two categories: **`ps_armor`** (`is-item: false`) and **`ps_items`** (`is-item: true`)  
- Set key = `{slug}`; SkinSet `set: {base_set}` from upload (filtered by kind — [step-8](./batches/step-8/00-index.md))  
- `ps_items` kinds: `handheld`, `large_handheld`, `bow`, `large_bow`, `crossbow`  
- Gate with `permission: armourshop.submission.{slug}` (Bukkit `hasPermission`; LP grants the node)  
- **No scroll** on player submission sets  

Apply path stays existing `ArmorMerger.merge` + IA id (inventory item must match the chosen BaseSet).

## LuckPerms

On apply: grant issuer UUID `armourshop.submission.{slug}`.  
On revoke/deny-after-apply (if ever): remove node and optionally disable IA permission.

## Deferred reload

Same policy as map regen when possible:

1. Write files immediately.  
2. If players online → mark pending reload (`pending-reload.yml`).  
3. When `onlineCount == 0` or on restart/enable → console **`iazip`** (reload configs + regenerate resourcepack).  
4. On `ItemsAdderPackCompressedEvent` → `POST /skins/plugin/applied` (not only when files are written).

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

- [x] `/linkdiscord` → `link/start` ([step-5/04](./batches/step-5/04-armourshop-linkdiscord.md))  
- [x] `/armourshop token create` → `POST /skins/codes` + click-to-copy ([step-6](./batches/step-6/00-index.md))  
- [x] Scaffold empty `tfmc_submissions` + `pack-apply` paths ([step-7/01](./batches/step-7/01-scaffold.md))  
- [x] Pack writer + harness ([step-7](./batches/step-7/00-index.md) 02–05)  
- [x] `base_set` API/UI + pull + shop + LP + reload + applied ([step-8](./batches/step-8/00-index.md) 01–06; live STAGING E2E boxes in [STAGING.md](../STAGING.md))  
- [x] Bow / large_bow / crossbow writers ([step-8/07](./batches/step-8/07-bow-crossbow-writers.md); staging apply unchecked)  
- [ ] `item_3d` + `shield` (blocking auto) later  

## See also

- [12-end-to-end-flows.md](./12-end-to-end-flows.md) — skin journey  
- [11-discord-bot.md](./11-discord-bot.md) — approval before pull  
- [08-implementation-checklist.md](./08-implementation-checklist.md) — Sprint / Pack track  
