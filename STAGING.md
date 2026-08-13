# Staging stack (AMP host / SSH)

Temporary ProvinceSystem next to production for Discord bot testing. Uses ports **18001** (API) and **13001** (UI). Production `docker-compose.yml` (8000/3000) is unchanged.

(If an older doc said 8001: that port is often already in use on the host.)

Data lives only under this clone (`backend/src/data`, etc.).

## Prerequisites

- Docker + Docker Compose on the host
- Git access to this repo

## Update staging clone (every pull)

Staging boxes should track the remote branch **exactly**. Do **not** keep local edits (including `chmod +x` dirtying the scripts — that makes `git pull` fail with “local changes would be overwritten”).

Use your staging path (`~/ProvinceSystem` or `~/tfmc-staging`). Checkout the branch you run on staging (**`site-rework`**). After `reset --hard`, always `chmod +x` again before running scripts.

```bash
cd ~/ProvinceSystem
git fetch origin
git checkout site-rework
git reset --hard origin/site-rework
chmod +x scripts/staging-*.sh
```

`reset --hard` discards any local chmod/script tweaks so the tree matches GitHub. Then set execute bits again before running the scripts.

## Start (SSH)

First-time clone:

```bash
git clone <ProvinceSystem-git-url> ~/tfmc-staging
cd ~/tfmc-staging
git checkout site-rework
chmod +x scripts/staging-*.sh
./scripts/staging-down.sh
./scripts/staging-up.sh
curl -s http://127.0.0.1:18001/ping
```

`staging-down.sh` clears a failed partial up before `staging-up.sh`.

After later updates: use **Update staging clone** above, then:

```bash
./scripts/staging-down.sh
./scripts/staging-up.sh
curl -s http://127.0.0.1:18001/ping
```

Expected ping body: `{"ok":true}` (JSON). An HTML 404 means something else owns that port.

Stop later:

```bash
./scripts/staging-down.sh
```

## Red bot (`skinsreview` config.yml)

On the same machine as AMP/Red:

```yaml
api_base_url: "http://127.0.0.1:18001"
staff_key: "dev-staff-key"
bot_feed_channel_id: YOUR_BOT_FEED_CHANNEL_ID
poll_interval_seconds: 60
```

Then in Discord: `-reload skinsreview` → `/skinsreview ping`.  
Enable slash if needed: `!slash enable skinsreview` then `!slash sync`.

## Step 17 — TFMCWeb identity + Discord gate (current)

**Playbook:** [Planning/13-tfmcweb.md](./Planning/13-tfmcweb.md) · full checklist [Planning/batches/step-17/08-docs-verify.md](./Planning/batches/step-17/08-docs-verify.md).

### Deploy

1. ProvinceSystem API on staging (identity grace + moderation outbox).
2. `Builds/TFMCWeb/tfmcweb-*.jar` with `plugins/TFMCWeb/config.yml`:
   - `api.base-url`: `http://127.0.0.1:18001`
   - `api.plugin-key`: same as API `PLUGIN_API_KEY`
   - **`player-meta`** ladders synced with donator groups (see Step 32) — required on **lobby** as well as survival
3. ArmourShop cutover jar (pack apply only; `skins-api` still for approved packs).
4. RPCharacters with Discord gate freeze API.
5. Bot: skinsreview `guild_id` + leave/join; minecraftban `config.yml` (`api_base_url`, `staff_key`, `banned_role_id` — role id required for role checks).
6. LuckPerms: `tfmcweb.token.create` (migrate from `armourshop.token.create`); staff `tfmcweb.warning`.

### Link + mint (operator)

1. Survival: `/linkdiscord` (TFMCWeb) → Discord `/linkdiscord code:<CODE>` → notices via TFMCWeb poller.
2. `/token create skin` → click-copy → redeem + upload on `http://127.0.0.1:13001/skins`.
   - Non-ranked / defaults: mint rejected (“cannot create skin tokens”).
   - Ranked: KindPicker filtered by `skin_kinds`; armor 3D helmet only if `allow_armor_3d_helmet`.
   - Second mint within cooldown → rejected with remaining wait.
3. Approve/Deny in `#bot-feed` → outcome DMs (skinsreview).
4. Optional: `/token create character` → redeem on `http://127.0.0.1:13001/character` (Remember me optional; see Step 19).
5. `/armourshop token create` redirects to `/token create skin` (obsolete AS mint).

If already linked, `/linkdiscord` does not mint a new code. Use `/unlinkdiscord` (in-game or Discord) to relink. One Discord ↔ one UUID.

### Gate / grace / moderation smoke

- Survival unlinked → frozen; message points to `/linkdiscord`. Non-Survival staff not gated.
- Leave guild → ≤1h play; rejoin clears; after expire → freeze.
- `/warning` + `/tempban` (or CE `/tfmc ban`) → Discord DM + Banned role; `/unban` clears role.

Checkpoint: see [08-docs-verify.md](./Planning/batches/step-17/08-docs-verify.md).

## Step 18 — Staff curated skins

**Playbook:** [Planning/batches/step-18/00-index.md](./Planning/batches/step-18/00-index.md) · checklist [Planning/batches/step-18/06-docs-verify.md](./Planning/batches/step-18/06-docs-verify.md).

**Code:** 18.01–18.07 done (API catalog + staff codes, TFMCWeb mint, ArmourShop `tfmc_armorshop` apply, web dropdowns, display-only staff ids, `/armourshop skin delete`). Tick boxes below on live staging.

### Deploy

