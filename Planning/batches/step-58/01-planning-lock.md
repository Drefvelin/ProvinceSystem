# Step 58.01 — Planning lock

**Plan + docs only.** Lock full campaign axis, progression FSM, white peace proposals, Campaign GUI, and persistence before 58.02+ code.

> **Historical:** runtime FSM and defender yellow-choice rules below were **superseded by [step 62.01](../step-62/01-campaign-progression-lock.md)** (2026-08). Axis, occupation, and GUI tint rules remain authoritative unless 62 lock says otherwise.

**Repos:** `Workspace/simplefactions`  
**Depends on:** [00-index](./00-index.md) · [step-57](../step-57/00-index.md) · [Wars.md](../../../../simplefactions/Documentation/Wars.md) · [war-build-order.md](../../war-build-order.md)  
**Authoritative gameplay doc:** [Wars.md](../../../../simplefactions/Documentation/Wars.md)

## Goal

Lock step 58 boundaries so batches 58.02–58.07 do not creep into battle scheduling, Warbands runtime, map export, or raid war routes.

---

## Locked — step 58 scope

| In scope | Out of scope |
|----------|----------------|
| **Full campaign axis** at declare / `warpath` regen | Battle window, hour voting (59) |
| `cursorIndex` at border **B** (middle of axis) | Warbands merge, battle engine (60–61) |
| Initiative init + spend rules | Surrender polish, goal apply, reparations (62) |
| Cursor ±1 after fought battle | Fort ZOC siege gates (63), naval (64) |
| Occupation bulge persistence | Map `wars[]` emit (67) |
| White peace auto-propose + GUI accept | Raid routes (66) |
| **CampaignView** GUI + WarView entry | Declare codes (68) |
| Capital-closer objective rule | De jure claims for GUI tint |

**58.01 itself:** lock doc + Wars.md alignment only. **No Java changes.**

---

## Locked — full campaign axis (replaces step 57 v1 polyline)

Step 57 shipped **`B → objective`** only with **`cursor_index = 0`**. Step **58.02** replaces this with a **dual-axis line**; cursor starts at the **border in the middle**.

### Visual model (Campaign GUI)

```text
← ATTACKER   [ capital … … B … … objective ]   DEFENDER →
                              ↑
                         cursorIndex
                         first battle
```

- **Left:** attacker faction capital → border **B** (full path at declare; always shown).
- **Right:** **B** → objective terminus (inclusive).
- **Attacker direction = left**, **defender direction = right**.

```mermaid
flowchart LR
  cap[Attacker capital]
  leftSeg[Left segment]
  B[Border B]
  rightSeg[Right segment]
  obj[Objective]
  cap --> leftSeg --> B --> rightSeg --> obj
```

### Generation algorithm (58.02+ in `WarCampaignService`)

1. Pick regional **objective** via [`ObjectiveProvincePicker`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/objective/ObjectiveProvincePicker.java).
2. **Step A:** for each invasion entry candidate **B** (defender-owned province adjacent to attacker-owned), pathfind **B → objective** (passes 1→2→3); pick **B** with minimum cost → **`campaignStartProvinceId`** (first battle province). If no land entry exists, use defender provinces adjacent to **sea**.
3. **Capital-closer rule:** if defender/subject **faction capital** path cost **B → capital** `<` **B → regionalObjective**, set **`objectiveProvinceId = capital`** and rebuild right segment **B → capital**.
4. **Left segment:** pathfind **attacker faction capital → B** (3-pass); store ordered **capital … B** (left to right).
5. **Right segment:** pathfind **B → objective** (inclusive).
6. **Merge:** `campaignProvinces = leftSegment + rightSegmentWithoutDuplicateB` ( **B** appears once).
7. **`cursorIndex` = index of B** in merged array (**not** 0).
8. Attacker capital must exist (`Faction.getCapital() > 0`); if missing, declare/regen fails (same as invalid campaign).

### Battles on the axis

