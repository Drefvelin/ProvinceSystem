# Step 40 — Staff map access control

**Repos:** `ProvinceSystem` · `Workspace/tfmcweb` (LP permission)  
**Depends on:** [step-37](../step-37/00-index.md)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 6

## Goal

Configurable public vs staff-only maps: regular players see `main` only; staff with map permission can access dev/other maps.

## Locked rules

| Piece | Choice |
|-------|--------|
| Permission | TFMCWeb/LP e.g. `tfmc.map.staff` |
| Config | PS map registry: `{ mapId, public, staff_permission? }`; SF `mapRef` must match |
| API | 403 on map assets/data routes for unauthorized `mapId` |
| Frontend | Hide non-public map links in nav; direct URL still gated by API |

## Batches (when step starts)

1. **01-planning-lock**  
2. **02-ps-map-registry** — Config + route guards  
3. **03-staff-session** — Auth check (TFMCWeb staff session or equivalent)  
4. **04-frontend-gate** — Nav + error states  
5. **05-docs-verify** — STAGING Step 40  

## Status

**Planned.**
