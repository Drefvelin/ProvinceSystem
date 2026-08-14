# Step 37 — Map site UX and interaction

**Repos:** `ProvinceSystem` frontend (+ backend crop overlays)  
**Depends on:** [step-36](../step-36/00-index.md) · site shell [step-3](../step-3/00-index.md)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirements 1, 5, 7

## Goal

Refined map layout matching the TFMC hub; fast interaction (cropped overlays, rAF hover); click-to-open nation modal; Ctrl+click drill; mobile-friendly panels.

## Locked rules

See [01-planning-lock](./01-planning-lock.md). Summary:

| Piece | Choice |
|-------|--------|
| Layout | Split `MapViewer` into `components/map/*`; remove header/hero/vote panel |
| Interaction | Click → modal; Ctrl/Cmd+click → drill; modal **Drill in** on mobile |
| Perf | Cropped region PNGs + bbox; rAF throttle; RGB→id map |
| Data | Wire `size`, `subject_size`, `subjects`, `overlord` into modal/hover |
| Styling | `--tfmc-*` tokens; match `SiteHeader` |
| Vote links | Removed from map; future dedicated vote page (not step 37) |

## Batches

1. **[01-planning-lock](./01-planning-lock.md)** — Scope lock **done**
2. **[02-split-map-viewer](./02-split-map-viewer.md)** — Component extraction + styling shell **done**
3. **[03-cropped-overlays](./03-cropped-overlays.md)** — `regiongen.py` bbox + frontend placement **done**
4. **[04-click-interaction](./04-click-interaction.md)** — Modal + Ctrl drill + hover data fix **done**
5. **[05-mobile-layout](./05-mobile-layout.md)** — Responsive layout + bottom sheet **done**
6. **[06-docs-verify](./06-docs-verify.md)** — STAGING Step 37 checklist **done**

## Checkpoint

```text
/map/main loads fast with cropped overlays
click nation → modal with size/subjects/relations
Ctrl+click drills subjects
usable on phone
visual match to hub
```

## Status

**Step 37 done (37.01–37.06).** Next build: [step-38](../step-38/00-index.md). Operator smoke: [STAGING.md](../../../STAGING.md) Step 37.
