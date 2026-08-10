# Batch 19.03 — Character redeem, Remember me, logout

**Plan + build:** Un-stub character redeem. Single-use code → Bearer session. Remember me lengthens TTL. Logout revokes.

**Repos:** `ProvinceSystem/backend` · `Workspace/tfmcweb` (mint already exists) · `frontend` (wire in 05)

**Depends on:** [step-17](../step-17/00-index.md) character scope mint; Discord link eligibility

## Locked TTLs

| Mode | Session TTL |
|------|-------------|
| Default (Remember me off) | **1 hour** |
| Remember me on | **30 days** |

Code remains **single-use**. Remember me only affects the **session** created at redeem.

## Plan

1. **`POST /skins/character/redeem`** — body `{ code, remember_me?: bool }`; validate scope `character`; consume code; create session row with TTL; return `session_token`, `player_uuid`, `expires_at`, `scope`, `remember_me`.
2. **Remove 501** stub; TFMCWeb mint message can say redeem is available once UI ships (update copy in 05/06).
3. **Auth dependency** — Bearer session required for character catalog GET (02) and create/list (04).
4. **`POST /characters/logout`** — delete current session row (idempotent).
5. **Skins sessions unchanged** — `POST /skins/redeem` still 1h only; character codes still rejected there.

## Verify

- [x] Redeem without remember_me → expires ~1h  
- [x] Redeem with remember_me → expires ~30d  
- [x] Second redeem of same code fails  
- [x] Logout → subsequent Bearer calls 401  
- [x] Skin-scope code rejected on character redeem  

## Implemented

- `redeem_character_code` / `revoke_session` in `src/skins/codes.py`
- `POST /skins/character/redeem` (un-501) with `CharacterRedeemBody`
- `POST /characters/logout`
- Smoke: `backend/scripts/character_session_smoke.py`; catalog smoke uses real redeem

## Out of scope

Full wizard UI; character CRUD; TFMCWeb mint copy (05/06).
