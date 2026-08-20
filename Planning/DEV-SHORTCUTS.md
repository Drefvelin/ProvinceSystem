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
| `war.battle_cadence.provinces_between_battles` | `1` | TBD (likely higher) | Faster campaign pacing on test server |
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
- **`defender_choice_deadline_hour` (default 12):** auto **Hold** if no defender choice when attacker initiative = 0.
- **`vote_close_hour` (default 16):** tally → schedule or postpone (`battleDay` +1, votes persist).
- **First battle day:** calendar **day after declare**; voting may start at declare.

**Locked dev surface (59.06, remove before prod):**

| Mechanism | Detail |
|-----------|--------|
| **`/faction warschedule <id>`** | Admin subcommands: `opencvote`, `closevote`, `skipday`, `castvote <hour> [attacker\|defender\|both]`, `forcequorum`, `setscheduled <iso>` |
| **`war.battle_voting.dev_min_players: 1`** | Test-server config only (default quorum uses `min_players: 4`) |
| **Shortened hour keys** | Test server may set e.g. 10/11/12/13 if order constraint holds |

**Remove before prod:** all `warschedule` spoof subcommands + `dev_min_players` + shortened schedule hours on live config.

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
| 2026-08-20 | Initial sweep; planned warschedule dev tools |
| 2026-08-20 | Step 59.01 lock: vote timeline, quorum, postpone, `/faction warschedule` dev commands |
