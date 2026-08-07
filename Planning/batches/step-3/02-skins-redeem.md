# Batch 3.02 — Skins redeem + session

**Plan + build:** Talk to ProvinceSystem skins API from the browser; redeem a code into a short-lived session.

## Plan

1. Env: `NEXT_PUBLIC_API_URL` (document in frontend `.env.example` if missing).
2. `lib/skins/api.ts`: `redeemCode(code)` → `POST {API}/skins/redeem`; typed errors from `detail`.
3. `lib/skins/session.ts`: store `session_token` (+ optional `player_uuid`, `expires_at`) in `sessionStorage`; clear helpers.
4. `/skins` page: redeem form (code input + submit). On success, show “ready to upload” state (upload UI in 3.03).
5. If session already present and not expired, skip straight to post-redeem UI placeholder.
6. Never call plugin/staff endpoints from the browser.

## Build

| File | Action |
|------|--------|
| `frontend/lib/skins/api.ts` | create |
| `frontend/lib/skins/session.ts` | create |
| `frontend/components/skins/RedeemForm.tsx` | create |
| `frontend/app/skins/page.tsx` | wire redeem |
| `frontend/.env.example` | `NEXT_PUBLIC_API_URL` |

## Verify

With API running (`SKINS_DEV=1`) and seed/issue a code:

- [ ] Bad code → clear error  
- [ ] Good code → session stored; UI advances past redeem  
- [ ] Refresh keeps session until expiry / clear  

## Out of scope

Multipart upload, slug validation UI, status polling.
