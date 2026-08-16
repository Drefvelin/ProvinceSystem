# Step 42.05 — SF map export

**Repos:** `Workspace/simplefactions`  
**Depends on:** [03-sf-setcapital-territory](./03-sf-setcapital-territory.md)  
**Spec:** [Settlements.md](../../../../Workspace/simplefactions/Documentation/Settlements.md) — Map export

## Goal

Export all faction settlements to `plugins/SimpleFactions/MapAPI/map_markers.json` and upload as mode `map_markers` on regen.

## Package layout

```text
Map/
  export/
    Markers.java    # lowercase subpackage under Map
```

## Build

| File | Action |
|------|--------|
| `Map/export/Markers.java` | Build JSON: `map_id`, `exported_at`, `settlements[]` per schema |
| `Map/MapSystem.java` | `uploadAll()` — write + `RestServer.upload("map_markers", file)` |
| `Map/MapSystem.java` | Enqueue map regen when settlements change (if not already covered in 42.03) |

### Export row (per settlement)

| Field | Source |
|-------|--------|
| `id` | `settlement.id` |
| `name` | `settlement.name` |
| `faction_id` | owning faction id |
| `province_id` | `centerProvince` |
| `center_x` / `center_z` | block coords (PS converts to map pixels) — extend schema if needed |
| `kind` | `faction_capital` if `faction.capital == centerProvince`; else `settlement` |
| `provinces` | optional array for PS/FE tooltip v1 |

Iterate all factions in `FactionManager` for upload payload (single file per map regen).

### Upload contract

Add `map_markers` to PS allowed upload modes in [06](./06-ps-markers-compile.md).

## Verify

- [ ] After `fullRegen` / `updateMap`, `map_markers.json` exists with settlements from test faction.
- [ ] Faction with no settlements → empty `settlements` array (or omit key — lock in 42.06).

## Out of scope

- PS ingest ([06](./06-ps-markers-compile.md))
- FE rendering ([09](./09-frontend-markers.md))

## Status

**Done** (2026-08-15). `Map/export/Markers.java`, `uploadAll` export + upload, `RestServer` validation. HTTP via TFMCWeb: [42.07](./07-sf-tfmcweb-gateway.md) **done**.

## Next

[06-ps-markers-compile](./06-ps-markers-compile.md)
