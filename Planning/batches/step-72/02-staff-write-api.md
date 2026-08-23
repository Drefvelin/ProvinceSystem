# Step 72.02 — Staff write API

**Build:** ProvinceSystem backend  
**Depends on:** [01-planning-lock](./01-planning-lock.md) · [step-41/02-ps-map-registry](../step-41/02-ps-map-registry.md)  
**Playbook:** [17-map-title-editor.md](../../17-map-title-editor.md)

## Goal

Authenticated staff-only endpoints to load and save title tier JSON with validation. Close the gap where `POST /{map}/data/upload/{mode}` is world-writable for `county`, `duchy`, `kingdom`, `empire`.

## Deliverables

### 1. `require_map_staff_write(map_name, authorization)`

In [`map_access.py`](../../../backend/src/api/map_access.py) (or sibling):

- Same session check as staff map GET.
- Raises / returns 403 if not staff.
- Used by all editor write routes.

### 2. `POST /{map_name}/editor/titles/{tier}`

New router [`editor_routes.py`](../../../backend/src/api/editor_routes.py):

| Param | Values |
|-------|--------|
| `tier` | `county`, `duchy`, `kingdom`, `empire` |

Body: full tier JSON object (same shape as `defines/{map}/{tier}.json`).

**Handler:**

1. `validate_map(map_name)` + staff write auth.
2. Validate payload with `validate_title_tier(tier, body, map_name)`.
3. Strip `overlay` from each entry (regen recomputes).
4. Write `defines/{map}/{tier}.json`.
5. Clear province cache if any (`_province_cache`).
6. Return `{ "ok": true, "tier": tier, "count": N }`.

### 3. `validate_title_tier()`

New module [`editor_validation.py`](../../../backend/src/api/editor_validation.py):

| Check | County | Duchy+ |
|-------|--------|--------|
| Keys non-empty strings | yes | yes |
| `name` present string | yes | yes |
| `rgb` matches `^\d{1,3},\d{1,3},\d{1,3}$`, 0–255 | yes | yes |
| Unique `rgb` within payload | yes | yes |
| `provinces` all ints | yes | - |
| No province in two counties | yes | - |
| `titles[]` all strings | - | yes |
| Child ids exist in child tier file | - | yes |
| No child in two parents | - | yes |

Return 400 with clear `detail` string (no em dash in user-facing errors).

### 4. Gate existing upload route

In [`data_routes.py`](../../../backend/src/api/data_routes.py) `upload_region_data`:

For `mode in {county, duchy, kingdom, empire}`:

- Require staff write auth (same as new endpoint).
- Optionally route through same validator.

Nations/guilds/queue/map_markers keep current auth (plugin key hardening is separate).

### 5. `POST /{map_name}/editor/regen/{regen_type}`

Staff-only wrapper around existing regeneration:

- Accept `regen_type` like `fullregen:county`, `fullregen`, `fullregen:duchy`.
- Call `regeneration` pipeline synchronously (or same as `regen_routes` without hashed key).
- Return `{ "ok": true, "regen_type": "..." }` or error detail.

### 6. `GET /{map_name}/editor/provinces`

Staff-only:

- Parse `defines/{map}/provinces.txt`.
- Return `{ provinces: [{ id, rgb, terrain, fertility }] }`.
- Used by county mode sidebar (province count, filters later).

### 7. Tests

[`test_editor_routes.py`](../../../backend/src/api/test_editor_routes.py):

- Anonymous POST → 403.
- Staff session fixture → 200 write + file on disk.
- Duplicate province across counties → 400.
- Invalid rgb → 400.
- Duchy referencing missing county → 400.

## Files touched

| File | Change |
|------|--------|
| `backend/server.py` | Register `editor_router` |
| `backend/src/api/editor_routes.py` | New |
| `backend/src/api/editor_validation.py` | New |
| `backend/src/api/map_access.py` | `require_map_staff_write` |
| `backend/src/api/data_routes.py` | Gate title tier upload |
| `backend/src/api/test_editor_routes.py` | New |

## Done when

```bash
# staff bearer → 200
curl -X POST .../main/editor/titles/county -H "Authorization: Bearer ..." -d @county.json

# no auth → 403
curl -X POST .../main/data/upload/county -d @county.json  # also 403

pytest backend/src/api/test_editor_routes.py
```

## Status

**Done** (code + tests).

