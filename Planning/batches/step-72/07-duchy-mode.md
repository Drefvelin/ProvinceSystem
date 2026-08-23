# Step 72.07 — Duchy mode

**Build:** ProvinceSystem frontend  
**Depends on:** [06-county-mode](./06-county-mode.md) · [05-province-pick-layer](./05-province-pick-layer.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

**Duchy** tier: combine counties into duchies. Selection layer shows all counties at low opacity; active duchy at high opacity. Pick map uses county RGB (`mapdata/county` pick-safe).

## Deliverables

### 1. Child tier pick

`useEditorPick` extension:

- Tier `duchy` → load `GET /{map}/mapdata/county` into pick canvas.
- `rgbToCountyId` built from `county.json` draft + server snapshot.

### 2. `duchyAssignment.ts`

- `countyToDuchyId: Map<string, string>`
- `canSelectCounty(countyId, editingDuchyId, assignment)`

### 3. Paint at county granularity

Active/selection layers paint **all provinces** of each county (use `resolveCountyProvinces` from [`titleProvinces.ts`](../../../frontend/app/lib/titleProvinces.ts)):

- Selection layer: every county's `rgb` at 40% opacity.
- Active layer: member counties at 90% with duchy `rgb` (or county rgb tinted - **locked: use duchy rgb** on all member province pixels).

### 4. Sidebar

Same pattern as county mode but:

- Member count: `N counties`
- List shows duchy name + chip
- `titles[]` holds county ids

### 5. Click handling

- Pick county id from pick canvas RGB.
- Toggle county in `draft[duchyId].titles[]`.
- Cannot select county assigned to another duchy.

### 6. Prerequisite warning

If `county.json` empty or draft dirty unsaved, banner: "Save counties before editing duchies."

## Tests

- Paint: county membership expands to correct province set.
- Assignment: county in two duchies rejected in draft validator client-side.

## Done when

- Switch to Duchy tab → counties visible dimmed; click builds duchy membership.
- Create/edit/delete duchy in draft.
- Pick uses county colours accurately.

## Status

Done.
