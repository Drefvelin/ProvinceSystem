# Batch 28.07 — Docs + staging verify

**Plan + build:** Close batch statuses + hubs; leave STAGING operator ticks for humans.

**Depends on:** 28.01–28.06 implemented

## Build

1. Mark 00–06 statuses **Implemented** / done where code landed.  
2. Sync any leftover gaps in 05 / 10 / 14 / batches README / roadmap / checklist.  
3. Add STAGING Step 28 operator checklist (unchecked).  
4. Rewrite [AgentHandoff](../../../../Documentation/Agent/AgentHandoff.md) → Step 28 closed; next = operator staging or Phase 4 if asked.

## Staging checklist (operator, unchecked until built)

- [ ] `/skins` Book kind: upload unsigned+signed → Discord review → apply  
- [ ] Equipped/usable book shows unsigned; after sign shows signed  
- [ ] Kit journal customise + claim works; sign swap on kit book  
- [ ] Staff curated book path (if enabled) smoke OK  
- [ ] `resetkit` on starter re-opens journal customise  

## Out of scope

Phase 4 wardrobe. Changing knife templates beyond Step 27. Replacing grant path with MI/IA book base (only if verify forces it).

## Status

**Code+docs closed.** Operator ticks remain in [STAGING.md](../../../STAGING.md) Step 28.