1. Latest ProvinceSystem API (staff submit + catalog store).
2. `Builds/ArmourShop/armourshop-*.jar` — catalog sync + staff pack/shop path.
3. `Builds/TFMCWeb/tfmcweb-*.jar` — `/token create skin staff`.
4. Frontend with staff category/scroll UI on `/skins`.
5. ArmourShop `config.yml`: `scrolls:` list (`id` + `label`); `skins-api` + `pack-apply.*` as for Step 8.
6. ItemsAdder: `contents/tfmc_armorshop/` scaffold present (beside `tfmc_submissions`).
7. LuckPerms: grant **`tfmcweb.token.create.staff`** to staff who mint curated codes (does not require `tfmcweb.token.create`).

### Operator checklist

- [ ] Scrolls listed in AS `config.yml`; enable (or `/armourshop catalog sync`) syncs catalog — `GET /skins/catalog` shows categories + scrolls
- [ ] `/token create skin staff` → redeem on `/skins` → category + scroll dropdowns visible
- [ ] Staff armor → pack under `tfmc_armorshop` + chosen `a_*` category YAML with scroll; usable in shop via scroll
- [ ] Staff gun → IA + GaG `skins.yml` + item category entry
- [ ] Player `/token create skin` → still Discord review + `tfmc_submissions` / `ps_*` + LP
- [ ] No bot / `#bot-feed` post for staff submit
- [ ] Staff skin id is display-slug only (no MC IGN); reusing an existing category key is rejected as invalid
- [ ] `/armourshop skin delete <id>` clears `tfmc_armorshop` + chosen category YAML + API row (legacy `tfmc_armor` untouched)
- [ ] `/armourshop submission delete` refuses staff ids; player lane still clears `ps_*` + LP

Checkpoint:

```text
catalog sync → /token create skin staff → redeem + dropdowns → auto-approve
  → pack pull → tfmc_armorshop + category/scroll → shop usable
  → skin delete clears pack+category (not tfmc_armor)
```

## Step 19 — Web character creator (Phase 1)

**Playbook:** [Planning/14-character-creator.md](./Planning/14-character-creator.md) · batches [Planning/batches/step-19/00-index.md](./Planning/batches/step-19/00-index.md) · checklist [06-docs-verify](./Planning/batches/step-19/06-docs-verify.md).

**Code:** 19.01–19.06 done. **Staging verified** (operator). Kits Phase 2–3: [step-20](./Planning/batches/step-20/00-index.md) / [step-21](./Planning/batches/step-21/00-index.md) **code+docs done**; operator ticks under Step 20–21.

### Deploy

1. ProvinceSystem API on staging (characters routes + DB migrate for `creation_catalog` / `character_creates` / `character_roster` / `character_player_meta`).
2. `Builds/RPCharacters/` jar with `plugins/RPCharacters/config.yml` `characters-api.base-url` / `plugin-key` (same plugin key as skins). Reload pushes creation catalog; join or `/rpcharacter pending sync` applies web creates; roster push keeps the site list current and (when the player is online) syncs LP-based `max_alive_characters` for Create enablement, plus `real_age_set` / `eighteen` once age stages were completed in-game.
3. Frontend with `/character` (+ `/character/create`); `NEXT_PUBLIC_API_URL` → staging API (`http://127.0.0.1:18001`).
4. `Builds/TFMCWeb/tfmcweb-*.jar` — `/token create character` mint message points at site redeem. LP: `tfmcweb.token.create` (character scope).

**API smokes (from `backend/`):** `python scripts/character_session_smoke.py`, `creation_catalog_smoke.py`, `character_ingest_smoke.py`.

### Locked (do not reinvent on staging)

- Token single-use → session; default **1h**; Remember me **30d**; Log out revokes  
- Attribute sheet: pool / max-rank / costs from synced catalog (`stages.yml`)  
- No knife / Mojang skin UI required for Phase 1  

### Operator checklist

- [x] `/token create character` → redeem on `/character` (1h default)
- [x] Remember me → still logged in after browser restart (within 30d)
- [x] Log out → must mint a new token
- [x] In-game attribute sheet: spend exact pool per catalog; costs match shipped formula
- [x] Catalog sync after RPC reload updates web options
- [x] Web create → character in RPCharacters + listed on site
- [x] Dead characters visible on site
- [x] Slot limit enforced
- [x] No knife / player-skin UI required

Checkpoint:

```text
attribute sheet → catalog sync → redeem + Remember me
  → web wizard → RPC ingest → /character list alive/dead
```

## Step 20 — Starter kits (Phase 2)

**Playbook:** [Planning/14-character-creator.md](./Planning/14-character-creator.md) Phase 2 · batches [Planning/batches/step-20/00-index.md](./Planning/batches/step-20/00-index.md) · claim cutover [21.06](./Planning/batches/step-21/06-kit-claim-command.md).

**Code:** 20.01–20.03 done; claim cutover [21.06](./Planning/batches/step-21/06-kit-claim-command.md); multi-kit generalised in [21.08](./Planning/batches/step-21/08-kits-yml-and-kit-service.md) (`kits.yml` + `KitService`). Operator ticks below still for live verify.

### Deploy

1. Latest RPCharacters jar with `kit.yml` + **claim command** (no join/reload auto-grant) + roster kit meta.
2. ConditionalEvents: `tfmc_starter` is `enabled: false` in repo (`events/a_boosters.yml`); reload/restart CE so `/tfmc starter` stays off (no double kit).
3. ProvinceSystem API + frontend with kit cooldown / status on roster (no create “lose kit forever” warning).
4. Rebuild/redeploy website containers after API+FE land.

### Locked (target)

