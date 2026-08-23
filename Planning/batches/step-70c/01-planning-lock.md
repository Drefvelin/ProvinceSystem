# Step 70c.01 — Planning lock (geographic route GUI)

**Plan + docs only.** Supersedes GUI row rules in [70b.01](../step-70b/01-planning-lock.md) § "GUI schedule rows".  
**Repos:** `Workspace/simplefactions`, `Workspace/ProvinceSystem/Planning`  
**Depends on:** [70b.01](../step-70b/01-planning-lock.md) (schedule-only, cadence, display names)

---

## Locked — source of truth (unchanged from 70b)

| Layer | Rule |
|-------|------|
| **Persistence** | `campaignBattleSchedule` + `campaignCounterSchedule` on `War` JSON |
| **GUI** | One item per schedule slot. **Never** render axis provinces without a slot |
| **Export** | Both legs in `map_markers` wars[] mirror persistence |
| **Axis** | `campaign_provinces[]` + `cursor_index` for pathfinding, cursor push, map line |

---

## Locked — GUI route row (supersedes 70b.01)

### What the route row shows

- **Schedule-only** slots from both legs merged into one row
- **Geographic order:** sort by `campaignProvinces.indexOf(provinceId)` ascending (attacker-cap side left, defender objective side right)
- **Tie-break** at same `axisIndex`: `INVASION` leg before `COUNTER`; then `scheduleIndex` ascending within leg
- **Off-axis** slots (`axisIndex == -1`) sort last
- **No pagination:** single row, inventory slots 10-18 (9 slots); at most **8** battle items (`4` per leg hard cap)
- **Both legs** always visible (full war plan at declare)

### Slot visuals (unchanged from 70b)

| Status | Material / lore |
|--------|-----------------|
| **Fought** | Gray concrete or muted ownership; lore `Fought` |
| **Next** (active leg, active index) | Green concrete; lore `Next battle` |
| **Upcoming** | Blue/red ownership by viewer; battle kind in lore |

### First-battle marker

Below the slot at **border B**: `campaignProvinces[cursorIndex]`. When multiple slots share that province, marker targets invasion `scheduleIndex == 0`.

### Removed behavior

- Fight-order list (invasion block then counter block)
- Pagination (`ROUTE_SLOTS_PER_PAGE`, prev/next page buttons)
- Lore `Counter-push schedule`

---

## Locked — `max_battles_per_leg` cap

Hard maximum **4** per goal at config load (`Math.min(4, configured)`). Warn once if config exceeds 4.

---

## Locked — Brume vs Lantan acceptance (manual)

Axis: `452, 782, 758, 757, 672, 709, 713, 705`. Border **B** = `709` (index 5).

GUI left-to-right (geographic):

- Counter fields at **452** (capital), **782**, **672** (wilderness approach)
- Border field at **709** (first battle marker)
- Invasion siege/field toward **705** (Greenfort / Lanbury)

No `Counter-push schedule` lore. No pagination controls.

---

## Done when

- [x] Lock written; war-build-order lists step 70c
- [x] 70b.01 GUI section annotated as superseded
