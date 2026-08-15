# Step 41.02 — Map registry + route guards

**Repos:** `ProvinceSystem` backend  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Goal

Ship `maps.yml` registry loader, `ensure_map_access` on all map viewer GET routes, and `GET /maps/accessible`.

## Build

| File | Action |
|------|--------|
| [`backend/src/config/maps.yml`](../../../backend/src/config/maps.yml) | Registry: `main` public, `dev` staff-only |
| [`backend/requirements.txt`](../../../backend/requirements.txt) | Add `pyyaml` |
| [`backend/src/api/map_registry.py`](../../../backend/src/api/map_registry.py) | `MapEntry`, `load_map_registry`, `get_map_entry`, `list_map_entries`; `MAP_REGISTRY_PATH` env override |
| [`backend/src/api/map_access.py`](../../../backend/src/api/map_access.py) | `ensure_map_access`, `list_accessible_maps`, Bearer + character session + `permission_flags` |
| [`backend/src/api/maps_routes.py`](../../../backend/src/api/maps_routes.py) | `GET /maps/accessible` |
| [`backend/server.py`](../../../backend/server.py) | Register `maps_router` |
| [`backend/src/api/map_routes.py`](../../../backend/src/api/map_routes.py) | Guard all GET handlers |
| [`backend/src/api/data_routes.py`](../../../backend/src/api/data_routes.py) | Guard GET handlers; upload POST unchanged (`validate_map` only) |
| [`backend/src/api/file_routes.py`](../../../backend/src/api/file_routes.py) | Guard all GET handlers |
| [`backend/src/api/test_map_access.py`](../../../backend/src/api/test_map_access.py) | Registry, unit, and API tests (16 cases) |

### Registry shape

```yaml
maps:
  - id: main
    public: true
    display_name: Calavorn
    realm_id: main
  - id: dev
    public: false
    display_name: Adavaar
    realm_id: dev
    staff_permission: tfmc.map.staff
```

### Access rules (locked)

| Case | HTTP |
|------|------|
| Unknown map id | 404 |
| Public map (`main`) | 200 (file may still 404) |
| Staff map, no Bearer / invalid session | 403 — `Staff map access required` |
| Staff map, session without flag | 403 — `Staff map permission required` |
| Staff map, session + `permission_flags["tfmc.map.staff"]` on map `realm_id` | 200 |

Staff gate uses **character scope** Bearer only. `validate_map()` remains for upload/regen/scripts.

### Listing route

| URL | Response |
|-----|----------|
| `GET /maps/accessible` | `{ "maps": [{ "id", "display_name", "public" }, ...] }` |

Anonymous callers see `main` only; staff session with flag sees `main` + `dev`.

## Verify

```bash
cd backend/src
python -m unittest api.test_map_access -v
```

- [x] `python -m unittest api.test_map_access -v` passes (16 tests)
- [x] Unknown map `GET /notamap/data/nation` → 404
- [x] Anonymous `GET /dev/data/nation` → 403
- [x] Anonymous `GET /main/data/nation` → not 403
- [x] `GET /maps/accessible` anonymous → `main` only
- [ ] Smoke: backend running — `curl` anonymous `main` OK, `dev` 403

## Out of scope

- TFMCWeb `sync-permissions` operator doc ([03-staff-session](./03-staff-session.md))
- Frontend nav + Bearer on fetches ([04-frontend-gate](./04-frontend-gate.md))
- `POST /{map}/data/upload/{mode}` guard

## Status

**Done.**

## Next

[03-staff-session](./03-staff-session.md).
