# Step 43.02 — SF `forts[]` export

**Repo:** `simplefactions`

Export operational forts with SF-computed `zoc_provinces` in `map_markers.json`.

## Tasks

1. Add `Map/export/ZocRealm.java` — `topRealmId`, `sameTopRealm`, `computeZocProvinces`
2. Extend `Markers.export()` — `forts[]` for `InstallationKind.FORT` only
3. Validate `forts` array in `RestServer` map_markers upload
4. Update `map-export-schema.json` — `fort.center_x`, `fort.center_z`, `zoc_provinces` description

## Files

| File | Action |
|------|--------|
| `Map/export/ZocRealm.java` | New — ZOC province selection |
| `Map/export/Markers.java` | Export `forts[]` |
| `REST/RestServer.java` | Validate `forts` array type |
| `Documentation/Installations.md` | Fort ZOC export section |
| `Planning/assets/map-export-schema.json` | Fort schema fields |

## Done when

- `mvn -q package -DskipTests` passes
- After regen: `map_markers.json` has `forts[]` with `zoc_provinces` per operational fort
- Foreign / sea / unclaimed neighbors excluded from `zoc_provinces`

## Status

**Done** (2026-08-19).

## Next

[03-ps-zocgen](./03-ps-zocgen.md)
