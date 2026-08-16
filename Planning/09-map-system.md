# 09 — Map system (SimpleFactions ↔ ProvinceSystem)

> **Product truth:** [16-map-platform.md](./16-map-platform.md). This doc covers the existing SF ↔ API ↔ web pipeline.

End-to-end **interactive world map**: faction data on the Paper server becomes PNG layers and JSON on the website.

Perf/UX work (cropped overlays, hover, mobile): [04-map-performance.md](./04-map-performance.md).  
Website baseline: [01-current-state.md](./01-current-state.md).

## Components

| Piece | Path | Job |
|-------|------|-----|
| SimpleFactions | `Workspace/simplefactions/` | Owns nations/provinces; talks HTTP to API |
| ProvinceSystem API | `ProvinceSystem/backend/` | Upload defines, regen maps/regions, serve files |
| ProvinceSystem web | `ProvinceSystem/frontend/` | MapViewer, modes, drill-down |
| Data | `backend/src/input|defines|output/{map}/` | Per-map worlds (`main`, `dev`, …) |

## Flow

```mermaid
sequenceDiagram
  participant SF as SimpleFactions
  participant API as ProvinceSystem_API
  participant Disk as output_and_defines
  participant Web as Next_MapViewer

  SF->>SF: claim change enqueues RGB
  SF->>API: POST map data upload nation or queue
  SF->>API: GET regenerate queued or fullregen
  API->>Disk: process_nations mapgen regiongen
  Web->>API: GET data and mapdata and regions
  Web->>Web: compose overlays hover drill-down
```

## SimpleFactions REST

Primary client: `Workspace/simplefactions/.../REST/RestServer.java` — delegates to TFMCWeb `ProvinceSystemGateway` via `api/GatewayClient.java`.

| Call | Purpose |
|------|---------|
| `GET {api}/{mapRef}/map/province/{x},{z}` | Resolve province under player |
| `POST {api}/{mapRef}/data/upload/{mode}` | Push nation / provinces / guilds / queue / `map_markers` JSON |
| `GET {api}/{mapRef}/{hashedKey}/api/regenerate/{type}` | `textonly`, queued, or `fullregen` |
| `GET {api}/generator/banner` | Random banner patterns |

Config knobs:

| Where | Key | Purpose |
|-------|-----|---------|
| **TFMCWeb** `config.yml` | `api.base-url`, `api.plugin-key` | ProvinceSystem HTTP (all SF map calls) |
| **SimpleFactions** `config.yml` | `map-reference` | `Cache.mapRef` — which map folder (`main`, `dev`, …) |
| **SimpleFactions** `config.yml` | `enable-map` | `Cache.mapEnabled` — kill switch |
| SF source | regen path hash | MD5 segment in regenerate URL (move to config in a later security batch) |

SimpleFactions **soft-depends** on TFMCWeb; with `enable-map: true` and TFMCWeb missing, SF logs a severe startup warning and map HTTP fails at runtime.

Claim changes typically `enqueue("nation", rgb)` then later upload queue + regenerate.

## ProvinceSystem map pipeline

1. Load/compile nation (and other modes) into `defines/{map}/`.  
2. `create_map` / `generate_regions` write `output/{map}/maps/` and `regions/`.  
3. [`file_routes`](../backend/src/api/file_routes.py) serves PNGs; data routes serve JSON (including `GET /{map}/data/markers` for settlement pins).  
4. Frontend uses `NEXT_PUBLIC_API_URL` + `mapId` (e.g. `/map/main`); `MapSettlementMarkers` renders pins + straight labels on political modes when zoomed in.

Generators on `dev` are fast; browser cost is still full-size region overlays until [04](./04-map-performance.md) lands.

## Multi-map

Each logical world has its own `input/{map}`, `defines/{map}`, `output/{map}`. SimpleFactions `mapRef` must match the website `mapId` for that season/world.

## Local vs live

| Mode | Map data |
|------|----------|
| Website only | Sample `input`/`defines` + one-shot regen → `output` ([06](./06-local-development.md)) |
| Integration | TFMCWeb `api.base-url` → local/staging API; SF `map-reference` = test mapRef |
| Production | SF on Paper → live API; players browse tfminecraft.net |

SimpleFactions is **not** involved in skins.

## Implementation notes (map track)

See [16-map-platform.md](./16-map-platform.md) steps 37–45. Technical perf detail: fix hover card, cropped PNGs, SF config hygiene.

## See also

- [12-end-to-end-flows.md](./12-end-to-end-flows.md) — journey “map border update”  
- [03-roadmap.md](./03-roadmap.md) — Track A  
- [08-implementation-checklist.md](./08-implementation-checklist.md) — Map track tasks  
