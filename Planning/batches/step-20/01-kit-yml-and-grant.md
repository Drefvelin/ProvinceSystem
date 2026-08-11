# Batch 20.01 — kit.yml + grant engine (RPCharacters)

**Plan + build:** Own starter kits in RPCharacters. Grant on join / reload. No website editor.

**Repos:** `Workspace/rpcharacters`  
**Depends on:** Existing character active/select + player data storage

## Locked grant rules

| Rule | Value |
|------|--------|
| Per character | At most **one** successful starter-kit grant |
| Per player cooldown | **48 hours** after a successful grant (configurable in `kit.yml`) |
| Triggers | (1) Player **join** with an active character (2) Plugin **reload** while player is online with an active character |
| Eligibility at create | If player cooldown is **active** when the character is created (in-game finish or web ingest apply), mark that character **kit-ineligible** (never granted) |
| Eligible + not yet granted | On join/reload: if cooldown **clear**, give kit, mark character granted, stamp player `last_kit_grant_at` |
| Eligible + cooldown still active | Do **not** grant on this tick; character stays eligible until a successful grant or explicit policy (prefer: remain eligible and grant on first join/reload after cooldown clears, **unless** created during cooldown → already ineligible) |
| Inventory | Best-effort give; log failures; do not soft-lock create if inventory full (define drop/overflow behaviour in implement) |

**Create-during-cooldown is the hard miss:** that character never gets the kit. Characters created with cooldown clear get the kit on the next successful grant tick after create.

## Plan

1. **`kit.yml`** under `plugins/RPCharacters/` (ship default in jar resources). Include:
   - `cooldown-hours: 48`
   - Ordered item list (MI type/id/amount and/or vanilla material/amount)
   - Baseline contents from CE `tfmc_starter` unless Caroline trims to food+knife at build time:
     - `TOOLS` / `IRON_HUNTING_KNIFE` ×1
     - `FOODS` / `CHURRO` ×256 (or reduced amount if desired)
     - `CURRENCY` / `GOLD_COIN` ×32
     - oak boat, writable book, bundle, white bed
   - Optional `editable:` under knife (Phase 3 fields: `skin-png`, `base-set`) — **parse or ignore; do not implement editor**. Custom skins = player submissions → bot → `ps_items` (no staff category).
2. **Persistence** on player/character data:
   - Character: `kit_granted` (bool) and/or `kit_granted_at`; `kit_ineligible` (bool) when created during cooldown
   - Player (UUID): `last_kit_grant_at` (epoch ms)
3. **`KitService` (name flexible)** — `tryGrant(Player)`:
   - Resolve active character; abort if none / already granted / ineligible
   - If cooldown remaining > 0: abort (leave eligible character for later if not ineligible)
   - Give items from `kit.yml`; on success mark granted + update player stamp; message player
4. **Hooks**
   - Join (after character active is known)
   - Reload path: for each online player with active character, `tryGrant`
   - Character create finish (in-game) + web ingest apply: if cooldown active → set `kit_ineligible` + warn; if clear → leave eligible (grant on join/reload or immediately if online)
5. **CE cutover** — Document disabling `tfmc_starter` in ConditionalEvents (`a_boosters.yml`) once RPC grant is live so players cannot double-dip. Prefer disable in same deploy as RPC jar.
6. **Admin** (optional small): command to inspect kit status / clear cooldown for tests — only if cheap; otherwise staging uses time manipulation / test UUID wipe.

## Verify

- [x] Fresh character, cooldown clear → kit on join (or reload) once *(code paths wired; operator smoke after jar)*  
- [x] Same character join again → no second kit *(kit-status granted)*  
- [x] Grant → create second character inside 48h → ineligible, no kit on join  
- [x] After 48h → new character eligible → kit on join  
- [x] Reload with online eligible character → grant  
- [x] CE `/tfmc starter` disabled (`enabled: false` in a_boosters.yml)  

## Implemented

- `kit.yml` full CE contents + `KitLoader` / `StarterKitService`
- Character `kit-status` + account `last-kit-grant-ms`
- Hooks: join (`initiatePlayer`), reload (`loadConfigs`), `CharacterCreation.finish`, `CharacterIngestService.applyPayload`
- CE `tfmc_starter` disabled

## Out of scope

Web UI; cooldown API sync (02); lore editor; ArmourShop; `assets/knife_skin.png` usage.