- Per character: kit once via `/rpcharacter kit starter`
- Per player: **48h** between successful claims
- Create during cooldown → character stays **eligible** (claim later)
- Discord owns player messaging (no website/in-game tip nudges)
- Full kit: hunting knife, 32 gold, 256 churro, oak boat, writable book, bundle, white bed

### Operator checklist (after 21.06)

- [ ] `kit.yml` loaded; CE `/tfmc starter` disabled
- [ ] `/rpcharacter kit starter` grants once; join/reload does **not** auto-grant
- [ ] New character during 48h cooldown can be created; claim blocked until cooldown clears
- [ ] Second claim same character rejected
- [ ] After cooldown, new character can claim
- [ ] No create warning that creating now permanently loses the kit

Checkpoint:

```text
kit.yml → /rpcharacter kit starter → 48h between claims
  → create anytime; claim when cooldown clear
```

## Step 21 — Kits + lore customise (Phase 3)

**Playbook:** [Planning/14-character-creator.md](./Planning/14-character-creator.md) Phase 2–3 · batches [Planning/batches/step-21/00-index.md](./Planning/batches/step-21/00-index.md).

**Code:** 21.01–21.09 + 21.05 docs **done** (21.07 create-wizard path **superseded**). Operator checklist below still unchecked.

### Deploy

1. RPCharacters jar with `kits.yml` + `KitService` + `/rpcharacter kit <id>` + lore apply + `assets/knife_skin.png`.
2. ProvinceSystem API + FE character detail → Kits (no create-wizard knife step).
3. ArmourShop / skins path unchanged for player `handheld` + `knives` → `ps_items`.

### Locked

- Configurable kits in `kits.yml`; per-kit cooldown; once-per-character flag
- Claim `/rpcharacter kit <id>`; no auto-grant
- Customise via ALIVE character → Kits → Edit editable items (not create wizard)
- Once-per-character claimed → no customise
- `pending_skin` blocks that kit’s claim until `ready`
- `editable`: `skin-png` + `base-set` only; NBT preview
- No tip/nudge copy (Discord owns messaging)

### Operator checklist

- [ ] `kits.yml` + `/rpcharacter kit starter` (and other kit ids when present)
- [ ] Per-kit cooldown from config; once-per-character for starter
- [ ] Web: character → Kits → Edit knife; create wizard has no knife step
- [ ] Non-editable items listed without Edit
- [ ] Claimed once-per-character kit cannot be customised
- [ ] `pending_skin` blocks claim; approve → claim delivers skin + lore
- [ ] No `tfmc_armorshop` / staff category path

Checkpoint:

```text
kits.yml → character kits UI → Discord if needed → /rpcharacter kit <id>
  → kit with skin+lore (block while pending_skin)
```

## Step 22 — Web character sheet (read-only parity)

**Playbook:** [Planning/14-character-creator.md](./Planning/14-character-creator.md) · batches [Planning/batches/step-22/00-index.md](./Planning/batches/step-22/00-index.md).

**Code:** 22.01–22.03 done (roster sheet sync + FE sheet UI + docs). Operator ticks below.

### Deploy (when built)

1. RPCharacters jar that pushes sheet fields on roster sync.
2. ProvinceSystem API + FE character detail sheet + shared nested-route margins.

### Locked

- Read-only identity sheet (no switch/kill)
- Display names for race/class
- Fields: age, birthday, gender, description, attributes, traits, clues
- Shared `px-6` / max-width shell on character nested pages

### Operator checklist

- [ ] Detail shows display race/class (not raw ids)
- [ ] Sheet shows age, birthday, gender, description, attributes, traits, clues when present
- [ ] Kits routes have side margins like the list page
- [ ] No switch/kill on website

Checkpoint:

```text
roster sheet fields → /character/[id] identity sheet → Kits with padded layout
```

## Step 23 — Kit lore editor polish

**Playbook:** [Planning/14-character-creator.md](./Planning/14-character-creator.md) · batches [Planning/batches/step-23/00-index.md](./Planning/batches/step-23/00-index.md).

**Code:** 23.01–23.04 done (pickable/preview/namespace + customise colours/lore/hash/3D + FE + docs). Operator ticks below.

### Deploy (when built)

1. ProvinceSystem API (pickable filter, texture GET, name_colours, lore normalize, texture_hash, item_3d bridge).
2. RPCharacters jar with namespace-aware kit customise merge.
3. FE lore item editor polish.

### Locked

- Pick: own applied + staff i_tools (same base_set); omit missing PNGs
- Preview from website disk; staff `tfmc_armorshop` / player `tfmc_submissions`
- Name colours; inline lore + §7 default; duplicate PNG guard; optional 3D

### Operator checklist

- [ ] Pick list shows own + staff i_tools knives with thumbs; no missing-file rows
- [ ] Staff pick applies with armorshop namespace; player with submissions
- [ ] Name colours + inline lore + gray default on claim
- [ ] Duplicate PNG upload rejected; 3D optional upload works

Checkpoint:

```text
pick thumbs → coloured name + inline lore → claim with correct IA namespace
```

## Step 24 — Character sheet parity (traits, attrs, background)

**Playbook:** [Planning/14-character-creator.md](./Planning/14-character-creator.md) · batches [Planning/batches/step-24/00-index.md](./Planning/batches/step-24/00-index.md).

**Code:** 24.01–24.04 done (RPC empty lore + roster fields + PS accept + FE sheet + docs). Operator ticks below.

### Deploy (when built)

