# Batch 5.05 — E2E verify (link + DMs)

**Plan + build:** Smoke script and staging checklist for the full Step 5 path.

**Repos:** ProvinceSystem (+ Discord / staging as available)

**Depends on:** 5.01–5.04 (5.04 optional if using curl for link/start)

## Plan

1. Update [`skins_e2e_smoke.py`](../../../backend/scripts/skins_e2e_smoke.py):
   - Before upload: `link/start` + `link/complete` with a fake Discord id
   - Assert submission response / DB path includes `discord_user_id`
   - Assert a `submitted` notification exists (or GET notifications returns it); ack optional
2. Staging / AMP checklist (manual):
   - curl or ArmourShop `/linkdiscord` → Discord `/linkdiscord CODE`
   - Issue + redeem skins code → upload
   - Confirm **submitted** DM
   - Approve / Deny in `#bot-feed` → outcome DM
3. Mark Step 5 index final checkpoint done in planning if green.

## Build

| File | Action |
|------|--------|
| `backend/scripts/skins_e2e_smoke.py` | Link + notify assertions |
| Optional | Short note in `STAGING.md` if helpful |

## Verify

```text
smoke script ALL OK
+ manual: link → upload → submitted DM → approve/deny DM
```

- [x] Automated smoke green (`skins_e2e_smoke.py` — Step 5 assertions)
- [ ] Manual Discord DM path green (staging or local API + AMP bot) — see [STAGING.md](../../../STAGING.md)
- [x] Step 5 automated checkpoint satisfied; live DM checklist documented for operator

## Out of scope

New features; ban-role; IA apply.
