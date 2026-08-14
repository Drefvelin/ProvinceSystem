# Step 37.05 — Mobile layout

**Repos:** `ProvinceSystem` frontend  
**Depends on:** [04-click-interaction](./04-click-interaction.md)

## Goal

Usable map on phone: full-width canvas, toolbar mode selector, nation detail in modal/bottom sheet, no squeezed `w-[18%]` sidebar.

## Plan

1. **`MapPageLayout.tsx`** — `flex-col` below `md:` breakpoint; map first, toolbar second; hide fixed right sidebar on small screens.
2. **`MapToolbar.tsx`** — sticky or top bar on mobile; mode select full width; 44px min touch targets.
3. **`NationDetailModal.tsx`** — full-screen or bottom sheet on `max-md`; dismiss on backdrop tap; **Drill in** prominent.
4. Test tap-to-open modal (no Ctrl on mobile).
5. Optional: collapse drill breadcrumb into toolbar chip row.

## Build

| File | Action |
|------|--------|
| `frontend/app/components/map/MapPageLayout.tsx` | responsive layout |
| `frontend/app/components/map/MapSidePanel.tsx` | `MapMobileToolbar` + `MapDesktopSidePanel` |
| `frontend/app/components/map/NationDetailModal.tsx` | bottom sheet / full-screen variant |

## Verify

- [x] Phone width: map readable, no horizontal scroll from sidebars
- [x] Tap nation → modal opens with same fields as desktop
- [x] Drill in works from modal
- [x] Mode selector usable with touch
- [x] `npm run build` passes

## Out of scope

Pan/zoom gestures; parchment styling (38).