| Rule | Detail |
|------|--------|
| **First battle** | Always at **`campaignProvinces[cursorIndex]`** (= defender-side **B** / invasion entry), regardless of **N** |
| **Later field battles** | Every **N** provinces along axis + mandatory nodes (objective, fort ZOC siege, capital) — **scheduling in 59–63** |
| **Counter-push** | Defender chooses **leftward** node on **existing** line toward attacker capital — **no** polyline append at choice time |

**Raid wars:** skip (step 66).

---

## Locked — province control for Campaign GUI (de facto)

**Not de jure.** **Not occupation bulge** for concrete block colors.

Use **belligerent territorial ownership** via [`BelligerentTerritory`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/pathfinder/BelligerentTerritory.java) + [`TitleManagerProvinceOwnerLookup`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/pathfinder/TitleManagerProvinceOwnerLookup.java):

| Check | Rule |
|-------|------|
| Owner | `ProvinceOwnerLookup.getOwnerFactionId(provinceId)` |
| Coalitions | Main leader, subjects, **called allies** on each [`Side`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/Side.java) |
| Viewer blue | Province owned by viewer's belligerent coalition |
| Viewer red | Province owned by enemy belligerent coalition |
| Neutral / unowned on line | **Red** for both viewers (v1) |

**Occupation bulge** (`occupied_by_*`) persists for map export (67) and chronicle — **separate** from Campaign GUI concrete colors.

---

## Locked — Campaign GUI

**Navigation:** War list → [`WarView`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/Managers/Inventory/WarView.java) → **Campaign** button → **`CampaignView`** (new `SFGUI.CAMPAIGN_VIEW`).

### Layout

| Row | Content |
|-----|---------|
| Route | Horizontal concrete blocks, one per `campaignProvinces[]` entry; paginate if line > ~9 slots |
| Cursor | Marker on `cursorIndex` (banner / glowing pane — separate from control color) |
| Info | Initiative both sides, `campaignPhase`, white peace proposal flags |
| Voting | Hour slots (step **59**, same screen) |
| Leaders | Accept white peace, surrender (62 polish) |

### Concrete legend (viewer-relative)

| Material | Meaning |
|----------|---------|
| **Blue concrete** | Owned by **your** belligerent coalition |
| **Red concrete** | Owned by **enemy** belligerent coalition |
| **Green concrete** | **Next battle** — single valid option (action slot) |
| **Yellow concrete** | **Choice** — two valid next battles (leader click) |

**No gray.** **No white.** Every battle has a winner; no neutral result tile.

Green/yellow **replace** the block material on actionable slots only (ownership in item lore).

### Leader actions (GUI-first)

| Situation | UI |
|-----------|-----|
| Attacker has initiative | Attacker leader: **green** on next attack node |
| Attacker initiative = 0 | Defender leader: **yellow** on **current front** (hold) and **next node left** (counter-push); confirm: Hold / Counter-push / Accept white peace |
| Auto-propose active | Other leader: **Accept white peace** button |
| Both auto-propose | Automatic white peace (no accept) |

**No player commands** for hold/counter-push/accept — admin/debug only (`warstatus`, `warpath`).

Fort / objective / capital nodes: lore tags (siege required, objective, capital); battle type rules in 63+.

---

## Locked — campaign progression

### Initiative

| Rule | Default |
|------|---------|
| Start per side | `war.initiative_per_side` (**4**) |
| Fought battle | Offensive side **−1** |
| Postponed battle (59) | **0** spend |
| At 0 initiative | Cannot launch **new offensive** |

### Cursor (after each fought battle)

| Outcome | Cursor |
|---------|--------|
| Pushing side wins | **+1** along line |
| Pushing side loses | **−1** |

Direction follows **who is pushing**, not fixed attacker/defender.

### Campaign phase FSM

| Phase | Entry |
|-------|-------|
| `INVASION` | Declare |
| `RETAKE` | Attacker holds objective |
| `COUNTER_PUSH` | Defender chooses counter-push |

