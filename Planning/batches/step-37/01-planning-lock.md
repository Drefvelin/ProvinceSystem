# Step 37.01 — Planning lock

**Plan + docs only.** Lock map site UX scope before implementation batches 02–06.

**Repos:** Planning  
**Depends on:** [00-index](./00-index.md) · [16-map-platform.md](../../16-map-platform.md) (requirements 1, 5, 7)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md)

## Locked — layout and chrome

| Decision | Choice |
|----------|--------|
| Site shell | Global [`SiteHeader`](../../../frontend/app/components/shell/SiteHeader.tsx) from [`layout.tsx`](../../../frontend/app/layout.tsx); **remove** map-local sticky header (Patreon/Discord/logo bar inside `MapViewer`) |
| Hero banner | **Remove** 350px `/background.png` hero from map page |
| Vote links | **Remove** from map sidebar in step 37; **defer** to a future dedicated vote page or hub link (not in this step) |
| Discord CTA | Rely on site header nav; no full sidebar Discord/vote panel |
| Typography / color | `--tfmc-*` tokens + Fraunces/Source Sans; retire hardcoded `#657c4c` / `#2b2218` panel palette |
| Page background | Dark forest gradient (`--tfmc-forest-deep`), not gray `#8f8b7e` gradient |

## Locked — component split (batch 02)

```text
frontend/app/components/map/
  MapPageLayout.tsx       — page shell below SiteHeader
  MapCanvas.tsx           — base img, canvas pick layer, overlays, hover images
  MapToolbar.tsx          — mode selector, drill breadcrumb, reset
  NationDetailModal.tsx   — click-open nation sheet
  types.ts                — RegionInfo, MapMode shared types
```

[`MapViewer.tsx`](../../../frontend/app/components/MapViewer.tsx) becomes a thin composer; [`map/main/page.tsx`](../../../frontend/app/map/main/page.tsx) import path unchanged.

## Locked — interaction

| Input | Behavior |
|-------|----------|
| Click / tap | Open `NationDetailModal`; **no** drill on plain click |
| Ctrl+click (Cmd on Mac) | Existing drill-down (`handleClick` logic) |
| Hover | Highlight overlay; tooltip shows **nation name** (not raw x/z as primary) |
| Modal | **Drill in** button when region has subjects (mobile-friendly) |

## Locked — data (batch 04)

[`useRegionHover.ts`](../../../frontend/app/hooks/useRegionHover.ts) must set `size`, `subject_size`, `overlord`, `subjects` from `regionData[id]` (nation JSON already has values).

## Locked — performance (batch 03)

Cropped region PNGs + bbox ([04-map-performance.md](../../04-map-performance.md)); rAF mousemove; RGB→id map; overlays without bbox default to full-map placement.

## Locked — mobile (batch 05)

Map full width on small screens; mode in toolbar; nation detail in bottom sheet/modal; min 44px tap targets.

## Out of scope (step 37)

- Parchment / Xaero ([step-38](../step-38/00-index.md))
- Curved labels ([step-40](../step-40/00-index.md))
- Staff map gating ([step-40](../step-40/00-index.md))
- Pan/zoom library
- New vote page (future site task)

## Hub edits

- [00-index](./00-index.md) — batch links + status
- [16-map-platform.md](../../16-map-platform.md) — vote deferral note
- [STAGING.md](../../../STAGING.md) — Step 37 checklist from [06-docs-verify](./06-docs-verify.md)
- [08-implementation-checklist.md](../../08-implementation-checklist.md) — 37.01 locked note

## Verify

- [x] Locked tables in this file
- [x] Batches [02](./02-split-map-viewer.md)–[06](./06-docs-verify.md) exist
- [x] Hub docs updated
- [x] No application code in 37.01

## Status

**Done** (37.01). Next: [02-split-map-viewer](./02-split-map-viewer.md).
