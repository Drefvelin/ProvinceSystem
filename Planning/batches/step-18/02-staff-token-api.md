# Batch 18.02 — Staff token + auto-approve API

**Plan + build:** Staff skins codes and submissions: flag on mint, require category/scroll on upload, auto-approve (skip Discord pending), include in plugin pull payload with staff landing fields.

**Repos:** `ProvinceSystem/backend`

**Depends on:** [01-catalog-sync](./01-catalog-sync.md) (validate category/scroll against catalog when present)

## Plan

1. **Codes** — extend mint (`POST /skins/codes` or equivalent) with staff mode, e.g. `staff: true` or scope `skin_staff`. Only plugin key + staff mint path may set it. Player mint unchanged.
2. **Redeem** — session carries staff flag (or code metadata) so upload UI/API know mode.
3. **Submit** — staff submissions accept:
   - `category` (ArmourShop category id)
   - `scroll` (item / single) and/or per-tier scrolls for `armor_set`
   - Validate against latest catalog when available (unknown category/scroll → 400)
   - Reject if skin-set key would collide with existing key in that category (unless explicit overwrite later — default **reject**)
4. **Auto-approve** — staff submit → status `approved` immediately; **do not** enqueue skinsreview notifications / pending for bot.
5. **Plugin approved payload** — include `staff: true`, `category`, `scroll`(s), `ia_namespace: tfmc_armorshop` (or let AS infer from staff flag). Player payload unchanged (`tfmc_submissions`, `ps_*`).
6. Player submissions must reject category/scroll fields if present.

## Build

| Area | Action |
|------|--------|
| codes / redeem / submit | staff flag + fields |
| review outbox | skip for staff |
| plugin approved DTO | staff landing fields |

## Verify

- [x] Player code → submit → still `pending` + bot path  
- [x] Staff code → submit → `approved` immediately, no review notify  
- [x] Missing/invalid category or scroll → 400  
- [x] Plugin approved list includes staff rows with category/scroll  

## Implemented

- Scope `skin_staff` on codes; redeem/session return `scope` + `staff`
- Submissions columns: `staff`, `category`, `scroll`, `tier_scrolls`
- Staff submit validates catalog (empty → “catalog not synced”); auto-approves; skips `enqueue_submitted`
- `GET /skins/plugin/approved` staff landing fields + `ia_namespace: tfmc_armorshop`
- Smoke: `backend/scripts/skins_e2e_smoke.py` (18.02 section)

## Out of scope

TFMCWeb command (03); pack write (04); UI dropdowns (05).
