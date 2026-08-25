# Auth and security

ProvinceSystem authentication model, production guards, and staff access controls.

Sources: [`prod_guard.py`](../../backend/src/api/prod_guard.py), [`map_access.py`](../../backend/src/api/map_access.py), [`internal_access.py`](../../backend/src/api/internal_access.py), [STAGING.md](../../STAGING.md).

## Threat model (intentional)

Public map data is low sensitivity. Still validate uploads, hash codes, and keep plugin/staff secrets server-side. Docker isolation matters more than auth theater on map read endpoints.

Cosmetics and identity are higher sensitivity: UUID-bound codes, opaque Bearer sessions, and server-side staff keys.

## Opaque Bearer sessions

| Surface | Mechanism |
|---------|-----------|
| Player redeem (skins / drinks / character) | `POST …/redeem` with code → short-lived **opaque** session token stored in SQLite; client sends `Authorization: Bearer <token>` |
| Session scope | Encoded in DB row (`skin`, `drink`, `character`, `profile`, …) |
| TTL | Default **8h** after redeem; character Remember me **30d** |
| Profile / map staff | `profile` scope session from character redeem path; carries `player_uuid` and `realm_id` for permission checks |
| No website passwords | Codes are UUID-bound and not shareable by design |

Codes are **hashed at rest** (SHA-256). Plaintext shown once in-game at mint.

### Scope enforcement

Routes validate session **scope** before acting:

- Skin upload/submit requires a valid `skin` or `skin_staff` session tied to the issuer UUID.
- Drink submit requires `drink` scope.
- Character create requires `character` scope.
- Staff map viewer and title editor require `profile` scope plus permission flags.

Invalid or expired tokens return **401**. Wrong scope returns **403**.

## Staff map and site staff

[`map_access.py`](../../backend/src/api/map_access.py) centralizes map and staff checks.

### Staff-only maps

- Map entries in `maps.yml` declare `public: false` and optional per-map `staff_permission`.
- `ensure_map_access()` returns **403** without a valid profile Bearer session and matching permission from `rpc_player_meta` / LuckPerms sync.

### Map title editor write

- `ensure_map_staff_write()` requires `tfmc.map.staff` permission flag (constant `EDITOR_STAFF_PERMISSION`).
- Editor regen endpoints use Bearer staff session, not the plugin regen hash.

### Site staff helper

`require_site_staff(authorization)`:

1. Parses Bearer token.
2. Accepts any valid feature session (`skin`, `drink`, `profile`, …) via `get_feature_session()`.
3. Requires `has_map_staff_access(…, "tfmc.map.staff")`.
4. Returns **401** without token; **403** without permission.

Used by **`POST /skins/codes/inspect`** so only staff can decode redeem codes from the website UI.

### UI dev bypass (non-production only)

When `CHARACTER_UI_DEV=1` and token is `ui-dev-session`, staff map/editor checks bypass for local UI work. **Must be unset in production** (see production guard below).

## Plugin and staff API keys

| Key | Header | Used by |
|-----|--------|---------|
| `PLUGIN_KEY` | `X-Plugin-Key` | TFMCWeb gateway, ArmourShop, DrinkBuilder, link start, code mint, plugin pull |
| `STAFF_KEY` | `X-Staff-Key` | tfmc_bot approve/deny, notifications, staff file download |

Never expose these as `NEXT_PUBLIC_*` env vars.

## Localhost-only internal routes

[`internal_access.py`](../../backend/src/api/internal_access.py) defines `require_localhost(request)`:

- Allows only `127.0.0.1` and `::1`.
- Used for internal queue upload and regen callers on the same host as the API.

**Production rule:** TFMCWeb `api.base-url` on the game host must be loopback (e.g. `http://127.0.0.1:18001` on staging), not the public site hostname. SimpleFactions regen and queue upload inherit that URL through TFMCWeb's gateway.

## Production startup guard

[`prod_guard.py`](../../backend/src/api/prod_guard.py) runs at server startup when `PS_PRODUCTION=1`:

| Check | Failure if |
|-------|------------|
| `SKINS_DEV=1` | Dev skins helpers enabled |
| `CHARACTER_UI_DEV=1` | UI dev session bypass enabled |
| Missing `PLUGIN_KEY` | Plugin routes unauthenticated |
| Missing `STAFF_KEY` | Staff routes unauthenticated |

Startup raises `RuntimeError` and refuses to boot if any check fails.

### Frontend production build

`frontend/scripts/assert-prod-build-env.mjs` runs on `prebuild`: if `PS_PRODUCTION=1` and `NEXT_PUBLIC_CHARACTER_UI_DEV=1`, the build fails.

Pass `PS_PRODUCTION` as a Docker build arg for production frontend images.

## Staging vs production checklist

| Topic | Staging | Production |
|-------|---------|------------|
| `PS_PRODUCTION` | **Do not set** | Set `PS_PRODUCTION=1` |
| Dev flags | `SKINS_DEV=1` OK | `SKINS_DEV` and `CHARACTER_UI_DEV` must be unset |
| API keys | Compose dev defaults OK | Real `PLUGIN_KEY` / `STAFF_KEY` required |
| Internal queue/regen | Loopback `127.0.0.1:18001` | Same: never public hostname |
| Code inspect | Staff Bearer + `tfmc.map.staff` | Same |
| Frontend build | `NEXT_PUBLIC_CHARACTER_UI_DEV` unset for prod images | Pass `PS_PRODUCTION=1` build arg |

Full operator detail: [STAGING.md](../../STAGING.md), [ops/dev-config.md](../ops/dev-config.md).

## Free-text validation

Display names and prose fields share charset rules in `backend/src/text_validation.py` (frontend mirror: `frontend/lib/textValidation.ts`):

- Display names: Unicode letters, digits, limited punctuation; no emoji or colour codes.
- Prose: printable text; no controls or colour codes.
- Technical ids (slugs, codes): unchanged strict alphabets.

Invalid input is **rejected** at the API (400). React renders user strings as text only.

## Site dev gate (optional)

When `NEXT_PUBLIC_SITE_DEV_GATE=1`, the entire UI is replaced by a dev landing page until the visitor redeems a **character** code and has `tfmc.map.staff`.

**Security:** Client-side gate only; API routes remain reachable if endpoints are known. Unset on public launch.

## See also

- [identity/tfmcweb.md](./tfmcweb.md) - Discord link and tokens
- [cosmetics/skins.md](../cosmetics/skins.md) - skins HTTP contracts and staff routes
- [map/overview.md](../map/overview.md) - staff map gates