1. RPCharacters jar with empty-lore fix and expanded roster sheet payload.
2. ProvinceSystem API accepting `background` + `experience_modifiers`.
3. FE character sheet sections for EXP / background / formatted birthday.

### Locked

- Traits: personality / evil only
- Attributes: merged totals; profession EXP from experience modifiers
- Background: writable-book lore; empty lore never adds blank lines
- Birthday display: `26/09/326 AE` (pad day/month, never pad year)

### Operator checklist

- [ ] Traits on sheet are personality/evil only
- [ ] Attributes include trait modifiers; profession EXP shown
- [ ] Background matches writable book; no blank gaps from empty lore
- [ ] Birthday displays like `26/09/326 AE`

Checkpoint:

```text
empty lore → roster sheet fields → /character/[id] parity with Character Info
```

## Step 25 — Kit customise submit + deny UX

**Playbook:** [Planning/14-character-creator.md](./Planning/14-character-creator.md) · batches [Planning/batches/step-25/00-index.md](./Planning/batches/step-25/00-index.md).

**Code:** 25.01–25.03 done (deny customise state + FE Submit item UX + docs). Operator ticks below.

### Deploy (when built)

1. ProvinceSystem API with `denied` customise state on skin deny.
2. FE lore item editor Submit item / file chips / success + denied copy.

### Locked

- CTA: Submit item; 5 min + Discord DM; upload needs approval
- File inputs styled like skins upload
- Skin deny → customise `denied`; keep name/lore; require new skin

### Operator checklist

- [ ] Submit item label; pick vs upload success messages differ
- [ ] File choose looks like skins upload chip
- [ ] Deny → customise denied, name/lore kept, kit not ready
- [ ] Resubmit without skin blocked; with skin proceeds

Checkpoint:

```text
Submit item → deny skin → denied customise → resubmit with new skin
```

## Step 26 — Kit asset sync + post-submit status

**Playbook:** [Planning/14-character-creator.md](./Planning/14-character-creator.md) · batches [Planning/batches/step-26/00-index.md](./Planning/batches/step-26/00-index.md).

**Code:** 26.01–26.03 done (kit-skin PUT sync + status page + docs). Operator ticks below.

### Deploy (when built)

1. ProvinceSystem API with `PUT /characters/plugin/kit-skins/{name}`.
2. RPCharacters jar that uploads `assets/{skin_png}.png` after catalog sync.
3. FE customise status page + post-submit redirect.

### Locked

- RPC owns assets; catalog sync copies to `backend/assets/kit_skins/`
- Missing PNG: warn + skip; catalog still succeeds
- After submit → character status page (not skins token route)

### Operator checklist

- [ ] Catalog/reload syncs `knife_skin.png`; default preview works on staging
- [ ] Submit item → status page (pending/ready copy)
- [ ] Denied status shows reason + Edit again

Checkpoint:

```text
reload → default knife preview → submit → status page → deny → Edit again
```

## Step 27 — Kit skin templates + `resetkit`

**Playbook:** [Planning/14-character-creator.md](./Planning/14-character-creator.md) · batches [Planning/batches/step-27/00-index.md](./Planning/batches/step-27/00-index.md).

**Code:** 27.01–27.05 done (templates + customise limits + `resetkit` + docs). Operator ticks below.

### Deploy (when built)

1. RPC jar parsing `2d-template` / `3d-template` + catalog fields + `resetkit`.
2. PS/FE kit customise kind + size from templates + customise wipe route.
3. Staff `/rpcharacter resetkit <player> <character_id> <kit_id>` + PS customise wipe.

### Locked

- Editable: `2d-template` required; `3d-template` optional (omit = no 3D)
- Knife: `handheld` + `item_3d`; PNG sizes match `/skins`
- Resetkit: ELIGIBLE + clear cooldown + clear kit customisations (RPC + PS)

### Operator checklist

- [ ] Catalog shows knife templates
- [ ] Kit upload enforces 16×16; 3D optional works
- [ ] `resetkit` allows reclaim + re-customise

Checkpoint:

```text
kits.yml templates → catalog → knife 16×16 / optional 3D
  → resetkit → claim/customise again
```

## Step 28 — Book skins + kit journal

**Playbook:** [Planning/05-skins-system.md](./Planning/05-skins-system.md) · [Planning/10-armourshop-itemsadder.md](./Planning/10-armourshop-itemsadder.md) · [Planning/14-character-creator.md](./Planning/14-character-creator.md) · batches [Planning/batches/step-28/00-index.md](./Planning/batches/step-28/00-index.md).

**Code:** 28.01–28.07 done (book kind + sign swap + kit journal + docs). Operator ticks below.

### Deploy

1. PS `book` kind (unsigned + signed) + FE KindPicker.
2. ArmourShop pack/shop apply + sign-time texture swap.
3. Kit editable journal (`2d-template: book`) + customise bridge.

### Locked

- Full `/skins` kind; two 16×16 PNGs; no 3D
- Sign → signed texture
- Starter grant stays `v.WRITABLE_BOOK` unless verify forces MI/IA base

### Operator checklist

- [ ] `/skins` Book: upload unsigned+signed → Discord review → apply
- [ ] Equipped/usable book shows unsigned; after sign shows signed
- [ ] Kit journal customise + claim; sign swap on kit book
- [ ] Staff curated book path (if enabled) smoke OK
- [ ] `resetkit` on starter re-opens journal customise

Checkpoint:

```text
/skins book → apply → kit journal → claim → sign → signed texture
```

## Step 29 — Kit customise visibility + claim AS gate

**Playbook:** [Planning/14-character-creator.md](./Planning/14-character-creator.md) · batches [Planning/batches/step-29/00-index.md](./Planning/batches/step-29/00-index.md).

