# Step 42.06 — PS markers compile + API

**Repos:** `ProvinceSystem` backend  
**Depends on:** [05-sf-map-export](./05-sf-map-export.md) · [map-export-schema.json](../../assets/map-export-schema.json)

## Goal

Accept SF `map_markers` upload, store under defines/input, serve via GET for map viewer.

## Build

| File | Action |
|------|--------|
| `backend/src/api/data_routes.py` | Add `map_markers` to allowed upload modes |
| `backend/src/...` (upload handler) | Write uploaded JSON to `input/{map}/map_markers.json` (or defines — match guilds pattern) |
| `backend/src/api/data_routes.py` or new route | `GET /{map}/data/markers` → settlement list for FE |
| `scripts/...` | If compile step needed for regen queue, hook like `guilds` / `province_data` |

### API shape (proposed)

`GET /{map}/data/markers`

```json
{
  "settlements": [
    {
      "id": "rivendell",
      "name": "Rivendell",
      "faction_id": "elves",
      "province_id": 42,
      "center_x": 1200,
      "center_z": -3400,
      "kind": "settlement",
      "provinces": [42, 43, 44]
    }
  ]
}
```

### Map pixel coords

**v1 (locked):** `map_x` / `map_y` on GET response are derived from `defines/{map}/province_centroids.json` for each settlement's `province_id` (`round(centroid.x)`, `round(centroid.y)`). SF `center_x` / `center_z` (Minecraft block coords) are passed through unchanged for future fine placement; no world→pixel transform exists yet.

## Verify

```bash
cd backend/src
# upload test map_markers.json via SF or curl POST
curl http://localhost:8000/main/data/markers
```

- [ ] Upload mode accepts `map_markers`
- [ ] GET returns settlements after regen
- [ ] Staff map `dev` respects map access gate from step 41

## Out of scope

- Frontend markers ([09](./09-frontend-markers.md)); population size ([08](./08-sf-marker-size-export.md))

## Status

**Done** (2026-08-15). Upload mode, `GET /data/markers`, centroid enrichment, tests.

## Next

[07-sf-tfmcweb-gateway](./07-sf-tfmcweb-gateway.md)
