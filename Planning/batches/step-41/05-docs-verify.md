# Step 41.05 — Docs verify + STAGING

**Repos:** Planning + `ProvinceSystem`  
**Depends on:** [02](./02-ps-map-registry.md)–[04](./04-frontend-gate.md)

## Goal

Close step 41 in hub docs and STAGING; operator checklist for public `main` vs gated `dev` on staging deploy.

## Docs updated

| File | Action |
|------|--------|
| [step-41/00-index.md](./00-index.md) | Status → **41.01–41.05 done** |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | M4 **done**; 41.05 checked; next → step 42 |
| [16-map-platform.md](../../16-map-platform.md) | Req 6 done; build order step 41 done |
| [01-current-state.md](../../01-current-state.md) | Staff maps shipped; known issue removed |
| [03-roadmap.md](../../03-roadmap.md) | Track H: step 41 done; next step 42 |
| [batches/README.md](../README.md) | step-41 row → **done** |
| [12-end-to-end-flows.md](../../12-end-to-end-flows.md) | Next build → step-42 |
| [13-tfmcweb.md](../../13-tfmcweb.md) | Next product work → step-42 |
| [STAGING.md](../../../STAGING.md) | Step 41 frontend nav/gate checks added |

## Automated tests

**Backend:**

```bash
cd ProvinceSystem/backend/src
python -m unittest api.test_map_access characters.test_rpc_player_meta -v
```

- [x] 26 tests pass (16 map access + 10 rpc_player_meta incl. `has_map_staff_access`)

**Frontend:**

```bash
cd ProvinceSystem/frontend
npm test
npm run build
```

- [x] 86 tests pass (7 files incl. `map/api`)
- [x] `npm run build` passes (`/map/main`, `/map/r3b1rth` routes built)

## STAGING operator checklist

See [STAGING.md](../../../STAGING.md) **Step 41**. Summary:

### Registry and LP

- [ ] `maps.yml` lists `main` (public) and `dev` (staff)
- [ ] LuckPerms grants `tfmc.map.staff` to staff groups
- [ ] TFMCWeb `player-meta.sync-permissions` includes `tfmc.map.staff` on lobby + survival

### Anonymous (no profile login)

- [ ] Nav shows **Map** only — no Adavaar link
- [ ] `/map/main` loads; nation hover/click work; pan/zoom/labels unchanged
- [ ] `GET /main/data/nation` returns 200
- [ ] `/map/r3b1rth` shows `MapAccessGate` login message (not broken partial map)
- [ ] `GET /dev/data/nation` returns 403
- [ ] `GET /maps/accessible` returns `main` only

### Staff (profile login + LP flag)

- [ ] Staff joins lobby/survival once; redeems profile code on website
- [ ] `GET /characters/player-meta` shows `permission_flags.tfmc.map.staff: true`
- [ ] Nav shows **Adavaar** link → `/map/r3b1rth`
- [ ] `/map/r3b1rth` loads (map images via Bearer blob URLs)
- [ ] `GET /dev/data/nation` returns 200
- [ ] `GET /maps/accessible` includes `dev` for staff session only

### Regression

- [ ] Player without flag never sees dev nav link; permission gate on `/map/r3b1rth`
- [ ] Logout on `/character` removes staff nav link (storage event; second tab to observe)
- [ ] SimpleFactions `mapRef` for each server matches registry `id`

## Verify

- [x] Batch docs 41.01–41.05 written
- [x] All implementation batches complete
- [x] Operator checklist in STAGING (human ticks on staging deploy)
- [x] Hub "next build" → step-42
- [x] Backend + frontend automated tests pass

## Status

**Done.**

## Next

[step-42 capitals](../step-42/00-index.md).
