# Step 64.01 — Campaign battle schedule lock

**Plan + docs only.** Lock slot model, fort ZOC siege rules, trim priority, initiative formula, template vs display kinds, and zone-removal scope before 64.02+ code.

**Repos:** `Workspace/simplefactions`  
**Depends on:** [step 63](../step-63/00-index.md) (shipped) · [Wars.md](../../../../simplefactions/Documentation/Wars.md) · [Installations.md](../../../../simplefactions/Documentation/Installations.md)

**Status:** **Done** (2026-08-22). Authoritative gameplay summary in [Wars.md](../../../../simplefactions/Documentation/Wars.md) (Campaign battle schedule section).

---

## Locked — two layers: template vs display

| Layer | Purpose | Values |
|-------|---------|--------|
| **`BattleType` (template)** | Win rules, lives, capture vs contest timer | `FIELD`, `SIEGE`, `RAID` |
| **`CampaignBattleKind` (display)** | Campaign GUI icon, lore, staff setup expectations | `FIELD`, `SIEGE`, `NAVAL`, `NAVAL_INVASION` |

**Step 64 ships** `FIELD` and `SIEGE` display kinds only. `NAVAL` and `NAVAL_INVASION` enum values may be added in 64.02 for forward compatibility but are **unused** until step 65.

### Mapping (step 64 scope)

| Slot | `BattleType` | `CampaignBattleKind` | Flags |
|------|--------------|----------------------|-------|
| Objective (required) | `FIELD` | `FIELD` | `required = true` |
| Field cadence | `FIELD` | `FIELD` | |
| Fort ZOC gate | `SIEGE` | `SIEGE` | `fortInstallationId` |

Objective provinces keep existing objective / capital / next-battle markers. Display kind is **Field Battle** because gameplay is field capture.

**No `BattleType.NAVAL`.** Naval fights use `FIELD` + `navalVariant` template flag (step 65).

---

## Locked — battle schedule at declare

Build once when `WarCampaignService.populateCampaign` succeeds. Persist ordered list on `War`.

```text
schedule = CampaignScheduleBuilder.build(war, axis, objectiveIndex)
trimmed  = CampaignScheduleTrimmer.trim(schedule, maxBattlesForGoal(war.goal))
war.setCampaignBattleSchedule(trimmed)
war.setInitiativeFuelBothSides(ceil(trimmed.size() * initiative_factor))
```

### Natural slot insertion (before trim)

Walk campaign axis from border start (index `cursorIndex` at declare) toward objective index. For each province on the axis segment being advanced:

1. **Fort ZOC siege** — if province is in an operational fort's ZOC and that fort's **war-time controller** is the **enemy** of the advancing coalition at schedule-build time (defender controls all forts at declare), insert a **siege** slot at the **fort province** (once per fort on the line, not once per ZOC province).
2. **Field cadence** — every `war.battle_cadence.provinces_between_battles` provinces along the axis (existing config), insert a **field** slot at that province.
3. **Objective** — always append a **required field** slot at `objectiveProvinceId` (may coincide with a cadence or siege province; dedupe to one slot with `required` winning).

**Capital inside uncleared fort ZOC:** if objective province is inside a fort ZOC still enemy-controlled at declare, natural list contains **siege at fort** then **objective field** (two slots, not merged).

### Schedule index vs cursor

| Field | Role |
|-------|------|
| `campaignScheduleIndex` | Index into **trimmed** `campaignBattleSchedule`; which slot is next to fight |
| `campaignBattlesFought` | Count of fought campaign battles (stats / legacy); increments +1 per fought campaign battle alongside `campaignScheduleIndex` |
| `cursorIndex` | Axis position after push/hold; unchanged by schedule model |

- `nextBattleProvince(war)` resolves from `campaignBattleSchedule[campaignScheduleIndex]` (after re-siege insert check below).
- `cursorIndex` still moves along axis per existing push rules after each battle.

**Target feel:** per-goal `max_battles` default **4**; `initiative_factor` **1.5** → starting fuel `ceil(4 × 1.5) = 6` for a trimmed 4-battle war. Back-and-forth spends fuel until exhaustion or victory.

---

## Locked — fort ZOC

Reuse `ZocRealm.computeZocProvinces(fortOwner, fortProvince)` for province membership.

| Rule | Detail |
|------|--------|
| ZOC shape | Fort tile + same-top-realm **land** neighbors (existing export rule) |
| Overlap | At most **one fort per province**; if multiple ZOCs cover a province, **oldest operational fort** wins (`Installation.completedAt` ascending; tie-break by installation `id`) |
| Siege trigger | Campaign line **passes through** a province in fort F's ZOC |
| Siege location | Battle at **fort's province** (`fortInstallationId` on slot) |
| Coastal fort | **Dropped** — no special coastal-fort rule (docs cleanup in 64.09 / 65) |

---

## Locked — war-time fort control

Fort **installation ownership** in the faction DB does **not** change during war.

| State | Meaning |
|-------|---------|
| `fortControllers: Map<installationId, CampaignCoalition>` on `War` | Who **controls the ZOC** for campaign purposes |
| At declare | Each operational fort → controller = owning faction's coalition |
| After siege | **Winner's coalition** becomes controller for that fort |
| Passing ZOC again | If controller is **enemy**, require siege again |

**Symmetric:** defender counter-push through a fort the attacker now controls requires defender to win a siege at that fort.

Siege outcome hook (64.06) updates `fortControllers` before cursor / schedule advance.

### Locked — dynamic re-siege insert (counter-push)

When resolving the next battle, **before** returning the scheduled slot:

