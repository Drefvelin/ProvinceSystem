# Step 60.01 — Planning lock (province presence + battle runtime)

**Plan + docs only.** Lock the central province enter/leave tracker, battle type matrix (field / siege / raid + naval variants), template scope, and step 60 boundaries before 60.02+ code.

**Repos:** `Workspace/simplefactions`, reference merge source `Workspace/warbands`  
**Depends on:** [00-index](./00-index.md) · [step-59.01](../step-59/01-planning-lock.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md) · [war-build-order.md](../../war-build-order.md)  
**Authoritative gameplay doc:** [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

Lock step 60 boundaries so batches 60.02–60.10 do not creep into collective lives formula (61), goal apply (62), fort ZOC gate selection (63), full naval campaign routing (64), inter-battle raids (65), raid war declare route (66), map export (67), or declare codes (68).

**60.01 itself:** lock doc + Wars.md alignment only. **No Java changes.**

---

## Locked — step 60 scope

| In scope | Out of scope |
|----------|----------------|
| Central **province enter/leave** tracker (1s poll, events) | Per-feature ad-hoc province checks |
| Merge Warbands battle engine into SF submodule | Full lives / regiment casualty math (61) |
| Staff **battle templates** (spawns, jails, points/areas) | Fort ZOC **campaign gate** logic (63) |
| **Field**, **siege**, **raid** battle modes + naval variants | Inter-battle tactical raids (65) |
| Auto-start from `SCHEDULED` / `AUTORESOLVE_PENDING` | Raid **war type** declare route (66) |
| Player **join command** for campaign battles | Goal apply / reparations (62) |
| Province-leave penalty (field + siege) via central tracker | Port pick per battle (64) |

---

## Locked — central province presence (SF-wide)

One service owns player province transitions. Battles, future ZOC warnings, raids, and map UX subscribe to it instead of polling locations themselves.

### Poll loop

| Rule | Detail |
|------|--------|
| **Interval** | **1 second** (20 ticks), main thread |
| **Scope** | All **online** players each tick |
| **Lookup** | [`RestServer.getProvince(Player)`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/REST/RestServer.java) → [`ProvinceGrid.getAt(x, z)`](../../../../simplefactions/Documentation/ProvinceGrid.md) |
| **State** | Per-player **last province id** (including invalid / unknown sentinel) |
| **Events** | `PlayerProvinceEnterEvent`, `PlayerProvinceLeaveEvent` (custom Bukkit events) |

### Transition rules

| Case | Behavior |
|------|----------|
| First join / no prior state | Fire **enter** only (no leave) |
| Province id unchanged | No events |
| Province id changed | Fire **leave** (old) then **enter** (new) |
| Map disabled / invalid id (`-2`) | Treat as **unknown** province; still fire leave/enter when crossing between known ↔ unknown |
| Quit | Fire **leave** for last known province; drop state |

### API surface (60.02)

| Method | Use |
|--------|-----|
| `getCurrentProvince(Player)` | Read cached province (updated each 1s tick) |
| `isInProvince(Player, int provinceId)` | Battle boundary checks |
| Events | Battle leave penalty, future hooks |

**No other SF subsystem** may run its own periodic all-player province scan once 60.02 ships. One-off reads (`getProvince` at command time) remain allowed.

---

## Locked — battle types

Three **modes**. Field and siege share campaign province bounds; raid does not.

| Mode | Win condition | Allowed region | Respawns |
|------|---------------|----------------|----------|
| **Field** | Capture **points** (Warbands-style progress to 100%) | Battle **province** (+ naval add-on below) | Per template / step **61** lives (v1: collective lives from template until 61 refines) |
| **Siege** | Hold **contest area** for **contest duration** (default **3 minutes**, staff GUI) | Same as field | Same as field |
| **Raid** | Attacker objective at **target only**; defenders hold | **No region limit** — players may go anywhere | **Attackers: none** (elimination). **Defenders: infinite** or **set lives** (template toggle) |

### Field battle

| Rule | Detail |
|------|--------|
| **Template** | Staff sets spawns, jails, **capture points** (reuse Warbands point capture) |
| **Bounds** | Players in battle must stay in allowed provinces (see naval). Leaving → [province-leave penalty](#locked--province-leave-penalty-field--siege) |
| **Use** | Default **campaign** battles at route provinces |

### Siege battle

| Rule | Detail |
|------|--------|
| **Template** | Staff sets spawns, jails, **contest area** (volume/region), **`contest_duration_seconds`** (default **180**, editable in staff template GUI) |
| **Progress** | While contested side meets area rules, **hold timer** counts down; reset or pause per implement batch (document in 60.07) |
| **Bounds** | Same province rules as field (+ naval) |
| **Use** | Fort ZOC gates (63 triggers **siege** mode); capital-in-fort path |

### Raid battle

| Rule | Detail |
|------|--------|
| **Target** | One **settlement / province** (raid war 66, inter-battle raid 65, or staff manual) |
| **Bounds** | **No battle province fence.** Players may traverse the map freely during the fight |
| **Scoring / capture** | Only the **target** location counts for raid progress / win |
| **Attackers** | **No respawns.** Side eliminated when all attacker participants are dead (disconnect counts as out for raid) |
| **Defenders** | Template chooses **`defender_respawn_mode`**: `INFINITE` **or** `LIVES` (integer pool) |
| **Use** | Raid war type (66), inter-battle raids (65), optional staff manual raids |

---

## Locked — naval variant (field + siege only)

When template flag **`naval_variant: true`** (staff GUI):

| Rule | Detail |
|------|--------|
| **Extra province** | The **sea province** adjacent to the battle land province (from province graph; [`Province.isSea()`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/Map/Provinces/Province.java)) is added to allowed set |
| **Attacker spawn** | Placed on **naval** spawn point in that sea province (template) |
| **Defender spawn** | Land spawn unchanged unless template overrides |
| **Leave penalty** | Applies when leaving **either** allowed province (land or adjacent sea) |
| **Not used** | Raid mode (raids have no region limit anyway) |

Naval **campaign routing** (blocked sea zones, port pick) remains step **64**. Step 60 only adds the **battle footprint** + spawns for fights that already reached a coastal province.

---

## Locked — province-leave penalty (field + siege)

Uses **central province tracker**, not battle-local polling.

| Rule | Detail |
|------|--------|
| **Applies to** | **Field** and **siege** battles only |
| **Trigger** | Registered battle participant **leaves** allowed province set → start **10s countdown** (config `battle.province_leave_countdown_seconds`, default **10**) |
| **Return** | Re-enter allowed province before countdown ends → cancel |
| **Expire** | Force death → respawn at **side spawn** (template); counts as battle death |
| **Raids** | **No** province-leave penalty (no fence) |

---

## Locked — template storage (staff GUI)

Per **province id** (and optional terrain fallback), staff maintain reusable templates:

| Field | Field mode | Siege mode | Raid mode |
|-------|------------|------------|-----------|
| Attacker / defender spawns | yes | yes | yes (attacker may be off-map rally) |
| Jails | yes | yes | optional |
| Capture **points** | yes | no | optional (target-only scoring) |
| Contest **area** | no | yes | no |
| `contest_duration_seconds` | no | yes (default 180) | no |
| `naval_variant` + naval spawn | optional | optional | n/a |
| `defender_respawn_mode` | lives (61) | lives (61) | **`INFINITE` or `LIVES`** |
| Friendly fire / keep inventory | yes | yes | yes |

Campaign auto-battle picks template by **`scheduledBattleProvinceId`** + resolved **mode** (field vs siege vs raid).

---

## Locked — battle start triggers (from step 59)

| `battleSchedulePhase` | Step 60 action |
|-----------------------|----------------|
| `SCHEDULED` | At `scheduledBattleAt` (within battle window): create battle from template, open join window, start at configured time |
| `AUTORESOLVE_PENDING` | Start **immediately** when both leaders accepted live autoresolve (59 revision: 60s `/faction accept`, not stored flags) |
| After battle ends | Hand off outcome to existing campaign progression (58); re-open voting (59) — **61** applies casualties |

---

## Locked — Warbands merge

| Rule | Detail |
|------|--------|
| **Pattern** | Same as professions → RPCharacters: SF owns packages under `me.Plugins.SimpleFactions.War.battle.*` (exact path in 60.03) |
| **Keep** | Capture point engine, side membership, battle instance lifecycle |
| **Repurpose** | Manual warband muster GUI → campaign **join command** + auto roster from war participants |
| **Remove** | Standalone Warbands plugin dependency on production server |

Reference: [`warbands/src/main/java`](../../../../warbands/src/main/java) (~27 Java files).

---

## Locked — batches (60.02–60.10)

| Batch | Summary |
|-------|---------|
| [60.02 province presence](./02-province-presence.md) | 1s tracker + enter/leave events + tests |
| [60.03 warbands merge](./03-warbands-merge.md) | Submodule move, build, strip standalone plugin |
| [60.04 battle domain](./04-battle-domain.md) | `BattleType`, template model, persistence |
| [60.05 template GUI](./05-template-gui.md) | Staff template editor (points, area, durations, naval, raid respawn mode) |
| [60.06 field runtime](./06-field-runtime.md) | Capture points, bounds, join, leave penalty |
| [60.07 siege runtime](./07-siege-runtime.md) | Contest area + hold timer |
| [60.08 raid runtime](./08-raid-runtime.md) | Target-only scoring, attacker no-respawn, defender modes |
| [60.09 schedule hook](./09-schedule-hook.md) | `SCHEDULED` / `AUTORESOLVE_PENDING` → battle instance + join command |
| [60.10 docs verify](./10-docs-verify.md) | Tests + staging checklist |

---

## Locked — config keys (defaults)

| Key | Default | Notes |
|-----|---------|-------|
| `battle.province_poll_interval_ticks` | `20` | 1 second |
| `battle.province_leave_countdown_seconds` | `10` | Field + siege |
| `battle.siege.contest_duration_seconds` | `180` | Overridable per template in GUI |
| `battle.raid.defender_respawn_mode_default` | `INFINITE` | Template may set `LIVES` + pool |

---

## Verification (60.01)

- [x] Central 1s province tracker + events locked
- [x] Field / siege / raid modes locked
- [x] Naval variant for field + siege locked
- [x] Raid: no region fence, target-only scoring, attacker no-respawn, defender infinite or lives locked
- [x] Province-leave penalty uses central tracker (field + siege only)
- [x] Step 60 scope vs 61–68 locked
- [x] Wars.md updated to match

**Done when:** this file + [00-index](./00-index.md) + [Wars.md](../../../../simplefactions/Documentation/Wars.md) aligned.
