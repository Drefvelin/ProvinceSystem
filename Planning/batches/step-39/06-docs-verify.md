# Step 39.06 — Docs verify

**Repos:** Planning + STAGING  
**Depends on:** [02-ink-base](./02-ink-base.md) · [03-earth-tone-fills](./03-earth-tone-fills.md) · [04-adaptive-borders](./04-adaptive-borders.md) · [05-frontend-opacity](./05-frontend-opacity.md)

## Goal

Close Step 39 in hubs; add STAGING operator checklist; point next build to Step 40 (labels).

## Plan

1. Mark batches 01–06 done in [00-index](./00-index.md) when code ships.
2. Update [08-implementation-checklist.md](../../08-implementation-checklist.md) — new **M2b** or extend M2 with Step 39 items; M3 labels → step-40.
3. Update [03-roadmap.md](../../03-roadmap.md) Track H — step 39 ink done; next step 40.
4. Update [16-map-platform.md](../../16-map-platform.md) — req 2/3 note ink pass; build order insert 39.
5. Update [01-current-state.md](../../01-current-state.md) — visual issue wording; next build step-40.
6. Update [12-end-to-end-flows.md](../../12-end-to-end-flows.md) · [13-tfmcweb.md](../../13-tfmcweb.md) · [batches/README.md](../README.md).
7. Add **STAGING Step 39** operator checklist (human verify on staging).
8. Update [step-38/00-index.md](../step-38/00-index.md) footer — note 39 refines visual; 38 remains shipped baseline.

## STAGING operator checklist (draft)

- [ ] `fullregen` produces ink-style `parchment_base.png` (served at `/map/parchment`)
- [ ] `/map/main` default base: colour satellite (`map.png`), not parchment
- [ ] `/map/main/map/parchment` (or API `GET /main/map/parchment`): cream paper + brown coastlines when regen run
- [ ] Nation hover: faithful-hue parchment wash, not neon
- [ ] Uniform dark ink borders on all realms (Drakhanate + Nimbus spot-check; no white/black clash at shared edges)
- [ ] Drill stack opacity ≥ hover opacity
- [ ] Hover cropped overlay ~1% expand (no harsh crop edge)
- [ ] Click modal + Ctrl+drill pick unchanged; tooltip shows visible overlay nation
- [ ] No map base toggle in toolbar
- [ ] `/map/dev` still works

## Verify

- [x] All hub “next build” links → step-40
- [x] Step 39 index status → done (code complete)
- [x] No stale “step-39 labels” references remain

## Status

**Done.**

## Next

[step-40 curved labels](../step-40/00-index.md).