```text
onNextBattleResolve(war):
  if advancing path crosses a province in fort F's ZOC
     AND FortControlService.controller(war, F) == enemy of advancing coalition
     AND next schedule slot is not already SIEGE for fortInstallationId F:
       insert SIEGE slot at campaignScheduleIndex (shift tail right)
```

Implemented in 64.06 (`CampaignCapabilityService` / schedule mutator). No full schedule rebuild on push direction change.

---

## Locked — trim priority

Per goal `max_battles` in config (all goals **4** for now). If natural list length > max, **drop lowest priority first**:

| Priority (keep) | Kind | Notes |
|-----------------|------|-------|
| 1 (never cut) | Objective (`required`) | |
| 2 | Siege | |
| 3 | Naval | Step 65 — trimmer accepts kind but no naval slots yet |
| 4 | Naval invasion | Step 65 |
| 5 (cut first) | Field cadence | |

Within the same priority tier, drop slots **farthest from objective** first (highest axis index distance to objective index).

---

## Locked — initiative

| Rule | Detail |
|------|--------|
| Remove | `war.initiative_per_side` fixed per side |
| Add | `war.initiative_factor` (default **1.5**) |
| Add | per-goal `max_battles` under `war.goals.<GOAL>.max_battles` (default **4**) |
| Formula | `fuel = ceil(trimmedSchedule.size() * initiative_factor)` for **both** coalitions at declare |
| Recompute | Only at declare in 64; dynamic re-siege inserts do **not** recompute fuel |

Initiative count is based on **final** battle count **after** trim.

---

## Locked — remove battle zone limitation

Delete entirely in 64.08 (no feature flag):

| Remove | Location |
|--------|----------|
| `allowedProvinceIds` enforcement on battle start | `BattlePlacementValidator`, `BattleBoundsService` |
| Spawn / jail / capture / contest must be inside allowed provinces | `BattleSideSetupService`, `BattleContestSetup` |
| Province-leave countdown → death | `BattleLeavePenaltyService` for field/siege |
| Docs: leave penalty, allowed province set, naval adjacent-sea allowed set | `Wars.md` |

Staff may place spawns, jails, capture points, and contest areas **anywhere**. Raids were already unbounded. **Naval variant** template flag remains for staff layout (attacker sea spawn); it does not enforce province bounds after 64.08.

`allowedProvinceIds` JSON field: stop writing / stop reading in 64.08 (empty on disk OK for old saves).

---

## Locked — config schema (64.05)

```yaml
war:
  initiative_factor: 1.5
  # remove: initiative_per_side
  battle_cadence:
    provinces_between_battles: 1   # unchanged
  goals:
    DE_JURE_ANNEX:
      max_battles: 4
    SUBJUGATE:
      max_battles: 4
    TRANSFER_SUBJECT:
      max_battles: 4
```

---

## Locked — persistence (`War` JSON)

New / changed fields:

| Field | Type | Meaning |
|-------|------|---------|
| `campaignBattleSchedule` | `ScheduledCampaignBattle[]` | Trimmed ordered slots |
| `campaignScheduleIndex` | int | Next slot to fight (0 at declare) |
| `fortControllers` | `Map<String, String>` | installation id → `attackers` \| `defenders` coalition key |
| `initiativeFuelAggressor` / `initiativeFuelDefender` | int | Set from trimmed schedule at declare |

Each `ScheduledCampaignBattle`:

| Field | Type |
|-------|------|
| `provinceId` | int |
| `kind` | `FIELD` \| `SIEGE` \| `NAVAL` \| `NAVAL_INVASION` |
| `required` | boolean |
| `fortInstallationId` | string? (siege only) |
| `battleType` | derived: `SIEGE` if kind is `SIEGE`, else `FIELD` |

---

## Locked — resolver & launch (64.06)

`CampaignBattleTypeResolver` (currently stubbed to `FIELD`; stale comment references step 63) maps schedule slot → `BattleType`:

- `SIEGE` kind → `BattleType.SIEGE`
- All other kinds in 64 → `BattleType.FIELD`

`CampaignBattleLaunchService` reads slot from `campaignScheduleIndex` at prepare/start time.

---

## Locked — GUI (64.07)

Route province items show battle kind lore under the province name:

| Kind | Lore label (example) |
|------|----------------------|
| `FIELD` | `Field Battle` |
| `SIEGE` | `Siege` |

Objective provinces: Field Battle lore + existing objective / next-battle markers.

Icon materials chosen in 64.07 (e.g. iron sword vs shield); must be distinct at a glance.

`warschedule` admin output lists kind per slot.

---

## Locked — test scenarios

1. Declare war with route crossing one fort ZOC → schedule contains siege at fort + objective; trim keeps both if under max.
2. Route crossing two forts → two siege slots (distinct `fortInstallationId`).
3. Overlapping ZOC → older fort assigned per province (`completedAt`, then `id`).
4. Natural list 6 slots, max 4 → objective + both sieges kept, field cadence slots dropped first (farthest from objective).
5. Initiative fuel = `ceil(4 * 1.5)` = 6 for 4-battle schedule.
6. Siege won by aggressor → `fortControllers` updated; defender must siege again if line re-enters ZOC (dynamic insert at `campaignScheduleIndex`).
7. `CampaignBattleTypeResolver` returns `SIEGE` for siege slots, `FIELD` for field/objective.
8. Battle starts with spawn outside battle province → allowed after 64.08.
9. Player leaves battle province during field battle → no penalty after 64.08.

---

## Out of scope (explicit)

- Port ZOC, naval battles, naval invasion (step 65)
- `ZocRealm` war-based controller filter on map export (step 65)
- Per-battle port/airport/fort pick (step 65)
- Chronicle / map export `battle_scheduled` payload (step 67)
- Raid war type (step 66)