**Code:** 29.01–29.06 done (customise visibility + claim AS gate + docs). Operator ticks below.

### Deploy

1. PS player delete-customise for one kit item + FE kit list/editor UX.
2. RPC claim: approval block + ArmourShop slug presence (“awaiting skins”).
3. Status copy: pending approval only (no kit-ready DM).

### Locked

- List: custom name, blue Custom tag, pending gray / no Edit
- Dirty Submit; Delete resets customise only (not skin)
- Claim pulls web; missing AS skin → awaiting skins message

### Operator checklist

- [ ] Kit list shows Custom tag / pending gray + no Edit while awaiting approval
- [ ] Dirty Submit; Delete resets item, skin remains in `/skins`
- [ ] Claim while approval pending → approval message
- [ ] Claim after approve before pack → “awaiting skins”
- [ ] Claim after AS apply → custom item granted
- [ ] Customise only journal (or only knife) → claim OK when that skin is ready

Checkpoint:

```text
customise → Custom/Pending on list → claim gates → grant when AS has skin
```

## Step 30 — Character skin wardrobe (Phase 4)

**Playbook:** [Planning/14-character-creator.md](./Planning/14-character-creator.md) · batches [Planning/batches/step-30/00-index.md](./Planning/batches/step-30/00-index.md).

**Code:** 30.01–30.08 done (wardrobe API, MineSkin, web UI, RPC apply/mask/cmd, creation stages, docs). Operator ticks below when live.

### Deploy

1. Free MineSkin API key on PS backend (`MINESKIN_API_KEY` in gitignored `.env`).
2. PS API + FE wardrobe + RPC jar (apply / wardrobe command / mask / stages).
3. Catalog reload (`/rpcharacter catalog sync`) so `wardrobe-skin-slots` + stage `platform` (incl. wardrobe stages) sync.

### Locked

- Slots: base + masked (all) · extras by rank (1/1/2/3/3 swappable)
- 64×64 only; MineSkin on Save; no staff review
- Apply on join + character switch; mask on/off; `/rpcharacter wardrobe` opens GUI (optional slot arg still equips)
- Soft refresh ~45s; web PENDING until plugin ack after apply
- Rank drop wipes extras; empty base = no auto-apply
- Creation: `platform` game tip vs web upload card

### Operator checklist

- [ ] Free MineSkin API key configured on PS backend
- [ ] Web: upload 64×64 base → spinner → slot ready with 3D preview
- [ ] Non-64×64 rejected
- [ ] Locked extras show Gilded+ / Ascended+ (coloured when possible)
- [ ] Masked upload; not selectable in `/rpcharacter wardrobe`; tip to match Base head for TAB
- [ ] Character switch / join applies active skin; empty base leaves account skin
- [ ] Mask on/off swaps masked ↔ active
- [ ] Gilded unlocks 2 swappable; Ascended 3
- [ ] Rank drop wipes extras
- [ ] Game create: wardrobe tip only; web create: wardrobe card (optional upload)
- [ ] Optional skin names (defaults Base / Skin 2 / Skin 3 / Masked)
- [ ] PENDING overlay clears after in-game pull/apply ack
- [ ] `/rpcharacter wardrobe` GUI: green filled / yellow empty / red locked

Checkpoint:

```text
web upload → MineSkin → switch/join apply → mask · wardrobe cmd · rank wipe
```

## Step 31 — Drink Builder (BreweryX)

**Playbook:** [Planning/15-drink-builder.md](./Planning/15-drink-builder.md) · batches [Planning/batches/step-31/00-index.md](./Planning/batches/step-31/00-index.md).

**Code:** 31.02–31.08 done (shared cooldown, PS drink API, DrinkBuilder scaffold/pack/delete, `/drinks` UI, `drinksreview` bot). Docs/cutover 31.09 closed. Operator ticks below when live.

### Deploy

1. Staging PS up (`scripts/staging-up.sh` / curl `http://127.0.0.1:18001`).
2. Deploy DrinkBuilder jar from `Builds/DrinkBuilder/`; config `api.base-url` / `api.plugin-key`, `paths.breweryx-folder`, `paths.itemsadder-tfmc-drinks`, CMD range, `ia-reload-delay-seconds`. Put `assets/glass_bottle.png` + `assets/potion_overlay.png` in the DrinkBuilder plugin folder (synced to PS on enable/reload/catalog sync). Empty `tfmc_drinks` scaffold is created on enable.
3. `/drinkbuilder catalog sync` (prune `ingredients.yml` as needed), then `/drinkbuilder pack pull [force]` after Discord approves.
4. FE `/drinks` on staging UI (`13001`).
5. Copy `tfmc_bot/drinksreview/` into Red cogs; `config.yml` (same `api_base_url` / `staff_key` / `#bot-feed` as skins); `-load drinksreview`; slash enable/sync; `/drinksreview ping`.
6. TFMCWeb shared `token-cooldowns` already shipped (31.02) — confirm jar/config on staging.
7. Retire ConditionalEvents `/tfmc drinks`: event file is `plugins/ConditionalEvents/events/drinkbuilder.yml.disabled` — reload ConditionalEvents (or restart). Players use `/token create drink` then redeem on `/drinks`.

### Locked

