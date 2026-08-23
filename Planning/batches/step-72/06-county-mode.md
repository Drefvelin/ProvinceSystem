# Step 72.06 — County mode

**Build:** ProvinceSystem frontend  
**Depends on:** [05-province-pick-layer](./05-province-pick-layer.md) · [03-title-rgb-picker](./03-title-rgb-picker.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Full **county** tier: create county from province clicks, edit name/colour/members, delete county. Sidebar and draft logic wired to map.

## Deliverables

### 1. Assignment maps

[`frontend/app/lib/map/editor/countyAssignment.ts`](../../../frontend/app/lib/map/editor/countyAssignment.ts)

From draft `county.json`:

- `provinceToCountyId: Map<number, string>`
- `unassignedProvinces(provinceIds, assignment)`
- `canSelectProvince(pid, editingId, assignment)` - false if assigned to another county

### 2. County sidebar UX

Extend `TitleSidebar` for county tier:

| Control | Behavior |
|---------|----------|
| Title list | All counties sorted by name; colour chip |
| **New county** | Clears selection; generates `COUNTY_N` id; suggest rgb from first click |
| Name field | Updates `draft[id].name` |
| `TitleRgbPicker` | Updates `draft[id].rgb`; `usedRgbs` from other counties |
| Member count | `N provinces` |
| **Delete** | Confirm modal; remove key from draft |

Selecting list item → `selectedId` → active layer shows that county.

### 3. Click handling (county)

While `selectedId` set (edit or new):

- Click unassigned province → add to `selectionSet` (highlight).
- Click selected province → remove from selection.
- Click province owned by other county → ignore (tooltip: "Assigned to {name}").

**Apply selection to draft:**

- On each toggle OR explicit **Add to county** button: merge `selectionSet` into `draft[selectedId].provinces`.
- Clear `selectionSet` after merge.

Alternative (match Tkinter): toggling immediately updates `provinces[]` on selected county - **locked: immediate update** (no separate Apply button).

### 4. Create county flow

1. New → empty `provinces: []`, default name `COUNTY_N`, rgb from `tweakRgbNear` of first province or grey.
2. Staff clicks provinces → `provinces[]` grows.
3. Rename → Save draft locally (dirty).

### 5. Edit county flow

1. Pick from list → populate form.
2. Click province in county → remove from `provinces[]`.
3. Click unassigned → add.
4. Rename / recolour.

### 6. Empty state

No county selected: selection layer shows all counties at 40%; message "Select a county or create new".

## Tests

- `countyAssignment` duplicate detection.
- Draft reducer: add/remove province, delete county.

## Done when

- Full county CRUD in UI without upload (dirty flag set).
- Live paint reflects all counties + current edit.
- 64 counties on `main` load and display in list.

## Status

Done.
