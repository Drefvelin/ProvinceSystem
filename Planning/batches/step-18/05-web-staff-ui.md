# Batch 18.05 — Website staff dropdowns

**Plan + build:** When session is staff, show category + scroll (per tier for armor) from catalog; send on submit. Minimal UI change.

**Repos:** `ProvinceSystem/frontend`

**Depends on:** [01-catalog-sync](./01-catalog-sync.md) · [02-staff-token-api](./02-staff-token-api.md)

## Plan

1. Detect staff session from redeem response (flag on session).
2. `GET` catalog; filter out `ps_armor` / `ps_items` from category dropdown.
3. Dropdowns: **category**; **scroll** (from catalog scrolls). For `armor_set`, scroll per tier (or one scroll applied to all tiers — pick one UX; prefer **per tier** to match curated YAML).
4. Filter categories by kind where helpful (`is-item` vs armor) using catalog metadata.
5. Submit payload includes category + scroll(s) only in staff mode.
6. Status page: staff skins show approved/applied without Discord review copy.
7. No Kind-help lectures beyond existing; no bot messaging.

## Build

| Area | Action |
|------|--------|
| session / redeem types | staff flag |
| UploadForm | dropdowns + payload |
| status copy | skip review wait for staff |

## Verify

- [x] Player session → no category/scroll fields  
- [x] Staff session → required dropdowns; submit succeeds  
- [x] Collision with existing set key → API error shown  

## Implemented

- Session persists `staff` / `scope` from redeem
- `getCatalog()` + `filterStaffCategories` (drop `ps_*`, filter by `is_item`)
- UploadForm staff category + scroll / per-tier `tier_scrolls`
- StatusCard staff copy without Discord review wait

## Out of scope

New kinds; redesign of upload form layout beyond dropdowns.