- Noble: color-only; Gilded+: texture upload or reuse (applied CMD only)
- Shared skin↔drink mint cooldown on TFMCWeb only
- Curated ingredient catalog → PS/web (category labels from DrinkBuilder)
- Drink colour stops + texture from DrinkBuilder `permission-groups.yml` (in-game); website gates prefer TFMCWeb `rpc_player_meta` after lobby join (Step 32)
- IA `tfmc_drinks` potion + `model_id` / Brewery `customModelData`
- Delete: recipe always; texture/CMD iff refcount 0

### Operator checklist

- [ ] Non-ranked cannot `/token create skin|drink`
- [ ] Shared cooldown skin ↔ drink
- [ ] Noble: color-only drink approve → Brewery recipe (`color`)
- [ ] Gilded: textured drink → `tfmc_drinks` + CMD match
- [ ] Ingredient modal shows labeled categories + search
- [ ] Distill checkbox off by default; runs/time only when enabled
- [ ] NameColourPicker respects rank stops (Noble 1, Gilded 2, Ascended/Legacy 8)
- [ ] Tinted potion preview on color mode (after DrinkBuilder asset sync)
- [ ] Discord approve/deny + DMs (`drinksreview`)
- [ ] Staff delete + shared texture refcount (`/drinkbuilder drink delete`)
- [ ] `/token resetcooldowns <player>` clears shared mint clock
- [ ] `/tfmc drinks` disabled (CE event retired); players use token + website
- [ ] After lobby join (TFMCWeb only): `/drinks` colour picker unlocked for ranked players without DrinkBuilder on lobby

Checkpoint:

```text
/token create drink (ranked) → redeem /drinks
  → submit color-only (Noble) or textured (Gilded+)
  → Discord approve
  → DrinkBuilder pack (if texture) + recipes.yml
  → brewable in BreweryX with correct look
/token create skin then drink blocked by shared cooldown
staff delete drink; shared texture kept if still referenced
```

## Step 32 — `rpc_player_meta` + TFMCWeb join sync

**Batch:** [Planning/batches/step-32/00-rpc-player-meta.md](./Planning/batches/step-32/00-rpc-player-meta.md).

Web entitlements (`name_colour_stops`, `allow_drink_texture`, skin kinds, character slots, LP flag snapshots) are pushed by **TFMCWeb on player join** to ProvinceSystem `rpc_player_meta`. Lobby with TFMCWeb only is enough; DrinkBuilder / ArmourShop / RPCharacters are not required on that box for website gates.

### Deploy

1. Staging PS up (DB migrate creates `rpc_player_meta`).
2. Deploy TFMCWeb jar with `player-meta` section in `config.yml` (duplicated ladders — keep in sync with plugin `permission-groups.yml` files). **Lobby must have this jar/config.**
3. Join lobby once as a ranked/staff player (or `/web syncmeta [player]`).
4. Confirm `GET /characters/player-meta` (Bearer skin/drink/character session) shows expected stops / texture / `permission_flags`.

### Operator checklist

- [ ] Lobby join as gilded → `name_colour_stops >= 2`, `allow_drink_texture: true`
- [ ] Staff `*` → colour stops capped at 8 for web
- [ ] `/drinks` and `/character/create` colours correct after lobby join without DrinkBuilder/RPC on lobby
- [ ] Skin redeem + `skin_staff` bypass still works
- [ ] Never-joined-since-deploy players still work via legacy meta fallback
- [ ] `rulequiz.completed` present in `permission_flags` when configured

## Step 33 — Realm + token policy

**Batch:** [Planning/batches/step-33/00-realm-token-policy.md](./Planning/batches/step-33/00-realm-token-policy.md).

TFMCWeb stamps `realm_id` on minted codes and gates which scopes `/token create` allows per box. Character creates inherit `realm_id` from the Bearer session. Lists/ingests are **not** filtered by realm yet (Plan 3).

### Deploy

1. Staging PS up (migrate adds `codes.realm_id` + `character_creates.realm_id`, default `main`).
2. Deploy TFMCWeb jar with:

```yaml
realm:
  id: main   # lobby+main share; use tutorial / dev on those boxes

tokens:
  enabled-scopes:
    - character   # lobby example — skin/drink rejected locally
  # main / survival: skin, drink, character, skin_staff
  # tutorial: []  (tokens disabled)
```

3. `/web reload` after editing live config (or restart).

### Operator checklist

- [ ] Lobby: `/token create skin` fails; `/token create character` works; code/create tagged `main`
- [ ] Main: skin/drink/character still mint; shared cooldown unchanged
- [ ] Dev box: mint tags `dev`; character create row has `dev`
- [ ] Tutorial: any `/token create` rejected (“disabled on this server”)
- [ ] Old codes after migrate behave as `realm_id=main`

## Step 34 — Realm-scoped game data

**Batch:** [Planning/batches/step-34/00-realm-scoped-data.md](./Planning/batches/step-34/00-realm-scoped-data.md).

Pending character ingest, roster mirrors, and skin/drink apply queues are filtered by `realm_id` from TFMCWeb. Plugins soft-depend TFMCWeb; boxes without it fall back to `main`.

### Deploy

1. Staging PS up (migrate: roster PK includes `realm_id`; stamp/backfill `submissions.realm_id` / `drink_submissions.realm_id`).
2. Deploy TFMCWeb + RPCharacters + ArmourShop + DrinkBuilder jars together.
3. Confirm each box’s TFMCWeb `realm.id`:

| Box | `realm.id` |
|-----|------------|
| Lobby | `main` |
| Main / Survival | `main` |
| Tutorial | `tutorial` |
| Dev | `dev` |

### Operator checklist

