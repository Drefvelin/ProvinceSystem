# Batch 20.03 — Docs + staging verify (Phase 2 kits)

**Plan + build:** Docs only + staging checklist for Step 20 kit grant.

**Depends on:** 20.01–20.02

## Docs hubs

| File | Change |
|------|--------|
| [14-character-creator.md](../../14-character-creator.md) | Phase 2 status → implemented |
| [03-roadmap.md](../../03-roadmap.md) | Track E2 code done |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | Step 20 done |
| [batches/README.md](../README.md) | step-20 row done |
| [STAGING.md](../../../STAGING.md) | Step 20 deploy + operator checklist |
| This step `00-index` | Status **20.01–20.03 done** |

## Staging checklist (humans tick)

- [ ] `kit.yml` loaded; CE `/tfmc starter` disabled (no double kit)
- [ ] New character (cooldown clear) receives kit on join once
- [ ] Reload with online eligible character grants kit
- [ ] Second character inside 48h is ineligible; no kit on join
- [ ] In-game create shows wait-X-hours warning while cooling down
- [ ] Website `/character` create shows the same warning
- [ ] After cooldown, new character is eligible again and receives kit

Also mirrored under [STAGING.md](../../../STAGING.md) Step 20.

## Implemented

- Hubs / roadmap / checklist / batches README marked Phase 2 code-done
- [STAGING.md](../../../STAGING.md) Step 20 deploy notes; CE cutover noted (`enabled: false` in repo `a_boosters.yml`)
- Step-20 `00-index` closed as **20.01–20.03 done**

## Out of scope

Phase 3 lore-item editor; claiming staging green without human ticks.
