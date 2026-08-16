# Step 42.08 — Settlement population + marker size export

**Repos:** `Workspace/simplefactions` · `ProvinceSystem` (schema + pass-through only)  
**Depends on:** [06-ps-markers-compile](./06-ps-markers-compile.md) · [07-sf-tfmcweb-gateway](./07-sf-tfmcweb-gateway.md)

## Goal

Export **population** per settlement and a **marker size** tier (`small` | `large`) driven by SF `config.yml`. ProvinceSystem serves these fields on `GET /{map}/data/markers` unchanged (no PS-side threshold).

**Rule (v1):** `population > settlement-large-population-threshold` → `marker_size: "large"`; else `"small"`. Default threshold **8** (so 9+ guild capitals in the city = large).

`faction_capital` kind is exported unchanged; FE picks capital vs normal pin from `kind` + `marker_size` ([09](./09-frontend-markers.md) — four PNGs under `public/`, straight black label, zoom gate).

## Build

### SimpleFactions

| File | Action |
|------|--------|
| `src/main/resources/config.yml` | Add `settlement-large-population-threshold: 8` |
| `Loaders/ConfigLoader.java` | Load → `Cache.settlementLargePopulationThreshold` |
| `Cache.java` | New field (default 8) |
| `Map/export/Markers.java` | Per settlement: `population` (int), `marker_size` (`small`/`large`); root: `large_settlement_min_population` = threshold + 1 (or echo threshold — lock in build) |
| `settlement/handler/SettlementHandler.java` | Reuse `getPopulation(settlement).size()` |
| `Documentation/Settlements.md` | Map export table + config key |

**Export fields (add to schema):**

```json
{
  "map_id": "main",
  "exported_at": "2026-08-15T20:00:00Z",
  "settlement_large_population_threshold": 8,
  "settlements": [
    {
      "id": "rivendell",
      "name": "Rivendell",
      "faction_id": "elves",
      "province_id": 42,
      "population": 12,
      "marker_size": "large",
      "kind": "faction_capital",
      "map_x": 3233,
      "map_y": 1961
    }
  ]
}
```

`map_x` / `map_y` still added by PS on GET ([06](./06-ps-markers-compile.md)).

### ProvinceSystem

| File | Action |
|------|--------|
| `Planning/assets/map-export-schema.json` | `population`, `marker_size`, root `settlement_large_population_threshold` |
| `scripts/loader/markers.py` | Pass through new fields in `load_raw_markers` / `enrich_settlements` (no recomputation) |
| `scripts/loader/test_markers.py` | Fixture with population + marker_size preserved |

No regen / defines compile — markers remain live JSON from `input/`.

## Verify

- [ ] SF config threshold change → re-export → `marker_size` flips at boundary (8 vs 9 population)
- [ ] `GET /main/data/markers` includes `population`, `marker_size`, threshold on root
- [ ] Upload via TFMCWeb gateway ([07](./07-sf-tfmcweb-gateway.md)) end-to-end

## Out of scope

- PS storing threshold in defines (SF is source of truth; root field is informational for FE/debug)
- Per-guild markers

## Status

**Done** (2026-08-15). SF config + export; PS pass-through; tests + dev fixture.

## Next

[09-frontend-markers](./09-frontend-markers.md)