- [ ] Lobby character create (`main`) appears only on main RPC ingest, not tutorial/dev
- [ ] Tutorial create never applied on main
- [ ] Dev skin approve → only dev ArmourShop pulls it
- [ ] Dev drink approve → only dev DrinkBuilder pulls it
- [ ] Box without TFMCWeb still uses `main` fallback
- [ ] Website character list for a `dev` session shows only that realm’s pending + roster

## Step 35 — TFMCWeb HTTP gateway + per-realm isolation

**Batch:** [Planning/batches/step-35/00-http-gateway-per-realm.md](./Planning/batches/step-35/00-http-gateway-per-realm.md).

All plugin ProvinceSystem HTTP goes through TFMCWeb. `rpc_player_meta`, lore-items, and cosmetic/character uniqueness are realm-scoped. **RPC / ArmourShop / DrinkBuilder require TFMCWeb** on the box.

### Deploy

1. Staging PS up (migrate: `rpc_player_meta` PK includes `realm_id`; lore `realm_id`; submission id prefix rules for non-main).
2. Deploy TFMCWeb jar **first**, then RPC / ArmourShop / DrinkBuilder.
3. Remove live `characters-api` / `skins-api` / DrinkBuilder `api` config blocks (URL + key live only in TFMCWeb).
4. Confirm TFMCWeb `realm.id` per box (same table as Step 34).

### Operator checklist

- [ ] Box without per-plugin API config still reaches PS (TW only)
- [ ] Dev skin id is `dev_…` and lands in `tfmc_submissions_dev` on the dev box only
- [ ] Tutorial character name can match a main character name
- [ ] Lobby join sync writes `rpc_player_meta` for `main`; dev box writes `dev`
- [ ] Lore-item ready on tutorial never pulled by main RPC
- [ ] ArmourShop / DrinkBuilder no longer push player-meta on join

## Step 5 — Discord link + player DMs (historical)

> **Obsolete path notes:** Step 5 used ArmourShop for `/linkdiscord` and `/armourshop token create`. **Current owner is TFMCWeb** (Step 17). Curl snippets below remain for API smoke without the plugin.

Automated API path: `python scripts/skins_e2e_smoke.py` from `backend/` (link + notify + review).

```bash
curl -s -X POST http://127.0.0.1:18001/skins/discord/link/start \
  -H "Content-Type: application/json" \
  -H "X-Plugin-Key: dev-plugin-key" \
  -d '{"player_uuid":"00000000-0000-0000-0000-000000000001","minecraft_name":"Test"}'
```

Live path today: TFMCWeb `/linkdiscord` → Discord complete → `/token create skin` → site redeem (see Step 17).

## Mint a code + submit a skin

**Preferred (in-game, TFMCWeb / Step 17):**

1. Deploy `Builds/TFMCWeb/tfmcweb-*.jar` with `api.base-url` / `api.plugin-key` pointing at staging.
2. Grant LP `tfmcweb.token.create` (or use `tfmcweb.admin`).
3. `/linkdiscord` → Discord complete (**required before mint**).
4. `/token create skin` → click the aqua code to copy.
5. Redeem on `/skins` → KindPicker shows only entitled kinds.

Checklist extras:

- [ ] Non-ranked player cannot mint (even with LP if player-meta/defaults deny)
- [ ] Noble mint works; KindPicker is 2D items only (no armor/3D/gun)
- [ ] Second mint within cooldown fails with wait message
- [ ] Staff mint bypasses cooldown and shows all kinds
5. Open `http://127.0.0.1:13001/skins`, redeem, upload → `#bot-feed` / DMs as Step 5 (historical DM flow).

Admin: `/armourshop listtokens` lists unused unexpired codes (issuer + red `[Delete]` → `/armourshop token delete <code>`).

Operator checklist:

- [ ] Discord linked for test UUID (TFMCWeb / Step 17)
- [ ] LP: `tfmcweb.token.create` (or admin)
- [ ] `/token create skin` → click-copy
- [ ] Redeem + upload on staging UI
- [ ] `#bot-feed` / submitted + outcome DMs

**API-only fallback** (curl against staging):

```bash
curl -s -X POST http://127.0.0.1:18001/skins/codes \
  -H "Content-Type: application/json" \
  -H "X-Plugin-Key: dev-plugin-key" \
  -d '{"player_uuid":"00000000-0000-0000-0000-000000000001"}'
```

**Browser UI from your PC** (tunnel both ports):

```bash
ssh -L 13001:127.0.0.1:13001 -L 18001:127.0.0.1:18001 user@amp-host
```

Open `http://127.0.0.1:13001/skins`, redeem the code, upload (**Discord must already be linked** for that UUID). The site shows **Submitting…** until the composite review sheet is built, then the status page displays that sheet. Wait for `#bot-feed` (or `/skinsreview post <id>`) — Discord gets the same `review_sheet.png`, not raw 16×16 files.

## Step 8 — Flow 2 apply (armor / melee)

End-to-end for kinds with pack writers: **`armor_set`**, **`handheld`**, **`large_handheld`**, **`bow`**, **`large_bow`**, **`crossbow`**.

Bow kinds need four/five multipart fields (`texture`, `pull_0`, `pull_1`, `pull_2`, + `charged` for crossbow) — **filenames are freeform**, the server writes fixed `{id}...` stems itself. Sizes: bow/crossbow 16×16; large_bow 32×32.

