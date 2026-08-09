# Step 5 — Discord link + player DMs (batch index)

**Repos:** ProvinceSystem (API) → `tfmc_bot` → `Workspace/armourshop`  
**Host:** Red on **AMP**; ArmourShop on MC server  

Parent: [../../05-skins-system.md](../../05-skins-system.md), [../../11-discord-bot.md](../../11-discord-bot.md), [../../10-armourshop-itemsadder.md](../../10-armourshop-itemsadder.md).

## Goal

Durable **Minecraft UUID ↔ Discord user id** link via `/linkdiscord` (in game + Discord). Skins uploads require a link; submissions store both ids. Players get DMs for **submitted**, **approved**, and **denied** (+ reason). No Discord OAuth; no typing ids on the website.

## Locked rules

| Rule | Detail |
|------|--------|
| In game | `/linkdiscord` → `POST …/link/start` (UUID implicit) |
| Discord | `/linkdiscord <code>` → `POST …/link/complete` (Discord id implicit) |
| Site | Item name + PNGs only; upload requires active link |
| Relink | Replace link for same UUID; reject if Discord id already used by another UUID |
| DMs | Bot owns all DMs (`X-Staff-Key`); status page remains source of truth |

## Scope

| In | Out |
|----|-----|
| Link tables + start/complete API | Discord OAuth |
| Require link on submit; stamp `discord_user_id` | Free-text Discord name on site |
| Submitted notification outbox + staff poll/ack | “Applied” DM |
| Cog `/linkdiscord` + submit/approve/deny DMs | Ban-role mute |
| ArmourShop `/linkdiscord` → link/start | Full IA apply (Track B3 / S4) |

## Batch order

1. [01-link-api](./01-link-api.md) — ProvinceSystem schema + start/complete  
2. [02-submit-and-notify](./02-submit-and-notify.md) — submit gate + submitted outbox  
3. [03-cog-link-and-dms](./03-cog-link-and-dms.md) — `/linkdiscord` + DMs  
4. [04-armourshop-linkdiscord](./04-armourshop-linkdiscord.md) — MC `/linkdiscord`  
5. [05-e2e-verify](./05-e2e-verify.md) — smoke + staging checklist  

**Process:** one batch = one plan + implement; stop after verify; start the next only when asked.

## Config

| Key | Who | Purpose |
|-----|-----|---------|
| `PLUGIN_KEY` / `X-Plugin-Key` | API + ArmourShop | `link/start`, skins codes |
| `STAFF_KEY` / `X-Staff-Key` | API + bot | `link/complete`, notifications, review |
| `API_BASE_URL` | Bot + ArmourShop | ProvinceSystem base |
| Existing skinsreview channel/roles | Bot | Unchanged for `#bot-feed` |

## Final checkpoint

```text
/linkdiscord in game (or curl start)
→ /linkdiscord CODE in Discord
→ redeem skins code + upload
→ player DM: submission received
→ staff Approve or Deny in #bot-feed
→ player DM: outcome (+ reason if denied)
→ API submission has player_uuid + discord_user_id
```

**Automated:** `python scripts/skins_e2e_smoke.py` from `backend/` — link, stamp `discord_user_id`, submitted notify + ack, review path.  

**Manual (operator):** live Discord DMs — [STAGING.md](../../../STAGING.md) Step 5 checklist.
