# Step 42.07 — SimpleFactions via TFMCWeb gateway

**Repos:** `Workspace/simplefactions` · `Workspace/tfmcweb`  
**Depends on:** [05-sf-map-export](./05-sf-map-export.md) · [step-35 HTTP gateway](../step-35/00-http-gateway-per-realm.md)  
**Playbook:** [13-tfmcweb.md](../../13-tfmcweb.md)

## Goal

Stop SimpleFactions from opening raw `HttpURLConnection` to ProvinceSystem. All map HTTP (`upload`, `getProvince`, `commenceRegen`, `fetchBannerList`) goes through **TFMCWeb** `ProvinceSystemGateway`, matching ArmourShop / RPCharacters / DrinkBuilder.

This was previously deferred to “post map platform”; it is pulled into step 42 so settlement uploads and regen share the same plugin-key / base-url config as the rest of TFMC.

## Build

| File | Action |
|------|--------|
| `simplefactions/src/main/resources/plugin.yml` | `softdepend: [TFMCWeb]` (keep existing deps) |
| `simplefactions/.../api/GatewayClient.java` | **Add** — reflective bridge to `ProvinceSystemGateway` (copy pattern from ArmourShop) |
| `simplefactions/.../REST/RestServer.java` | **Refactor** — delegate HTTP to `GatewayClient`; remove hardcoded `apiURL` usage |
| `simplefactions/.../SimpleFactions.java` | Fail-soft log if TFMCWeb missing when `enable-map: true` |
| `simplefactions/Documentation/Settlements.md` | Note map transport is TFMCWeb-only |

### Path mapping (unchanged contract)

| RestServer today | Gateway path |
|------------------|--------------|
| `POST /{mapRef}/data/upload/{mode}` | `POST /{mapRef}/data/upload/{mode}` |
| `GET /{mapRef}/map/province/{x},{z}` | `GET /{mapRef}/map/province/{x},{z}` |
| `GET /{mapRef}/{hash}/api/regenerate/{type}` | `GET /{mapRef}/{hash}/api/regenerate/{type}` |
| `GET /generator/banner` | `GET /generator/banner` |

`ProvinceSystemGateway` injects `X-Plugin-Key` and reads `api.base-url` / `api.plugin-key` from **TFMCWeb** `config.yml`. SF **drops** duplicate API URL config (or ignores legacy keys with a one-time warning).

### Config cutover

| Before (SF) | After |
|-------------|--------|
| `RestServer.apiURL` / any SF API URL key | Removed or deprecated |
| — | TFMCWeb `api.base-url`, `api.plugin-key` (already on server) |

SF keeps gameplay config (`map-reference`, `enable-map`, settlement rules, etc.) in `plugins/SimpleFactions/config.yml`.

## Verify

**Dev server:**

- [ ] TFMCWeb + SimpleFactions loaded; `enable-map: true`
- [ ] `/faction` claim in mapped world still resolves province via gateway
- [ ] `fullRegen` / `updateMap` uploads `nation`, `guilds`, `province_data`, `map_markers` without SF-side HTTP errors
- [ ] Regen trigger returns 200 via gateway
- [ ] SF starts with clear error if TFMCWeb missing and map enabled

**Local (no MC):** unit/smoke optional — gateway client returns fail message when TFMCWeb absent.

## Out of scope

- Moving regen hash out of SF source (still embedded until a separate security batch)
- Realm_id injection on map routes (not on gateway allowlist today; map paths use `mapRef` segment)

## Status

**Done** (2026-08-15). `GatewayClient`, `RestServer` via TFMCWeb, `softdepend`, startup warning.

## Next

[08-sf-marker-size-export](./08-sf-marker-size-export.md)
