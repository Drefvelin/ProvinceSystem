# Step 54.04 — SF installations

**Repo:** `simplefactions`

## Goal

Named military installations (fort, port, airport) via `/faction construct`; persist per faction; dissolve on province loss; export `installations[]` in `map_markers.json`.

See [01-planning-lock](./01-planning-lock.md).

## Files

| File | Action |
|------|--------|
| `installation/InstallationKind.java` | `FORT`, `PORT`, `AIRPORT`; `fromCommand(String)` |
| `installation/Installation.java` | Model + `toData()` |
| `installation/handler/ConstructResult.java` | Command result |
| `installation/handler/InstallationHandler.java` | CRUD, validation, dissolve |
| `Database/InstallationData.java` | Gson DTO |
| `Objects/Faction.java` | `installationHandler`; `validate()` in `tick()` |
| `Database/FactionData.java` | `installations` list |
| `Database/Database.java` | Load/save installations |
| `Objects/Handler/ProvinceHandler.java` | `onProvinceLost` → dissolve installations |
| `Managers/CommandManager.java` | `/faction construct <kind> <name...>` |
| `Utils/TabCompletion.java` | `construct` + kind tab complete |
| `Map/export/Markers.java` | Export `installations[]` |
| `REST/RestServer.java` | `installations` optional array in upload validation |
| `config.yml` | `installations:` slot stubs (reserved for future) |

## Command

```
/faction construct <fort|port|airport> <name...>
```

Leader only. One installation of each kind per province (direct faction ownership). Port requires within `port-sea-proximity-blocks` of sea/river.

## Map export

```json
"installations": [
  {
    "id": "lanhold",
    "name": "§aLanhold",
    "kind": "fort",
    "faction_id": "Lantan",
    "province_id": 705,
    "center_x": 1748,
    "center_z": 2739
  }
]
```

## Verify

- [x] `mvn package -DskipTests` passes
- [ ] `/faction construct fort &aTest` on owned land succeeds (manual)
- [ ] Second fort same province rejected; fort on second province OK (manual)
- [ ] Construct in province not directly owned (vassal land) rejected (manual)
- [ ] Port inland rejected; coastal within `port-sea-proximity-blocks` OK (manual)
- [ ] Unclaim province dissolves installation (manual)
- [ ] `MapAPI/map_markers.json` contains `installations[]` after construct (manual)

## Status

**Done** (2026-08-18).

## Next

[05-ps-fe-markers](./05-ps-fe-markers.md)
