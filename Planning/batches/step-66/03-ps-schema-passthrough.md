# Step 66.03 — PS schema + API passthrough

**Repo:** `ProvinceSystem` (backend)  
**Depends on:** [66.02 SF wars export](./02-sf-wars-export.md)  
**Touches:** `Planning/assets/map-export-schema.json`, `backend/src/scripts/loader/`, `backend/src/api/data_routes.py`

## Goal

Validate and serve `wars[]` through the existing `map_markers` pipeline with `map_x`/`map_y` enrichment for battle slots and capital endpoints.

## Build

| File | Action |
|------|--------|
| `Planning/assets/map-export-schema.json` | Extend `$defs/war` with `campaign_battle_schedule`, `campaign_counter_schedule`, `push_target`, capital coords, slot `leg`/`status`/`kind` |
| `backend/src/scripts/loader/markers.py` (or equivalent) | Enrich war schedule slots: `province_id` → `map_x`/`map_y` via centroids or `world_coords_to_map_xy` |
| `backend/src/scripts/loader/test_markers.py` | Fixtures: wars with schedules → enriched coords |
| `backend/src/api/data_routes.py` | Ensure `get_map_markers` returns `wars` unchanged after enrichment |

### Enrichment rules

| Object | Resolution |
|--------|------------|
| Schedule slot | `resolve_province_map_xy(province_id, centroids)` |
| `attacker_capital` / `defender_capital` | Prefer `center_x`/`center_z` from export; else capital province centroid |
| `campaign_provinces` | Optional `campaign_line_points[]` precompute in loader (centroid per id) for FE convenience |

If centroid missing for a province, omit slot from enriched output and log warning (do not break entire payload).

## Verify

- [x] Upload test `map_markers` with `wars[]` accepted.
- [x] GET markers API returns wars with `map_x`/`map_y` on slots.
- [x] Schema validates sample payload from 66.02 test fixture.

## Status

**Done** (2026-08-23).

## Next

[66.04 FE campaign line](./04-fe-campaign-line.md)
