# Step 47.04 — Title province rollup

**Repos:** `ProvinceSystem` frontend (+ optional backend compile)  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Goal

Resolve `provinces[]` for empire/kingdom/duchy/county (and trade guild) entries so the existing label layout (`connectedComponents` → inset → `LabelLayer`) can run on any political mode.

## Locked rules

Rollup contract locked in [01-planning-lock](./01-planning-lock.md) — **Option A: frontend** (`titleProvinces.ts` + `useTitleLayerData`). Compile denormalize deferred.

| Map mode | Rollup |
|----------|--------|
| `county` | `region.provinces` directly |
| `duchy` | Each duchy: union `county.provinces` for `titles[]` county ids |
| `kingdom` | kingdom → duchies → counties → provinces |
| `empire` | empire → kingdoms → duchies → counties → provinces |
| `trade` | guild: provinces where guild is trade-dominant (from compiled `trade.json` `provinces[]`) |

**Incomplete holders** on kingdom map (e.g. `Letzebierg` with county-level `titles[]`): resolve id against `county.json` when parent tier is kingdom.

## Build

| File | Action |
|------|--------|
| `frontend/app/lib/titleProvinces.ts` | **Add** — `resolveTitleProvinces(entityId, mapType, layers)` |
| `frontend/app/lib/titleProvinces.test.ts` | **Add** — fixtures mirroring `colour_mapping` chains |
| [`backend/src/scripts/compile/trade_compiler.py`](../../../backend/src/scripts/compile/trade_compiler.py) | **Extend** — write `provinces[]` per guild |
| [`frontend/app/hooks/useTitleLayerData.ts`](../../../frontend/app/hooks/useTitleLayerData.ts) | **Add** — fetch county + intermediate JSON for active mode |

## API

Reuse existing `GET /{map}/data/{file}` — no new routes.

## Verify

- [x] `resolveTitleProvinces("KINGDOM_1", "kingdom", layers)` matches union expected from defines spot-check
- [x] Empire rollup includes all descendant provinces (no duplicates)
- [x] Trade guild entry returns province list after compile
- [x] Vitest green

## Out of scope

- Backend denormalize `provinces[]` onto kingdom/duchy/empire JSON (Option B — deferred per 47.01)
- Nation rollup changes (40 full-realm already shipped)
- MapViewer label wiring (47.05)

## Status

**Done.**

## Next

[05-title-labels-frontend](./05-title-labels-frontend.md).
