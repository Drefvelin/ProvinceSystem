# Batch 29.04 — Claim ArmourShop gate (RPC)

**Plan + build:** On kit claim, pull website customises and refuse grant if required skins are not on ArmourShop yet.

**Repos:** `Workspace/rpcharacters` (soft-dep ArmourShop / IA as today)  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Locked

| Piece | Choice |
|-------|--------|
| When | Inside `KitService.tryClaim` after eligibility / cooldown, before granting stacks |
| Pull | Existing claim-status + `ingestReadyForCharacterOnMain` (keep) |
| Approval block | If PS says awaiting staff approval → WARN and return |
| AS block | If any customise skin slug missing on IA → *Kit is not ready yet, awaiting skins.* |
| Name/lore only | No AS check for that line |
| Success | Grant with customise merge as today |

## Done

1. `KitCustomiseApplyService.isSkinPresent` / `requiredSkinsReady` via `CustomStack.getInstance`  
2. `tryClaim` gate after ingest, before build stacks  

## Verify

- [ ] Pending approval → blocked with approval wording  
- [ ] Approved, not in pack → “awaiting skins”  
- [ ] Applied / on AS → claim succeeds with custom item  
- [ ] Journal-only customise still claimable when that skin is ready  

## Status

**Implemented** (29.04). Next: [05-status-copy](./05-status-copy.md).
