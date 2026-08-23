# Step 70b.01 — Planning lock (schedule simplicity)

**Plan + docs only.** Lock rules before code.  
**Repos:** `Workspace/simplefactions`, `Workspace/ProvinceSystem/Planning`  
**Depends on:** [70.01](../step-70/01-planning-lock.md)  
**Authoritative after 70b.06:** [Wars.md](../../../../simplefactions/Documentation/Wars.md)

**Status:** **Done** (2026-08-23).

---

## Locked — source of truth

| Layer | Rule |
|-------|------|
| **Persistence** | `campaignBattleSchedule` + `campaignCounterSchedule` on `War` JSON are the **only** battle list |
| **GUI** | One item per schedule slot. **Never** render axis provinces without a slot |
| **Export** | `campaign_battle_schedule` + `campaign_counter_schedule` in `map_markers` wars[] mirror persistence |
| **Axis** | `campaign_provinces[]` + `cursor_index` remain for pathfinding, cursor push, map line only |

---

## Locked — leg walks (unchanged from 70)

Axis: `mergeAxisPaths(attackerCapital → borderB, borderB → objective)`.

| Leg | Walk on axis | First slot province | Terminal |
|-----|--------------|---------------------|----------|
| **Invasion** | `borderIndex → objectiveIndex` (increasing) | `campaignProvinces[borderIndex]` | Required `FIELD` at objective |
| **Counter** | `borderIndex - 1 → aggressorCapitalIndex` (decreasing) | `campaignProvinces[borderIndex - 1]` | Required `FIELD` at aggressor capital (when on axis) |

**Center** = border **B** (`cursor_index` at declare). Counter starts one tile **left** of B (wilderness / attacker approach), not on B itself.

---

## Locked — natural slot insertion (per leg)

Walk the leg segment once. At each axis step, in order:

1. **Siege** — enemy-controlled fort ZOC entered (once per fort id)
2. **Naval** — enemy port blocks sea run on segment
3. **Naval invasion** — first enemy land after sea (unless siege replaces)
4. **Field cadence** — see below (non-terminal provinces only)
5. After walk — **required terminal** field at objective / capital if not already `required`

Sieges, naval, and terminal slots **do not** suppress cadence on the **same** province when rules both apply (existing dedupe: one field + siege at same id is allowed; siege + required objective at capital is allowed).

---

## Locked — field cadence (70b change)

**Config:** `war.battle_cadence.provinces_between_battles: 3` (was `1` on dev; value applied in [70b.02](./02-cadence-config.md)).

**Algorithm (grid from leg start; matches `CampaignScheduleBuilder.cadenceMatches`):**

| Leg | `cadenceOrigin` | Offset at axis step |
|-----|-----------------|---------------------|
| **Invasion** | `borderIndex` | `abs(axisIndex - borderIndex)` |
| **Counter** | `borderIndex - 1` | `abs(axisIndex - (borderIndex - 1))` |

Place a **non-required field** slot when:

```text
axisIndex != terminalIndex
AND offset % N == 0
```

(`offset == 0` includes the first tile of the leg, e.g. border B on invasion or `borderIndex - 1` on counter.)

| N | Invasion example (B→obj, 3 tiles) | Counter example (672→452, 4 wilderness) |
|---|-------------------------------------|----------------------------------------|
| 3 | Field at B; next at B+3 if room | Field at 672; field at 782; required at 452 |

This is **not** step-since-last-battle counting. Sieges, naval, and required terminal slots can sit on the same province as a cadence field or immediately adjacent. If playtest feels wrong, 70b.02 may revisit; document any delta in [70b.06](./06-docs-verify.md).

**Not cadence:** sieges, naval, required terminal.

---

## Locked — trim (unchanged)

Each leg trimmed independently to `max_battles_per_leg` (default **4**). Drop order: non-required `FIELD` (farthest from terminal first) → `NAVAL_INVASION` → `NAVAL` → `SIEGE` → never drop `required`.

---

## Locked — GUI schedule rows

> **Superseded (70c.01):** Geographic axis order, no pagination, border-B marker. See [70c.01](../step-70c/01-planning-lock.md).

### What the route row shows

- **Single paginated list** in **fight order** (not geographic axis order) — **obsolete after 70c**
- **All invasion slots** first: `campaignBattleSchedule[0..n-1]`
- **All counter slots** second: `campaignCounterSchedule[0..m-1]`
- Both legs **always visible** (full war plan at declare), regardless of active `pushTarget`
- Pagination: 9 slots per page (`ROUTE_SLOTS_PER_PAGE`); page 0 starts at invasion schedule index 0
- Optional lore on first counter entry: `Counter-push schedule` (cosmetic; [70b.03](./03-schedule-only-gui.md))

The route row is **not** aggressor-left / defender-right per province. Axis geography is for the web map line and cursor only.

### Slot visuals

| Status | Material / lore |
|--------|-----------------|
| **Fought** (`index < activeIndex` on that leg) | Gray concrete or muted ownership; lore `Fought` |
| **Next** (active leg, `index == activeIndex`) | Green concrete; lore `Next battle` |
| **Upcoming** | Blue/red ownership by viewer; battle kind in lore |

### First-battle marker

Points to **invasion schedule index 0** (border fight), not "first slot on axis geography".

### Removed behavior

- No `CampaignRouteEntry` with `scheduleIndex == -1`
- No `resolveRouteDisplayName` branch for `slot == null`
- No upcoming-only filter that hides fought slots (show full schedule for campaign overview)

---

## Locked — display names

Player-facing title per slot (GUI item name + optional export):

| Kind | Pattern |
|------|---------|
| Field | `{ordinal}Battle of {location}` |
| Siege | `{ordinal}Siege of {location}` |
| Naval / invasion | Same as field template with kind in lore |

**Location** resolution order (unchanged): settlement name → fort name → county title → `Wilderness`.

**Ordinal** for a slot at render/export time:

```text
ordinal = locationBattleCounts[key] + 1 + count(previous slots in SAME leg with same location key)
```

So two scheduled fields at `Lanbury` before any are fought → `Battle of Lanbury`, then `Second Battle of Lanbury`.

Siege at fort uses `fort:{installationId}` key.

---

## Locked — Brume vs Lantan acceptance (manual)

Axis (main map): `452, 782, 758, 757, 672, 709, 713, 705`. Border **B** ≈ `709` (index 5).

**Invasion** (after trim, expect ≤4 slots):

- Field at or near border (`709`)
- Siege of Greenfort (axis tile 713 or 705 per ZOC anchor rules)
- Required field at Lanbury (`705`)

**Counter** (must include wilderness before Brume capital):

- Walk: `672 → 757 → 758 → 782 → 452`
- With N=3: fields at **672** and **782** in wilderness, required at **452**
- At least **one** non-terminal field battle in provinces `672–782`

GUI must list exactly these slots (no wilderness filler tiles). `warschedule` / war JSON must include `campaignCounterSchedule` non-empty.

---

## Done when

- [x] This doc reviewed and treated as lock for 70b.02–70b.06
- [x] GUI pagination locked: invasion slots then counter slots, both always visible, single paginated list
