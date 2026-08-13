# Step 31.02 — TFMCWeb shared mint cooldown + drink token

**Repos:** `Workspace/tfmcweb` · `ProvinceSystem` (remove mint cooldown only) · optionally stop using AS `skin-token-cooldown-days` for mint

## Goal

One mint clock for `skin` + `drink` on TFMCWeb. `/token create drink`. ProvinceSystem no longer enforces skin mint cooldown days.

## Plan

1. **TFMCWeb config** (new section), e.g.:

```yaml
token-cooldowns:
  shared-scopes: [skin, drink]
  defaults:
    cooldown-days: -1   # cannot mint
  groups:
    - permission: rpchar.group.noble
      cooldown-days: 28
    - permission: rpchar.group.gilded
      cooldown-days: 21
    - permission: rpchar.group.ascended
      cooldown-days: 14
    - permission: rpchar.group.legacy
      cooldown-days: 7
```

2. Last mint clock: ProvinceSystem `codes` (`skin`+`drink`) via `GET /skins/plugin/cosmetic-mint-status` (no local TW SQLite).
3. `TokenCommand`: add `drink` → API scope `drink`; before `POST /skins/codes`, check cooldown; insert updates the clock.
4. `skin_staff` / future `drink_staff`: skip cooldown.
5. `character`: not in shared-scopes.
6. **ProvinceSystem:** remove cooldown block from `issue_code` for `skin` (keep Discord eligible + insert). Keep AS colour/kinds entitlements untouched.
7. Docs: AS `skin-token-cooldown-days` deprecated for mint (may remove later or ignore).

## Verify

- [x] Non-ranked: cannot mint skin or drink (TW LP/`token-cooldowns` defaults `-1`).
- [x] Ascended: mint skin → drink fails until 14d; staff mint OK (TW checks shared status).
- [x] PS `/skins/codes` alone no longer applies days gate (TW is sole mint UX).
- [x] `/token create drink` issues `scope=drink` (redeem lands in 31.03).

## Done when

- [x] Shared cooldown live on TW
- [x] Drink scope mint works
- [x] PS mint cooldown retired
