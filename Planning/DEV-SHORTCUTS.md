# DEV shortcuts & production cutover tracker

Running list of **dev-only config, commented-out checks, spoof data, and test bypasses** that must be reverted or replaced before production.

**Last sweep:** 2026-08-20 (SimpleFactions + ProvinceSystem workspace)

**How to use**

- Add a row when you ship a new dev bypass (hardcoded timer, admin spoof, commented validation, etc.).
- Check off or delete rows only after production values are live and verified.
- War scheduling dev tools: see [Step 59 planned dev commands](#step-59-battle-scheduling-planned).

---

## SimpleFactions — `config.yml` (dev server template)

Shipped default in [`simplefactions/src/main/resources/config.yml`](../../simplefactions/src/main/resources/config.yml). Live server merges overrides into `plugins/SimpleFactions/config.yml`.

| Key | Dev value | Production target | Notes |
|-----|-----------|-------------------|-------|
| Header comment | `dev server template` | Remove or relabel | Documents intent only |
| `map-reference` | `dev` | `main` (or live map id) | Drives TFMCWeb upload/regen paths |
| `war.require_declare_code` | `false` | `true` | Step **68**; see also RelationView bypass below |
| `war.battle_cadence.provinces_between_battles` | `3` (70b lock) | `3` (or higher after playtest) | Was `1`; see [70b.01](./batches/step-70b/01-planning-lock.md) |
| `installations.fort.construction-time` | `10` | `432000` (5 days) | Seconds; see [Installations.md](../../simplefactions/Documentation/Installations.md) |
| `installations.port.construction-time` | `10` | `259200` (3 days) | Same |
| `installations.airport.construction-time` | `10` | `259200` (3 days) | Same |

Tick model: faction `tick()` runs **once per real second** (`FactionManager` timer every 20 ticks). Construction and regiment expansion `timeLeft` decrement **once per second**, so `10` = **10 seconds**, not 10 days.

---

## SimpleFactions — `regiments.yml`

| Regiment | Key | Dev value | Production target (comment in file) |
|----------|-----|-----------|-----------------------------------|
| professional | `expansion-time` | `10` | Default loader fallback `21600` (6 h) if omitted |
| militia | `expansion-time` | `10` | `#43200` (12 h) in comment |
| levy | `expansion-time` | `0` | `#43200` in comment |

Queue ticks once per faction second (same as construction).

---

## SimpleFactions — `Guilds/upgrades.yml`

All three realm upgrades use `expansion-time: 10` (10 seconds). Production values not commented in file; treat as **dev-only** until locked.

| Upgrade id | Dev `expansion-time` |
|------------|----------------------|
| `max_admin_power` | 10 |
| `max_diplomatic_capacity` | 10 |
| `admin_power_gain` | 10 |

---

## SimpleFactions — code bypasses (must revert)

| Location | What | Production action | Tracked in |
|----------|------|-------------------|------------|
| [`RelationView.java`](../../simplefactions/src/main/java/me/Plugins/SimpleFactions/Managers/Inventory/RelationView.java) ~L133 | **Commented block** skips declare pre-checks (code gate, opinion, duplicate war, target online) | Uncomment block; rely on `war.require_declare_code` + validators | Step **68**, staging checklists 56/57/58 |
| [`RestServer.java`](../../simplefactions/src/main/java/me/Plugins/SimpleFactions/REST/RestServer.java) L24 | `REGEN_HASH` hardcoded | Move to config / env (see checklist item below) | [08-implementation-checklist.md](./08-implementation-checklist.md) |

---

## SimpleFactions — admin / debug commands (keep, but document)

These are **intentional** staff tools, not production player features:

| Command | Purpose |
|---------|---------|
| `/faction warstatus <id>` | JSON war state (campaign, initiative, proposals) |
| `/faction warpath <id>` | Regenerate campaign route |
| `/faction fullregen <map>` | Trigger map regen via TFMCWeb |
| `/faction regen` | Queue nation upload + regen |

---

## SimpleFactions — timing quirks (verify before prod)

| System | Actual tick | UI / docs say | Action |
|--------|-------------|---------------|--------|
| Administrative power gain | Every **10 s** (`FactionManager.timer % 10`) | Lore shows `+N/hour` | Confirm intended hourly rate; may need slower tick or rescaled gain |
| Faction daily cycle | `timer >= 86400` (~24 h real time) | Daily guild income, loans, etc. | No dev shortcut; real-time days on test server |
| Diplomacy opinion drift | `RelationManager.tick` every **3600 s** | - | Real-time hour |
| Map partial upload | `MapSystem` full update every **3600 s** | - | Real-time hour |

---

## SimpleFactions — wars (Steps 56–68)

### Already dev-friendly (config, not hacks)

| Item | Dev setting | Prod |
|------|-------------|------|
| Declare without Discord ticket | `war.require_declare_code: false` | Step 68 codes |
| Declare GUI pre-checks | Disabled in code (see above) | Re-enable step 68 |

### Step 59 — battle scheduling (locked in [59.01](./batches/step-59/01-planning-lock.md))

**Timeline (Zulu, defaults configurable via `war.battle_schedule.*`):**

- **Vote open:** when next battle is pending (at declare or after battle end); does **not** wait for battle province.
- **`post_battle_choice_deadline_hour` (default 12):** auto **Push** (winner) or **Attack** (loser after Hold) if post-battle choice unresolved.
- **`vote_close_hour` (default 16):** tally → schedule or postpone (`battleDay` +1, votes persist).
- **First battle day:** calendar **day after declare**; voting may start at declare.

**Locked dev surface (59.06, remove before prod):**

| Mechanism | Detail |
|-----------|--------|
| **`/faction warschedule <id>`** | Admin subcommands: `opencvote`, `closevote`, `skipday`, `castvote <hour> [attacker\|defender\|both]`, `forcequorum`, `setscheduled <iso>`, `battlecreate`, `battledelete`, `battlestart`, `winbattle attacker\|defender`, `battlechoice push\|hold\|attack\|accept` (`defenderchoice` aliases retained) |
| **`war.battle_voting.dev_min_players: 1`** | Test-server config only (default quorum uses `min_players: 4`) |
| **Shortened hour keys** | Test server may set e.g. 10/11/12/13 if order constraint holds |

**Remove before prod:** all `warschedule` spoof subcommands + `dev_min_players` + shortened schedule hours on live config.

---

## Step 61b — battle dev mode (shipped 2026-08-21)

**Lock:** [step-61b/01-planning-lock.md](./batches/step-61b/01-planning-lock.md) · **Staging checklist:** [step-61b/05-docs-verify.md](./batches/step-61b/05-docs-verify.md)

| Mechanism | Detail |
|-----------|--------|
| **`/battle devmode on\|off\|status`** | Volatile in-memory toggle; resets on restart. Admin only. |
| **`battle.devmode.phantom_count`** | Default 10 phantom UUIDs: on manual `/warband create` when devmode on; on campaign **first signup** (not at empty shell create) |
| **`battle.capture_min_players: 1`** | Min players at capture zone (prod default) |
| **Campaign join rules** | Side membership check; roster cap = preview collective lives; bypass faction `WarbandSlot` for campaign battles |

**Solo staging workflow (attacker path):**

> **Superseded by [61c.05 campaign E2E](./batches/step-61c/05-docs-verify.md)** (signup flow, staff battle edit, full war pipeline). Keep below for historical 61b scope reference only.

1. `/battle devmode on` (check status)
2. Declare war, schedule battle (`dev_min_players: 1`)
3. `/warband create` or war GUI muster - roster shows phantoms in lore when devmode on
4. `/battle join <id> attacker` - wrong side rejected; roster cap enforced
5. Fight solo (capture min 1), verify lives/casualties/commitments
6. `/battle devmode off`; restart clears devmode and phantoms

**Remove before prod:** confirm `capture_min_players` prod value; treat phantom seeding as test-server only (devmode toggle is harmless if unknown).

---

## Step 61c — campaign UX (shipped 2026-08-21)

**Lock:** [step-61c/01-planning-lock.md](./batches/step-61c/01-planning-lock.md) · **E2E checklist:** [step-61c/05-docs-verify.md](./batches/step-61c/05-docs-verify.md)

| Theme | Detail |
|-------|--------|
| **Battle templates** | Settings only (lives, FF, keep inv, durations); staff place spawns/jails/points via `/battle edit` per battle |
| **`/faction warschedule`** | Formatted per-subcommand lines; full JSON stays on `warstatus` only |
| **Campaign signup** | One auto warband per battle side; players opt in via `/warband list` or `/warband join`; no Muster Army GUI; no faction slot limits |
| **Staff battle shortcuts** | `warschedule <id> battlecreate` (green province, any phase), `warschedule <id> battledelete` (reset battle + fresh warband shells), `warschedule <id> battlestart` |
| **`winbattle` (dev)** | `warschedule <id> winbattle attacker\|defender` - applies campaign outcome + occupation **without casualties**; errors if post-battle choice pending |
| **`battlechoice` (dev)** | `warschedule <id> battlechoice push\|hold\|attack\|accept` - resolves Push/Hold (winner) or Attack/Peace (loser after Hold); `defenderchoice hold\|counter` aliases map to hold/push |
| **Mid-battle join** | Allowed if side lives > 0 (costs 1 life); voluntary leave blocks rejoin for that battle |
| **Battle persistence (61c.09)** | Battles + referenced warbands saved to `plugins/SimpleFactions/Battles/` and `Warbands/`; 60s autosave + save on disable; in-progress fights resume on restart. **One manual battle** (`warId == null`); delete via battle edit slot 22 (TNT). Orphan manual warbands purged on shutdown. |
| **Side fast edit (61c.10)** | Battle edit -> Sides -> click side -> Set spawn / Set jail / Add point at player location. Points auto-name global chain letters A, B, C... (no per-side `A'`). Gated by `capture_points_enabled` (field template default true). |
| **Capture chain sync (61c.11b)** | Sequential capture ON: chain reorders from defender spawn (A = nearest, then greedy NN). Toggle ON, add/delete while sequential, or load with sequential ON triggers sync. Point View sorted by chain index. |
| **Capture point markers (61c.12)** | FIELD battles: per-player DUST pillars at capture points plus gray chain segments between points (A→B→C). Uses `Player.spawnParticle`, not world particles. Gray = locked (sequential), yellow = contested, green = friendly, red = enemy. |
| **Devmode phantoms** | Campaign: seed on **`battlecreate`** when devmode on (first phantom is leader until war side leader joins); also on first signup if not already seeded. Manual `/warband create`: seed at create (61b) |

**Campaign E2E workflow (test server):**

Prerequisites: `war.battle_voting.dev_min_players: 1`, optional `/battle devmode on` for solo capture.

**A. War setup**

1. `/battle devmode on` (optional) - status enabled
2. Declare war - `/faction warstatus <id>` shows commitments JSON
3. `/faction warschedule <id> opencvote` - formatted lines only (no JSON blob)
4. `/faction warschedule <id> castvote 21 both` - hour, voters, phase
5. `/faction warschedule <id> forcequorum`
6. `/faction warschedule <id> closevote` - scheduled instant + province (or `setscheduled <iso>` or `battlecreate` when campaign map shows green next battle)

**B. Battle prep**

7. Campaign battle exists - one warband per side; **0 members** until signup (or devmode phantoms immediately after `battlecreate`)
8. `/warband list` - faction warband visible; you are **not** auto-added
9. Staff: `/battle edit` - set spawns, jails, capture point(s) via **Sides -> side -> Set spawn / Set jail / Add point** (or legacy commands)
10. `/warband list` → join - first joiner is leader; war leader signup promotes over phantom leader
11. Devmode: with `battlecreate`, phantoms fill both sides; otherwise phantoms appear on first signup

**C. Fight loop**

12. Battle starts (scheduled tick, `warschedule battlestart`, or `/battle start`) - lives from committed regiments + signups
13. Wrong-side player cannot join warband
14. Capture progresses with `capture_min_players: 1`
15. `/kill` - collective lives drop; ledger tracks
16. Win or end battle - casualties apply; war phase returns to **VOTING**

**D. War end probe (pre-62)**

17. Repeat B–C for second battle OR `warschedule skipday`
18. End war: `/faction endwar <id>` or white peace via Campaign GUI
19. `/faction warstatus <id>` - status ended (goal not auto-applied until step 62)

**E. Cleanup**

20. `/battle devmode off`; restart plugin - devmode off, no phantom persistence; battles/warbands on disk reload (61c.09)

Full 22-step checklist with checkboxes: [05-docs-verify.md](./batches/step-61c/05-docs-verify.md).

---

## ProvinceSystem — backend

| Item | Location | Dev behavior | Production action |
|------|----------|--------------|-------------------|
| Calavorn trade/prosperity **spoof** | `backend/src/input/main/guilds.json`, `province_data.json` | Fake guilds until SF export | Replace with SF upload; see [step-47/03](./batches/step-47/03-calavorn-trade-data.md), [STAGING.md](../STAGING.md) |
| Spoof generator | `scripts/tools/generate_spoof_province_data.py` | Regenerates fake data | Keep tool; stop using output on prod map |
| Skin test code seeder | `skins/seed_dev_code.py` | Seeds `TEST-CODE-1` | Local/staging only |
| CORS origins | `backend/server.py` | `localhost:3000`, etc. | Restrict to prod domains on deploy |
| Regen hash in SF plugin | via `RestServer.REGEN_HASH` | Shared secret in Java source | Config/env (checklist open item) |

---

## ProvinceSystem — frontend

| Item | Env / path | Dev behavior | Production action |
|------|------------|--------------|-------------------|
| Character UI dev | `NEXT_PUBLIC_CHARACTER_UI_DEV=1` | Fake session, no redeem | **Unset** on prod build |
| UI dev modules | `lib/characters/uiDev.ts`, `sheetDev.ts`, `loreItemsDev.ts`, `kitsDev.ts`, `entitlementsDev.ts` | Fixtures when flag set | Harmless if flag off; verify CI/prod env |
| Creation catalog fixture | `fixtures/creationCatalog.dev.json` | Used by UI-dev lore editor | Local only |
| Dev map route | `/map/r3b1rth` → `mapId=dev` | URL-only test map | Not in nav; optional on prod |
| Map title editor | `/map/editor?map=main|dev`; entry via **Edit titles** on map viewer (not global nav); staff session + `tfmc.map.staff` | `NEXT_PUBLIC_CHARACTER_UI_DEV=1` + backend `CHARACTER_UI_DEV=1` uses `ui-dev-session` (no redeem) | Staff-only; unset both on prod |
| Editor regen (no SF hash) | `POST /{map}/editor/regen/fullregen:{tier}` | Bearer staff session token | Not plugin regen URL |
| Province id grid (editor) | `defines/{map}/province_id_grid.bin.gz` | `python -m scripts.tools.build_province_id_grid --map main` from `ProvinceSystem/backend` when `provinces.png` / `provinces.txt` change | Editor requires grid file; copy to SF `Input/` only when provinces change (step 54) |
| Title coverage check | `python -m src.scripts.util.validate_title_coverage main` | From `ProvinceSystem/backend` | After county rebuild on `main` |
| Drinks dev preview | `/drinks/dev-preview` | Local iteration page | Do not link publicly on prod |

---

## ProvinceSystem — fixture / map data tweaks

| Item | Notes |
|------|-------|
| Lanbury settlement trim (step 53) | Settlement provinces `[705]` only; faction may still own 704. Intentional test geometry, not a timer hack. |
| `map-reference: dev` vs `main` | SF dev server uses `dev`; Calavorn uses `main` with spoof trade |

---

## Production cutover checklist (summary)

Before go-live, confirm:

- [ ] `config.yml`: construction times, map-reference, war declare code
- [ ] `regiments.yml` + `Guilds/upgrades.yml`: expansion times
- [ ] `RelationView`: declare pre-checks uncommented (step 68)
- [ ] Step 59: remove battle schedule dev commands/flags
- [ ] Step 68: declare codes enabled
- [ ] `REGEN_HASH` / API secrets not in source
- [ ] `input/main` trade data from SF export, not spoof
- [ ] Frontend: `NEXT_PUBLIC_CHARACTER_UI_DEV` unset
- [ ] AP gain tick rate matches design (10 s tick vs `/hour` label)

---

## Changelog

| Date | Change |
|------|--------|
| 2026-08-21 | Step 61c.01 lock: template settings-only, warschedule output, campaign signup |
| 2026-08-21 | Step 61b shipped: battle devmode, capture min 1, campaign join cap |
| 2026-08-21 | Step 61b planned: battle devmode, capture min 1, campaign join cap |
| 2026-08-20 | Initial sweep; planned warschedule dev tools |
| 2026-08-20 | Step 59.01 lock: vote timeline, quorum, postpone, `/faction warschedule` dev commands |