`objectiveHeldBy`: `DEFENDER` until attacker wins at objective.

### Attacker initiative = 0 — defender choice

| Choice | Result |
|--------|--------|
| **White peace** | War ends, no reparations |
| **Counter-push** | Offensive toward attacker capital (left on axis) |
| **Hold** | No counter-offensive; front sits; attacker cannot attack at 0 initiative |

Counter-push **never mandatory** (e.g. successful siege defense while outnumbered).

### White peace proposals

| Side | Capitulation target |
|------|---------------------|
| Attacker (invasion/retake) | **Objective** (or capital if terminus) |
| Defender (counter-push) | **Attacker capital** |

Unreachable with remaining initiative → **auto-propose** flag. Other leader **accepts** → white peace. **Both** propose → **automatic** white peace.

Recalculate flags after each fought battle and phase change.

---

## Locked — occupation bulge (58.04)

On battle win, add to winner's occupation list:

1. Battle province
2. Graph neighbors that are: on `campaignProvinces`, already in either occupation list, or owned by enemy belligerent

Config: `war.occupation.bulge_include_enemy_neighbors: true`

---

## Locked — persistence fields (58.02)

| Field | Type | Notes |
|-------|------|-------|
| `initiativeAttacker` | int | Init at declare |
| `initiativeDefender` | int | Init at declare |
| `occupiedByAttacker` | int[] | Bulge export |
| `occupiedByDefender` | int[] | Bulge export |
| `lastBattleOccupied` | int[] | Last battle |
| `campaignPhase` | enum | `INVASION`, `RETAKE`, `COUNTER_PUSH` |
| `objectiveHeldBy` | enum | `ATTACKER`, `DEFENDER` |
| `whitePeaceProposedByAttacker` | boolean | |
| `whitePeaceProposedByDefender` | boolean | |
| `cursorIndex` | int | **Index of B**, not 0 |

Expand [`WarEndReason`](../../../../simplefactions/src/main/java/me/Plugins/SimpleFactions/War/enums/WarEndReason.java) for `WHITE_PEACE`, `AUTO_WHITE_PEACE` (full enum in 62).

---

## Locked — config

```yaml
war:
  initiative_per_side: 4
  battle_cadence:
    first_battle_at_border: true
    provinces_between_battles: 1
  occupation:
    bulge_include_enemy_neighbors: true
```

---

## Locked — module layout (58.02+)

| Path | Batch | Role |
|------|-------|------|
| `War/enums/CampaignPhase.java` | 58.02 | Phase enum |
| `War/enums/ObjectiveHolder.java` | 58.02 | Who holds objective |
| `War/campaign/WarCampaignService.java` | 58.02 | Full axis generation |
| `War/progression/CampaignProgressionService.java` | 58.03 | Cursor, initiative, phase |
| `War/progression/OccupationBulgeService.java` | 58.04 | Bulge province set |
| `War/progression/WhitePeaceService.java` | 58.05 | Proposals + accept |
| `Managers/Inventory/CampaignView.java` | 58.05 | Campaign GUI |
| `Managers/Inventory/CampaignCreator.java` | 58.05 | Concrete route items |

---

## Batch split

| Batch | Deliverable |
|-------|-------------|
| **58.01** | This lock + Wars.md (**done**) |
| **58.02** | Domain model, persistence, full axis, init at declare |
| **58.03** | `CampaignProgressionService` + unit tests |
| **58.04** | `OccupationBulgeService` + tests |
| **58.05** | `CampaignView`, route renderer, leader clicks |
| **58.06** | WarView Campaign button, `warstatus`, regen full axis |
| **58.07** | Docs verify + staging |

---

## Step 57 migration note

Existing wars with short `campaignProvinces` and `cursorIndex: 0` regenerate correctly via `/faction warpath` or on next declare. Unit tests expecting `cursorIndex == 0` update in **58.02**.

---

## Status

**Done** (2026-08-20). **Next batch:** [58.02 domain model](./02-domain-model.md) (TBD).
