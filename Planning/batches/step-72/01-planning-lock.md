# Step 72.01 — Planning lock

**Plan + docs only.** Lock map title editor scope, UX, API, and data contracts before implementation batches 72.02–72.11.

**Repos:** Planning (+ `ProvinceSystem` for later batches)  
**Depends on:** [00-index](./00-index.md) · [step-41/01-planning-lock](../step-41/01-planning-lock.md) · [step-47/01-planning-lock](../step-47/01-planning-lock.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Locked — why now

Steps 37–49 shipped a read-only political map viewer with pan/zoom, pick canvas, and title labels. Title hierarchy JSON (`county`, `duchy`, `kingdom`, `empire`) is still maintained by hand or via unauthenticated `POST /data/upload`. Lore staff need a guided web tool to combine provinces into counties and roll up higher tiers before Calavorn goes public with correct names and borders.

## Locked — users and permissions

| Actor | Access |
|-------|--------|
| Anonymous / player | No editor route; viewer unchanged |
| Profile logged in, no staff flag | Editor shows permission gate (same copy as `MapAccessGate`) |
| Staff (`tfmc.map.staff`) | Full editor for any map in registry (`main`, `dev`, future staff maps) |

Auth model matches step 41: character Bearer session + `has_map_staff_access(player_uuid, realm_id, staff_permission)`.

## Locked — editor route and nav

| Piece | Choice |
|-------|--------|
| URL | `/map/editor` |
| Map selector | Dropdown: all maps staff can access (`GET /maps/accessible`) |
| Default map | `main` if accessible, else first staff map |
| Nav | `SiteHeader` link "Map editor" only when session has staff map access (mirror dev map link pattern) |
| No obfuscated URL | Editor is staff tool; not hidden like `/map/r3b1rth` |

> **Superseded by [step 73.01](../step-73/01-planning-lock.md) (2026-08-23):** global nav "Map editor" link, staff map nav links (e.g. Adavaar), and in-editor map dropdown are **removed**. Entry is **Edit titles** on the map viewer; editor requires `?map=main|dev` with no map switcher. Step 72 history retained above.

Query params (optional v1):

- `?map=main` - preselect map
- `?tier=county` - preselect tier tab

## Locked — tier modes

| Editor tier | Child selection unit | Pick source | JSON file | Member field |
|-------------|---------------------|-------------|-----------|--------------|
| County | Province id | Province RGB (`provinces.png` aligned pick) | `county.json` | `provinces[]` |
| Duchy | County id | County pick map `mapdata/county` | `duchy.json` | `titles[]` |
| Kingdom | Duchy id | `mapdata/duchy` | `kingdom.json` | `titles[]` |
| Empire | Kingdom id | `mapdata/kingdom` | `empire.json` | `titles[]` |

**Not in v1:** nation, trade, guild, terrain/fertility/prosperity modes.

### Tier tab UX

Horizontal tabs: **County · Duchy · Kingdom · Empire**. Switching tier:

- Loads that tier's JSON into draft state.
- Resets selection (does not auto-save).
- Rebuilds selection + active paint layers.
- Pick canvas switches to correct pick map.

## Locked — visual layer model

```text
z-order (bottom → top):
  1. Base terrain image (/{map}/map)
  2. Selection layer (~SELECTION_OPACITY = 0.40)
  3. Active layer (~ACTIVE_OPACITY = 0.90)
  4. Pick canvas (opacity 0, pointer events)
```

| Layer content | County tier | Duchy tier |
|---------------|-------------|------------|
| Selection layer | Unassigned provinces in muted province colours; assigned provinces show owning county colour at low opacity | All counties at low opacity |
| Active layer | Current county colour on its provinces; click selection uses distinct highlight (e.g. accent purple like Tkinter `SELECT_COLOR`) | Current duchy colour on member counties; county click selection highlighted |
| Already assigned to **other** titles | Not clickable in create mode; shown in selection layer only | Child already in another duchy not clickable |

Constants (tune in 72.05 visual pass):

```ts
export const EDITOR_SELECTION_OPACITY = 0.40;
export const EDITOR_ACTIVE_OPACITY = 0.90;
export const EDITOR_SELECTION_HIGHLIGHT = "160,80,200"; // R,G,B for in-progress clicks
```

Public viewer parchment wash (`display_colour.py`) applies on **published** maps only. Editor paints **raw stored RGB** so staff see the colour they are saving.

Optional toggle (72.05): "Preview on map" applies client-side wash approximation for WYSIWYG.

## Locked — interaction model

Reuse viewer pan/zoom (`useMapViewport`, `screenToMap` from step 49).

| Input | Action |
|-------|--------|
| Scroll wheel | Zoom toward cursor |
| Middle mouse drag | Pan |
| Left click | Toggle province/county/etc. in current selection (if allowed) |
| Shift+click | Optional: flood-select connected component (defer if costly; document as follow-up) |

**Create flow:**

1. Click **New title** (or auto-enter create after New).
2. Type **name** in sidebar field.
3. Pick **colour** via `TitleRgbPicker`.
4. Click map to add members.
5. **Save** (local draft commit) or **Save & upload** (72.09).

**Edit flow:**

1. Select title from sidebar list.
2. Fields populate; map shows that title as active layer.
3. Click to add/remove members (remove = click assigned member while editing).
4. Save.

**Delete flow:**

1. Select title → **Delete** → confirm modal with title name.
2. Removes entry from draft; members become unassigned (county tier) or return to selection pool (higher tiers).

## Locked — colour rules

| Rule | Detail |
|------|--------|
| Storage | `"R,G,B"` integers 0–255 in JSON |
| Picker UI | Native `<input type="color">` + hex field; match `NameColourPicker` chip styling |
| Uniqueness | Warn if RGB collides with another title in **same tier file** |
| Auto-suggest | On create, suggest `tweak_rgb_near` from first member colour (port from `county_editor.py`) |
| Province colours | Immutable in editor - from `provinces.txt` |

## Locked — id generation

On **New title**:

```text
COUNTY_{max+1}   / DUCHY_{max+1}   / KINGDOM_{max+1}   / EMPIRE_{max+1}
```

Scan existing keys for highest numeric suffix. Id is stable after create (rename changes `name` only, not key).

## Locked — draft state

Client-side draft per tier:

```ts
type TitleDraft = Record<string, {
  name: string;
  rgb: string;
  provinces?: number[];
  titles?: string[];
}>;
```

- `dirty` flag per tier when draft differs from server snapshot.
- Load server JSON on map/tier change via `GET /{map}/data/{tier}`.
- Unsaved changes warning on tier switch or map switch.

Server is source of truth until upload succeeds.

## Locked — API (summary)

See [02-staff-write-api](./02-staff-write-api.md) for implementation detail.

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `GET /{map}/data/{tier}` | Staff map access | Load tier JSON (existing) |
| `POST /{map}/editor/titles/{tier}` | Staff only | Replace full tier JSON with validation |
| `POST /{map}/data/upload/{tier}` | **Gate** for title tiers | Existing path; require staff OR deprecate for titles |
| `POST /{map}/editor/regen/{regen_type}` | Staff only | Trigger `fullregen:county` etc. without hashed plugin key |
| `GET /{map}/editor/provinces` | Staff only | Province id list + rgb + terrain (for sidebar) |

Validation on write:

- `rgb` format regex `^\d{1,3},\d{1,3},\d{1,3}$` with 0–255 range.
- County: `provinces` unique ints; no duplicate province across counties in payload.
- Duchy+: `titles[]` reference existing child ids; no child in two parents in same payload.
- Strip `overlay` from client payload (server ignores or strips on write).

## Locked — regen contract

After upload, operator clicks **Regenerate map**:

| Tier saved | Regen call | Also regen |
|------------|------------|------------|
| county | `fullregen:county` | Parent tiers if their colours derive from children (queued OK) |
| duchy | `fullregen:duchy` | kingdom, empire if exist |
| kingdom | `fullregen:kingdom` | empire if exists |
| empire | `fullregen:empire` | - |

Use existing `regeneration.py` / `parse_regen_type` (`fullregen:{mode}`).

Show spinner + success/error; link **Open map viewer** in new tab.

## Locked — reuse from existing code

| Source | Reuse |
|--------|-------|
| `MapCanvas.tsx` / `MapViewport` | Pan/zoom wrapper |
| `useMapCoords` / `screenToMap` | Click → map pixel |
| `MapAccessGate.tsx` | Permission UI |
| `fetchMapApi` + Bearer | API client |
| `titleProvinces.ts` | Resolve child provinces for paint |
| `county_editor.py` | `tweak_rgb_near`, province map build, selection paint |
| `NameColourPicker.tsx` | Chip + native color input styling |
| `colour_mapping.py` | Server-side validation reference |

## Locked — Calavorn prep (operator)

Documented in [10-main-calavorn-prep](./10-main-calavorn-prep.md):

1. Backup `defines/main/{duchy,kingdom,empire}.json`.
2. Replace with `{}` or minimal stub.
3. Regen `fullregen:duchy` (or fullregen) so viewer clears higher tiers.
4. Counties: rename in editor county mode (64 entries).
5. Rebuild duchy → kingdom → empire in editor.
6. Final `fullregen` + QA on `/map/main`.

## Locked — tests

| Area | Tests |
|------|-------|
| API | Staff 403 without flag; validation rejects bad rgb and duplicate provinces |
| `TitleRgbPicker` | hex ↔ rgb string round-trip |
| Paint utils | province toggle, membership maps |
| `tweak_rgb_near` | port to TS or shared test against Python fixture |

## Out of scope (v1)

- Province geometry editor (`province_editor.py`).
- Nation / trade layers.
- Incremental queued regen from editor (use fullregen per tier for simplicity).
- Draft persistence across browser sessions (localStorage optional follow-up).
- Undo/redo stack (optional follow-up).

## Status

**Locked** — proceed to 72.02.