1. Deploy latest `Builds/ArmourShop/armourshop-*.jar`. On the **server** `plugins/ArmourShop/config.yml` (do not commit secrets):
   - `skins-api.base-url`: `http://127.0.0.1:18001` (or host-reachable staging API)
   - `skins-api.plugin-key`: same as compose `PLUGIN_KEY` (default `dev-plugin-key`)
   - `pack-apply.ia-contents-path`: absolute path to live ItemsAdder `contents/`
   - `pack-apply.categories-path`: absolute path to ArmourShop `Categories/`
   - `pack-apply.force-reload-time`: `"06:00"` server-local daily force pull + IA refresh (blank disables)
   - `pack-apply.ia-reload-delay-seconds`: seconds between `iareload` and `iazip` (default `5`)
2. Link Discord + mint + redeem (Step 17 / mint section above).
3. On `http://127.0.0.1:13001/skins`: choose kind. Armor: **Add tier** (1–6 of `iron/steel/abyssalite/mythril/mage/infantry`), 6 uploads per tier; non-armor: pick filtered **`base_set`** (no `item`), grip only for `large_handheld`. Upload any PNG file — filenames don't matter, the API derives the id from your linked Minecraft name + item name. Optional **Apply name** adds colours/styles. Site blocks if you already have an active submission with that item name.
4. Staff **Approve** in `#bot-feed` (embed shows the human submission id, Minecraft + Discord names, tiers or base set — never raw UUIDs).
5. Pack apply happens via:
   - **Manual:** `/armourshop pack pull` (force — runs even with players online)
   - **Empty server:** last player quit → auto pull + IA refresh if queue/API pending
   - **Daily:** `force-reload-time` (force)
   Expect console: pack write (**N files per tier for armor**) / shop (**N SkinSets for armor, one per tier, sharing one LP grant**) / LP (API, no `lp` chat) / `iareload` → delay → `iazip` / applied ack.
   Shop YAML uses plain `name` + separate `colour` (string or list) + optional `add-name` / `styles` (TLibs gradient at runtime).
6. Confirm id left the approved list:

```bash
curl -s http://127.0.0.1:18001/skins/plugin/approved \
  -H "X-Plugin-Key: dev-plugin-key"
```

7. Issuer opens ArmourShop → set(s) under **Player Armor** (`ps_armor`, one per tier) or **Player Items** (`ps_items`) → apply onto matching BaseSet/tier gear in inventory.
8. Staff delete (optional): `/armourshop submission delete <human-id>` (tab-completes ids like `drefvelin_blue_knight`, never a UUID) clears **all tiers'** shop + pack files + shared LP node and marks API `revoked`. Delete only **enqueues** the deferred IA refresh — it does not force an immediate `iareload`/`iazip`, even with staff online; the queued reload flushes on the next empty-server tick or the daily force time.

Operator checklist:

- [ ] Redeploy API (migrate drops `player_keys`; ignore any leftover unused column); bot; rebuild ArmourShop (+ TLibs if needed)
- [ ] Config: staging API + live `pack-apply.*` paths (+ force time / IA delay)
- [ ] Submit **multi-tier armor** (e.g. iron + steel) with arbitrary PNG filenames — accepted; id built from IGN + item name
- [ ] Upload blocked when same player reuses the same item name (no separate base-id conflict check)
- [ ] Approve → pack pull writes **N SkinSets** for an N-tier armor submission; `#bot-feed` shows names + tiers, not UUIDs
- [ ] `/armourshop submission delete <human-id>` tab-completes and removes shop/pack for all tiers; status revoked; IA refresh only **queued** (not forced)
- [ ] Issuer sees set(s) and applies onto matching BaseSet/tier gear

Failure modes: players online delays non-force IA refresh; LuckPerms missing so shop hides set; wrong BaseSet/tier gear in inventory; Mojibake `Â` means jar/source encoding still wrong; item name too long combined with IGN (shorten item name — 48-char id cap).

Checkpoint:

```text
approve → pack pull (N tiers) → shop + LP API → iareload → iazip → applied → issuer applies skin
```

## Keys (compose defaults)

| Env | Value |
|-----|--------|
| `SKINS_DEV` | `1` |
| `STAFF_KEY` | `dev-staff-key` |
| `PLUGIN_KEY` | `dev-plugin-key` |

Override in `docker-compose.staging.yml` if you want stronger keys for a longer-lived staging box.

## Free-text validation (display names + prose)

Web create / skin upload / Discord link / moderation free-text fields share charset rules in `backend/src/text_validation.py` (frontend mirror: `frontend/lib/textValidation.ts`).

| Class | Fields | Allowed |
|-------|--------|---------|
| Display name | character name, skin item name, tier aliases, optional gender, MC/Discord names when present | Unicode letters (accents ok), digits, space, `-` `_` `.` `'`. No emoji, commas, `<>{}[]\/`, or colour codes (`§`, `&c`, `#RRGGBB`). |
| Prose | description, clues, deny/moderation reasons | Printable text + normal punctuation; no controls, emoji, or colour codes. Length limits from catalog / route. |
| Technical ids | skin slugs, redeem codes | Unchanged (`naming.py` / server-issued codes). Do not widen slug alphabets for “friendly” names. |

**XSS:** React text rendering only (no `dangerouslySetInnerHTML` for user strings). Invalid input is **rejected** at the API; do not add an HTML sanitizer. Any future HTML sink must escape or stay off user content.

Web names may include accents; in-game chat creation `SetterStage` name gate is still ASCII letters/spaces until a separate RPC change.

Smoke: `name: "A<a>"` → 400; `José O'Brien` (length ok) → accepted; skin `display_name` with `<script>` rejected before slugify.

## Port already in use?

```bash
sudo ss -tlnp | grep -E '18001|13001|8001'
```

Change the left-hand side of `ports:` in `docker-compose.staging.yml` if needed, keep container ports `8000` / `3000`.
