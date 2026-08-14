# Step 38.05 — Docs verify



**Repos:** Planning + operator smoke  

**Depends on:** [02](./02-parchment-base.md)–[04](./04-frontend-composite.md) complete



## Goal



Close step 38 in hubs; STAGING checklist for humans.



## Plan



1. Tick [00-index](./00-index.md) status: **38.01–38.05 done**.

2. Update [08-implementation-checklist.md](../../08-implementation-checklist.md) M2 bullets.

3. Update [03-roadmap.md](../../03-roadmap.md) Track H step 38 done (when all batches shipped).

4. Update [16-map-platform.md](../../16-map-platform.md) / [01-current-state.md](../../01-current-state.md) / [12-end-to-end-flows.md](../../12-end-to-end-flows.md) / [13-tfmcweb.md](../../13-tfmcweb.md) next-build → step 39.

5. Replace STAGING Step 38 placeholder with operator checklist below.



## Verify



- [x] [00-index](./00-index.md) status: 38.01–38.05 done

- [x] [08-implementation-checklist.md](../../08-implementation-checklist.md) M2 complete

- [x] [03-roadmap.md](../../03-roadmap.md) Track H step 38 marked done (code)

- [x] [STAGING.md](../../../STAGING.md) Step 38 checklist added

- [x] Hub cross-links updated (`batches/README`, `16-map-platform`)



STAGING operator checklist items remain **unchecked** until verified on staging.



## Operator checklist (STAGING Step 38)



- [ ] `input/{map}/map.png` (Xaero plain background) present and aligned to `provinces.png`

- [ ] `fullregen` produces `output/{map}/maps/parchment_base.png`

- [ ] `/map/main` visual base is parchment (warm, desaturated terrain — not raw satellite)

- [ ] Nation hover overlays use muted colours (not neon RGB)

- [ ] Borders visible and readable on desktop and phone

- [ ] Click nation → modal still correct

- [ ] Ctrl+click drill still correct; pick at vassal edges unchanged

- [ ] `/map/dev` with province modes still usable if `dev` has Xaero asset

- [ ] Fallback: map without parchment output still loads (raw `map.png` via `/map`)



## Checkpoint



```text

Parchment base + muted nations on /map/main

Pick layer unchanged — interaction regression-free

STAGING Step 38 checklist green

```



## Status



**Done** (38.05). Step 38 closed in hubs; operator STAGING Step 38 smoke pending.



## Out of scope



[step-40](../step-40/00-index.md) curved labels.

