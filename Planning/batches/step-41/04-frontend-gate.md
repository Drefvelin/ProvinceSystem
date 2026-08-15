# Step 41.04 — Frontend nav + error states

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [03-staff-session](./03-staff-session.md)

## Goal

Consume `GET /maps/accessible`; show staff map nav link only when permitted; attach Bearer to map fetches; friendly 403 UI on staff map pages.

## Build

| File | Action |
|------|--------|
| [`frontend/lib/map/api.ts`](../../../frontend/lib/map/api.ts) | Map API client: Bearer fetch, blob URLs, accessible maps, access error helpers |
| [`frontend/app/lib/map/api.test.ts`](../../../frontend/app/lib/map/api.test.ts) | Unit tests for map API client |
| [`frontend/vitest.config.ts`](../../../frontend/vitest.config.ts) | `@/` path alias for vitest |
| [`frontend/app/hooks/useAccessibleMaps.ts`](../../../frontend/app/hooks/useAccessibleMaps.ts) | Fetch `/maps/accessible` with character session |
| [`frontend/app/components/shell/SiteHeader.tsx`](../../../frontend/app/components/shell/SiteHeader.tsx) | Client nav; staff map link when `dev` in accessible list |
| [`frontend/app/components/map/MapAccessGate.tsx`](../../../frontend/app/components/map/MapAccessGate.tsx) | Login vs permission gate UI |
| [`frontend/app/hooks/useMapAssetUrl.ts`](../../../frontend/app/hooks/useMapAssetUrl.ts) | Authenticated blob URLs for staff map images |
| [`frontend/app/components/map/MapAuthImage.tsx`](../../../frontend/app/components/map/MapAuthImage.tsx) | Image wrapper using `useMapAssetUrl` |
| [`frontend/app/components/MapViewer.tsx`](../../../frontend/app/components/MapViewer.tsx) | Dev-map access probe; session token wiring |
| [`frontend/app/hooks/useMapModeData.ts`](../../../frontend/app/hooks/useMapModeData.ts) | Bearer on data fetch; `accessError` |
| [`frontend/app/hooks/useMapGeometry.ts`](../../../frontend/app/hooks/useMapGeometry.ts) | Bearer on geometry fetch |
| [`frontend/app/hooks/useTitleLayerData.ts`](../../../frontend/app/hooks/useTitleLayerData.ts) | Bearer on title tier fetch |
| [`frontend/app/hooks/useGuildCache.ts`](../../../frontend/app/hooks/useGuildCache.ts) | Bearer on trade guild fetch |
| [`frontend/app/hooks/useProvinceHover.ts`](../../../frontend/app/hooks/useProvinceHover.ts) | Bearer on province meta / compiled data |
| [`frontend/app/components/map/MapCanvas.tsx`](../../../frontend/app/components/map/MapCanvas.tsx) | Auth images for base map, overlays, regions |
| [`frontend/app/components/map/NationDetailContent.tsx`](../../../frontend/app/components/map/NationDetailContent.tsx) | Auth banner images |

### Behaviour

| Case | UI |
|------|-----|
| Anonymous `/map/main` | Works unchanged (no Bearer) |
| Anonymous `/map/r3b1rth` | `MapAccessGate` — profile login required |
| Profile session, no staff flag | Permission gate; no staff nav link |
| Staff session + flag | Adavaar nav link; dev map loads with Bearer on all API + blob image URLs |

Staff map URL remains `/map/r3b1rth` (codename); registry `id` is `dev`.

## Verify

```bash
cd frontend
npm test
npm run build
```

- [x] `npm test` passes (86 tests incl. map API)
- [x] `npm run build` passes
- [ ] Anonymous `/map/main` works; nav shows Map only
- [ ] Anonymous `/map/r3b1rth` shows login gate
- [ ] Staff session: Adavaar nav link + dev map loads

## Out of scope

- STAGING sign-off ([05-docs-verify](./05-docs-verify.md))
- Rename `/map/r3b1rth` → `/map/dev`

## Status

**Done.**

## Next

[05-docs-verify](./05-docs-verify.md).
