# Step 37.06 — Docs verify

**Repos:** Planning + operator smoke  
**Depends on:** [02](./02-split-map-viewer.md)–[05](./05-mobile-layout.md) complete

## Goal

Close step 37 in hubs; STAGING checklist for humans.

## Plan

1. Tick [00-index](./00-index.md) status: **37.01–37.06 done**.
2. Update [08-implementation-checklist.md](../../08-implementation-checklist.md) M1 bullets.
3. Update [03-roadmap.md](../../03-roadmap.md) Track H step 37 done (if all batches shipped).
4. Copy operator checklist below into [STAGING.md](../../../STAGING.md) Step 37 (checked when verified on staging).

## Verify

- [x] [00-index](./00-index.md) status: 37.01–37.06 done
- [x] [08-implementation-checklist.md](../../08-implementation-checklist.md) M1 complete
- [x] [03-roadmap.md](../../03-roadmap.md) Track H step 37 marked done (code)
- [x] [STAGING.md](../../../STAGING.md) Step 37 enhanced (operator boxes left open for human verify)
- [x] Hub cross-links updated (`batches/README`, `16-map-platform`, `01-current-state`, `12-end-to-end-flows`, `13-tfmcweb`)

STAGING operator checklist items remain **unchecked** until verified on staging.

## Operator checklist (STAGING Step 37)

- [ ] `/map/main` uses site `SiteHeader` only (no duplicate map header or hero banner)
- [ ] No vote-links panel on map page
- [ ] Page styling matches hub (`--tfmc-*` forest theme)
- [ ] Click nation → modal with banner, tier, realm size, subjects, description
- [ ] Ctrl+click (Cmd on Mac) drills into subjects
- [ ] Hover tooltip shows nation name
- [ ] Cropped overlays align after backend regen
- [ ] Mobile: tap opens modal; mode selector usable; no broken sidebar squeeze
- [ ] `/map/dev` still works (URL-only)

## Checkpoint

```text
/map/main — refined layout, modal, drill, perf, mobile
STAGING Step 37 checklist green
```

## Out of scope

Steps 38–40.
