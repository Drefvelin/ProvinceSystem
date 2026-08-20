# Step 54.05 — PS/FE installation markers

**Repos:** `ProvinceSystem` · `simplefactions` (export only — done in 54.04)

Extend `map_markers.json` + API + frontend marker icons for fort, port, and airport.

See [01-planning-lock](./01-planning-lock.md) and [map-export-schema.json](../../assets/map-export-schema.json).

## Files

| File | Action |
|------|--------|
| `backend/src/scripts/loader/markers.py` | Load/enrich `installations[]`; shared `enrich_marker_rows` |
| `backend/src/scripts/loader/test_markers.py` | Installation load + enrich tests |
| `backend/src/input/dev/map_markers.json` | Sample fort + port fixtures |
| `frontend/app/components/map/types.ts` | `InstallationMarker`, extend `MapMarkersResponse` |
| `frontend/app/lib/installationMarkers.ts` | Filter + `installationToMapMarker` |
| `frontend/app/hooks/useMapMarkers.ts` | Load/filter installations |
| `frontend/app/lib/mapMarkers.ts` | `resolveMarkerImageSrc` for fort/port/airport |
| `frontend/app/components/MapViewer.tsx` | Merge settlement + installation markers |
| `frontend/public/fort.png` | Fort pin asset |
| `frontend/public/port.png` | Port pin asset |
| `frontend/public/airport.png` | Airport pin asset |

## API response

`GET /{map}/data/markers` now includes enriched `installations[]`:

```json
{
  "installations": [
    {
      "id": "lanhold",
      "name": "Lanhold",
      "kind": "fort",
      "faction_id": "Lantan",
      "province_id": 705,
      "center_x": 1748,
      "center_z": 2739,
      "map_x": 1748,
      "map_y": 2739
    }
  ]
}
```

`map_x`/`map_y` from `center_x`/`center_z` (1:1), centroid fallback when world coords absent.

## Frontend

- Installation markers use `installation:${id}` to avoid settlement id collisions
- Rendered after settlements (stack on top when co-located)
- Single small pin size per kind (`fort.png`, `port.png`, `airport.png`)

## Verify

- [x] `python -m unittest scripts.loader.test_markers -v` passes
- [x] `npm test` passes (99 tests)
- [x] `npm run build` passes
- [ ] `/map/dev` shows fort + port fixtures (manual)
- [ ] `/map/main` shows installations after SF regen upload (manual)
- [ ] Hover tooltip on installation markers (manual)

## Status

**Done** (2026-08-18).

## Next

[06-docs-verify](./06-docs-verify.md)
