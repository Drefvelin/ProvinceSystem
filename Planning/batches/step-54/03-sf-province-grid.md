# Step 54.03 — SF province grid

**Repo:** `simplefactions`

## Goal

Load `Input/province_id_grid.bin.gz`; replace HTTP `RestServer.getProvince()` with O(1) local lookup; add `ProvinceSpatial` for port checks (54.04).

See [01-planning-lock](./01-planning-lock.md).

## Files

| File | Action |
|------|--------|
| `Map/ProvinceGrid.java` | Load gzip grid; `getAt(x, z)` |
| `Map/ProvinceSpatial.java` | `isSeaAt`, `withinBlocksOfSea`, `withinConfiguredPortSeaProximity` |
| `SimpleFactions.java` | Load grid on enable; fail loud if missing; `getProvinceGrid()` |
| `REST/RestServer.java` | `getProvince(Player)` → grid (no HTTP) |
| `Cache.java` / `ConfigLoader.java` / `config.yml` | `port-sea-proximity-blocks` (default 20) |
| `src/main/resources/Input/province_id_grid.bin.gz` | Dev copy from PS defines (6400×6400) |

## Input path

`plugins/SimpleFactions/Input/province_id_grid.bin.gz` — copy from `ProvinceSystem/backend/src/defines/{map}/province_id_grid.bin.gz` after running 54.02 script.

## Verify

- [x] `mvn package -DskipTests` passes
- [x] Grid loads on enable; plugin disables if file missing
- [x] `RestServer.getProvince` uses `ProvinceGrid` (no `GatewayClient` for lookup)
- [x] `port-sea-proximity-blocks` in config (default 20)
- [ ] In-game spot-check claim/setcapital (manual)

## Status

**Done** (2026-08-18).

## Next

[04-sf-installations](./04-sf-installations.md)
