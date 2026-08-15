# Step 49.07 — Docs verify + STAGING

**Repos:** Planning + `ProvinceSystem` frontend  
**Depends on:** [02](./02-viewport-math.md)–[06](./06-edge-cases.md)

## Goal

Close step 49 in hub docs and STAGING; operator checklist for desktop pan/zoom on `/map/main` and `/map/dev`.

## Docs updated

| File | Action |
|------|--------|
| [step-49/00-index.md](./00-index.md) | Status → **49.01–49.07 done** |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | M3d **done**; 49.07 checked |
| [16-map-platform.md](../../16-map-platform.md) | Req 4d done |
| [01-current-state.md](../../01-current-state.md) | Pan/zoom shipped |
| [03-roadmap.md](../../03-roadmap.md) | Track H: steps 47–49 code done |
| [STAGING.md](../../../STAGING.md) | Step 49 operator checklist; Step 40 zoom-hide note |

## STAGING operator checklist

### Pan and zoom (`/map/main` + `/map/dev`)

- [ ] Scroll wheel zooms toward cursor; page does **not** scroll when cursor is over map
- [ ] Middle-mouse drag pans; cursor shows `grab` / `grabbing`
- [ ] Cannot pan to reveal empty margin outside map (test at zoom 1, 2, and max ~3×)
- [ ] Initial view at zoom 1 matches pre-pan/zoom fit-to-width

### Labels

- [ ] Nation/title/trade labels visible at default zoom; hidden after zooming in past ~1.5× user scale
- [ ] Label font size stays constant when zooming (no scale-with-zoom)

### Interaction regression

- [ ] Nation hover, click modal, and Ctrl+drill work at zoom 1 and after pan/zoom (spot-check corners + max zoom)
- [ ] Terrain / fertility / prosperity tooltips track cursor when zoomed/panned
- [ ] Switching map mode resets pan/zoom to fit view
- [ ] Navigating `/map/main` ↔ `/map/r3b1rth` resets pan/zoom

### Edge cases (49.06)

- [ ] Browser window resize reclamps without empty margins
- [ ] Middle-click does not open nation modal or trigger autoscroll
- [ ] Middle-drag cancels when cursor leaves map or window loses focus

## Automated tests

```bash
cd ProvinceSystem/frontend
npm test -- --run app/lib/mapViewportMath.test.ts app/hooks/useMapCoords.test.ts app/hooks/useMapViewport.test.ts
npm run build
```

## Verify

- [x] Batch docs 49.01–49.07 written
- [x] All implementation batches complete
- [x] Operator checklist copied to STAGING (human ticks on staging deploy)
- [x] Hub "next build" → step-41

## Status

**Done.**

## Next

[step-41 staff map access](../step-41/00-index.md) · [step-42 capitals](../step-42/00-index.md).
