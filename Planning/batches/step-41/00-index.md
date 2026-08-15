# Step 41 — Staff map access control

**Repos:** `ProvinceSystem` · `Workspace/tfmcweb` (LP permission)  
**Depends on:** [step-37](../step-37/00-index.md) · [step-32](../step-32/00-rpc-player-meta.md)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 6

## Goal

Configurable public vs staff-only maps: regular players see `main` only; staff with map permission can access `dev` and future staff maps. API enforces 403; frontend hides nav links and shows clear errors.

## Problem statement

**Resolved** in batches 41.02–41.04 (registry + API guards + frontend gate). Historical context:

| Issue | Root cause (was) |
|-------|------------------|
| Staff map is public | `/map/r3b1rth` and `GET /dev/...` worked without login |
| Nav-only hiding | `SiteHeader` linked `/map/main` only; API still open |
| No map registry | `validate_map()` was alphanumeric only |

## Locked rules (summary)

See [01-planning-lock](./01-planning-lock.md). Highlights:

| Piece | Choice |
|-------|--------|
| Registry | `maps.yml`: `{ id, public, display_name, realm_id?, staff_permission? }` |
| Public map | `main` — anonymous GET |
| Staff map | `dev` — profile Bearer + `permission_flags["tfmc.map.staff"]` |
| Profile session | Character Bearer redeem = website identity (profile rebrand deferred) |
| API | 403 staff maps without permission; 404 unknown map id |
| Listing | `GET /maps/accessible` for nav |

## Batches

1. **[01-planning-lock](./01-planning-lock.md)** — Registry, auth, routes, FE preview, tests
2. **[02-ps-map-registry](./02-ps-map-registry.md)** — Config + `require_map_access` on GET routes
3. **[03-staff-session](./03-staff-session.md)** — `rpc_player_meta` permission check; TFMCWeb sync doc
4. **[04-frontend-gate](./04-frontend-gate.md)** — Nav, Bearer on fetches, error states
5. **[05-docs-verify](./05-docs-verify.md)** — STAGING + hub close-out

## Status

**41.01–41.05 done.**

## Next

[step-42 capitals](../step-42/00-index.md).
