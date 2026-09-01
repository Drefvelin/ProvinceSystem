# SimpleFactions integration

Map bridge between SimpleFactions on Paper and ProvinceSystem. SimpleFactions owns nations/provinces in-game; ProvinceSystem owns mapgen, PNG layers, and the web viewer.

War gameplay docs: [`../../simplefactions/docs/wars.md`](../../simplefactions/docs/wars.md).

**See also:** [map/generation.md](../map/generation.md) · [map/overview.md](../map/overview.md) · [flows/journeys.md](../flows/journeys.md)

## Role split

| Actor | Responsibility |
|-------|----------------|
| SimpleFactions | Nation/province state; enqueue regen; HTTP upload |
| TFMCWeb | `ProvinceSystemGateway` - base URL, plugin key, async HTTP |
| ProvinceSystem | Compile defines, mapgen, regiongen, serve assets |
| Website | MapViewer, modes, markers, war overlays |

SimpleFactions is **not** involved in skins, drinks, or characters.

## HTTP contract

Primary client: `Workspace/simplefactions/.../REST/RestServer.java` - delegates to TFMCWeb `ProvinceSystemGateway` via `api/GatewayClient.java`.

| Call | Purpose |
|------|---------|
| `GET {api}/{mapRef}/map/province/{x},{z}` | Resolve province under player |
| `POST {api}/{mapRef}/data/upload/{mode}` | Push nation / provinces / guilds / queue / `map_markers` / title-tier JSON (internal IP; no staff token) |
| `GET {api}/{mapRef}/{hashedKey}/api/regenerate/{type}` | `textonly`, queued, or `fullregen` |
| `GET {api}/generator/banner` | Random banner patterns |

### Config knobs

| Where | Key | Purpose |
|-------|-----|---------|
| **TFMCWeb** `config.yml` | `api.base-url`, `api.plugin-key` | ProvinceSystem HTTP (all SF map calls) |
| **SimpleFactions** `config.yml` | `map-reference` | Which map folder (`main`, `dev`, …) - must match website `mapId` |
| **SimpleFactions** `config.yml` | `enable-map` | Kill switch |

SimpleFactions **soft-depends** on TFMCWeb. With `enable-map: true` and TFMCWeb missing, SF logs a severe startup warning and map HTTP fails at runtime.

### Loopback URL rule

On the game host, `api.base-url` must point at **loopback** (e.g. `http://127.0.0.1:8000`), not the public website hostname. Uploads and regen inherit this URL. Docker NAT then shows a private peer (often `172.18.0.1`), which the API treats as internal. Calling the public `/api/` host adds `X-Forwarded-For` and is rejected. See [identity/auth-security.md](../identity/auth-security.md).

## Queue upload and regen flow

Typical claim change sequence:

1. Gameplay changes nation borders.
2. SimpleFactions enqueues affected region RGB values.
3. `POST /{map}/data/upload/…` pushes nation JSON, queue, markers, war export, etc.
4. `GET /{map}/{hashedKey}/api/regenerate/{type}` runs mapgen on ProvinceSystem.
5. Website loads updated `output/{map}/` assets.

Regen types include `textonly`, queued partial regen, and `fullregen`. Title-tier regen (`fullregen:county`, etc.) is used after staff title editor saves.

## Upload modes

Common `mode` values on `POST /{map}/data/upload/{mode}`:

- `nation` - political nation JSON
- `province_data` - province metadata
- `guilds` - guild layer data
- `queue` - pending region RGB jobs
- `map_markers` - settlements, capitals, forts
- `chronicle` - wealth / prestige / territory snapshot (see below)
- `infestation_data` - province infestation overlay (Infestations plugin)
- `county` / `duchy` / `kingdom` / `empire` - de jure title JSON (same IP gate; validated payload)
- `chronicle` - economy snapshot (faction wealth/prestige, guilds), posted every 300s; does **not** overwrite a single file like the modes above - partitioned and indexed as the **ledger**, see [map/ledger.md](../map/ledger.md)

War and chronicle extensions follow the export schema in [`docs/assets/map-export-schema.json`](../assets/map-export-schema.json). SF-side export details: [`simplefactions/docs/map-export.md`](../../../simplefactions/docs/map-export.md).

## Upload cadence

SF splits its payloads by cost. Every 300 s it ships the **live** set (`province_data`, `guilds`, `chronicle`) unconditionally, and adds the **map** set (`queue`, `nation`, `map_markers`, title JSON) only when the map queue has work. A full nation cycle runs hourly regardless.

The live-only path finishes with `GET /{map}/{hashedKey}/api/regenerate/trade`. That regen type is **not implemented yet**; it should redraw trade and prosperity overlays without touching nation borders or title geometry. Until it exists the call returns an error that SF logs and swallows, so the uploads still land.

## Chronicle ingest (not implemented)

`chronicle` arrives roughly every 5 minutes per map. Unlike every other mode it must **not** overwrite `input/{map}/chronicle.json` - the current one-path-per-mode write would keep a single snapshot and discard the season. Partition on the payload's `captured_at`, for example `chronicle/{map}/{YYYY-MM-DD}/{HH-MM}.json`, with an index for range queries, then downsample to one canonical snapshot per day for charting.

Consuming it correctly:

- **Identity.** Key on `(id, founded_at)`, not `id`. Faction ids are derived from the faction name, not a UUID, and a deleted faction's name can be reused. Renames do not happen, so the id is stable within a lifetime.
- **Deletion.** Factions vanish from the payload when deleted. Only treat an absence as a deletion when the snapshot carries `complete: true`; keep a registry with first seen, last seen and the last known `name` / `rgb` so dead nations stay on historical charts.
- **Time.** Store both `captured_at` (real instant) and `server_day` / `day_progress_seconds` (in-game). The in-game clock counts server uptime, so it drifts against wall clock across downtime.
- **Wealth.** `faction_wealth` excludes all personal player money; chart it separately from `pouch_wealth` and `player_bank_wealth` and only sum for total money supply. Wealth is a stock of liquid bank plus sunk capital in nodes and guild expansions, so chart `wealth_breakdown` rather than the total alone.
- **Prestige.** The `Wealth` component is a share of global wealth, so prestige moves when rivals get richer. Chart `prestige_breakdown` alongside `global.faction_wealth`. Rank thresholds are competitive: draw threshold lines from each faction's `rank_up_at` / `rank_down_at`, never from `ranks.yml`.
- **Deltas.** Difference consecutive daily snapshots yourself. The flow fields (`net_income`, `inflation_delta`, `guild_income`) are full-day projections, a different quantity from the observed stock change.
- **Events.** `events` is present and always empty; the stream is still unowned on the SF side.

## Multi-map

Each logical world has its own `input/{map}`, `defines/{map}`, `output/{map}` on ProvinceSystem. SF `map-reference` must match the website `mapId` for that season/world.

## Local vs live

| Mode | Map data |
|------|----------|
| Website only | Sample `input`/`defines` + manual fullregen ([ops/local-dev.md](../ops/local-dev.md)) |
| Integration | TFMCWeb `api.base-url` → local/staging API; SF `map-reference` = test mapRef |
| Production | SF on Paper → live API; players browse tfminecraft.net |

## Security note

Map regen uses a hashed key in the URL path today (MD5 segment in regenerate URL). Prefer moving the secret to config/env. Public map **read** endpoints remain low sensitivity; write/upload paths should stay on loopback or authenticated plugin routes where applicable.

## See also

- [map/wars-on-map.md](../map/wars-on-map.md) - website war layers
- [map/title-editor.md](../map/title-editor.md) - staff title JSON (not SF-uploaded)
