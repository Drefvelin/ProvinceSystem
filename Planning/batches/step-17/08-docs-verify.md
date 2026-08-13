# Step 17.08 — Docs + staging verify

**Depends on:** 17.01–17.07 implemented.  
**Playbook:** [13-tfmcweb.md](../../13-tfmcweb.md).  
**Ops:** [STAGING.md](../../../STAGING.md) § Step 17.

No new feature code in this batch. Tick boxes on the live staging server.

## Out of scope

- Character creator website / RPCharacters creation rewrite  
- Folding SimpleFactions HTTP into TFMCWeb  
- Replacing Essentials ban execution  

## Deploy prerequisites

- [ ] **RPCharacters** jar with `setDiscordGate` / `DISCORD_REQUIRED` (17.01)
- [ ] **ProvinceSystem** API with identity grace + moderation routes (17.02, 17.07)
- [ ] **TFMCWeb** jar: `plugins/TFMCWeb/config.yml` → `api.base-url` / `api.plugin-key` (same plugin key as staging)
- [ ] **ArmourShop** cutover jar: pack apply only; no link/notice/player mint (17.06)
- [ ] **tfmc_bot** skinsreview: `guild_id` / leave-join; minecraftban `config.yml`: `api_base_url`, `staff_key`, `banned_role_id` (non-zero for role check)
- [ ] LuckPerms: grant `tfmcweb.token.create` (and `tfmcweb.warning` for staff) where `armourshop.token.create` used to be

## Staging pass checklist

### Gate + identity

- [ ] Survival unlinked player → frozen (`DISCORD_REQUIRED`); message points to `/linkdiscord`; characters untouched
- [ ] Creative / staff non-Survival → not Discord-gated
- [ ] `/linkdiscord` (TFMCWeb) → Discord `/linkdiscord <code>` → Survival unfrozen
- [ ] Leave TFMC Discord → still playable ≤1h (`in_grace`); rejoin within 1h clears grace
- [ ] After grace expires while still out → unlinked + Survival frozen
- [ ] No alts: second MC UUID cannot complete link to the same Discord account

### Tokens + pack

- [ ] `/token create skin` (TFMCWeb, perm `tfmcweb.token.create`) → redeem on `http://127.0.0.1:13001/skins` → upload works
- [ ] Non-ranked / entitlement defaults → mint denied
- [ ] Ranked KindPicker filtered; armor 3D helmet hidden unless Ascended+
- [ ] Cooldown blocks a second mint within the rank window
- [ ] Optional smoke: `/token create character` issues a code
- [ ] `/armourshop token create` redirects to `/token create skin`
- [ ] ArmourShop pack pull / apply still works with `skins-api` (AS does not own link)

### Warn / ban mirror

- [ ] Linked `/warning <player> <reason>` → in-game chat (if online) + Discord DM + staff log; row in `player_warnings`
- [ ] Unlinked warn → stored; console skip; no DM
- [ ] `/tempban` **or** CE `/tfmc ban` → Discord DM + Banned role + staff log
- [ ] `/unban` → Banned role cleared + staff log (no player DM)
- [ ] Manual `/minecraftwarn` / `/minecraftban` still work as fallback

### Docs hubs

- [ ] [13](../../13-tfmcweb.md), [11](../../11-discord-bot.md), [10](../../10-armourshop-itemsadder.md), [STAGING.md](../../../STAGING.md) describe TFMCWeb ownership (not AS link/mint)

## Done when

Staging checkpoint green on the live server; character creator UI still explicitly out of scope.
