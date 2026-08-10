# Batch 19.06 — Docs + staging verify (Phase 1)

**Plan + build:** Docs only + staging checklist for Step 19 Phase 1.

**Depends on:** 19.01–19.05

## Docs hubs

| File | Change |
|------|--------|
| [14-character-creator.md](../../14-character-creator.md) | Status → Phase 1 implemented |
| [13-tfmcweb.md](../../13-tfmcweb.md) | Character redeem live; session TTLs locked |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | Step 19 pointer done |
| [batches/README.md](../README.md) | step-19 row done |
| [STAGING.md](../../../STAGING.md) | Step 19 deploy + operator checklist |
| This step `00-index` | Status **19.01–19.06 done** |

## Staging checklist (humans tick)

- [ ] `/token create character` → redeem on `/character` (1h default)  
- [ ] Remember me → still logged in after browser restart (within 30d)  
- [ ] Log out → must mint a new token  
- [ ] In-game attribute sheet: exactly 12 points, max +2/stat, costs 1 then 2  
- [ ] Catalog sync after RPC reload updates web options  
- [ ] Web create → character exists in RPCharacters + listed on site  
- [ ] Dead characters visible on site  
- [ ] Slot limit enforced  
- [ ] No knife / player-skin UI required  

Also mirrored under [STAGING.md](../../../STAGING.md) Step 19.

## Implemented

- Hubs / roadmap / checklist / batches README marked Phase 1 done
- [STAGING.md](../../../STAGING.md) Step 19 deploy notes + operator checklist; Step 17 mint note no longer says 501
- TFMCWeb `/token create character` mint copy points at `/character`
- Step-19 `00-index` closed as **19.01–19.06 done**
- API smokes noted: `character_session_smoke.py`, `creation_catalog_smoke.py`, `character_ingest_smoke.py`

## Out of scope

Phases 2–4 implementation; claiming staging green without human ticks.
