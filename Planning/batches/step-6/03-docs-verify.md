# Batch 6.03 — Docs + verify (token create)

**Plan + build:** Planning/staging checklist for mint → website redeem → upload.

**Repos:** Planning docs + manual in-game path

**Depends on:** 6.01–6.02

## Plan

1. Confirm parent docs already name `/armourshop token create` (from Step 6 docs pass); add [`STAGING.md`](../../../STAGING.md) bullets if missing.
2. Operator checklist:
   - Discord linked for test UUID (Step 5)  
   - LP: `armourshop.token.create` (or admin)  
   - `/armourshop token create` → copy code  
   - Redeem + upload on staging UI  
   - `#bot-feed` / DMs as before  
3. Mark Step 6 index checkpoint / checklist boxes when green.

## Build

| File | Action |
|------|--------|
| `STAGING.md` | Token create steps if not already there |
| `batches/step-6/00-index.md` / this file | Verify checkboxes |

## Verify

```text
/armourshop token create → click copy → /skins redeem → upload OK
```

Tick after staging is green (operator; see [STAGING.md](../../../STAGING.md)):

- [ ] Tab complete works  
- [ ] Code redeems on website  
- [ ] Upload succeeds (Discord already linked)  

## Out of scope

New features beyond mint UX.
