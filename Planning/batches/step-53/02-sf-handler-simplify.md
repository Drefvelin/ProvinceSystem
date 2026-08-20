# Step 53.02 — SF handler simplify

**Repo:** `simplefactions`

## Files

| File | Action |
|------|--------|
| `settlement/handler/SettlementHandler.java` | Remove join/territory/hop/claim-growth; simplify `resolveCapital` |
| `settlement/Settlement.java` | `normalizeToCenterOnly()` on load |
| `Objects/Handler/ProvinceHandler.java` | Remove `onProvinceClaimed` hook |
| `Map/export/Markers.java` | Export `provinces: [centerProvince]` |
| `config.yml` | Remove `settlement-found-distance` |
| `Loaders/ConfigLoader.java` | Remove distance config load |
| `Cache.java` | Remove `settlementFoundDistance` |

## Removed behaviour

- `initialTerritory`, `findJoinTarget`, `join`, `minLandHops`, `minHopsToAnyCentre`, `nearestSettlement`, `isLandAdjacentToSettlement`, `onProvinceClaimed`

## Verify

- Compile: `mvn -q package -DskipTests` in `simplefactions`
- Found city on province A → `provinces` is `[A]` only
- `/setcapital` on empty adjacent province requires name (new city)
- Claim province does not grow existing settlement

## Status

**Done** (2026-08-18). Verified: `mvn package -DskipTests` passes; no hop/join/claim-growth symbols remain.

## Next

[03-dev-data-fix](./03-dev-data-fix.md)
