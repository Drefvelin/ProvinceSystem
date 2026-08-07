# Step 4 — Discord skins review (batch index)

**Repos:** `tfmc_bot/` (Red cogs) + small ProvinceSystem staff API  
**Host:** Red on **AMP (CubeCoders)**  
**Framework:** [Red-DiscordBot](https://github.com/cog-creators/red-discordbot) V3  

Parent: [../../11-discord-bot.md](../../11-discord-bot.md), [../../05-skins-system.md](../../05-skins-system.md).

## Goal

Staff review pending skins in Discord **`#bot-feed`**: embed + **raw PNG attachments**, Approve / Deny → ProvinceSystem staff API. No live website deploy required — point the cog at local/staging API.

## Scope

| In | Out |
|----|-----|
| `GET /skins/staff/pending` + staff file download | Review-sheet / render bake in Discord |
| Skins review cog in `tfmc_bot/` | ArmourShop / IA write |
| `#bot-feed` posts + buttons | Ban-role mute |
| Poll pending (no duplicate spam) | Webhook server (optional later) |
| AMP deploy notes | Changing public website |

## Batch order

1. [01-staff-pending-api](./01-staff-pending-api.md) — ProvinceSystem  
2. [02-cog-scaffold](./02-cog-scaffold.md) — Red cog loads  
3. [03-post-raw-files](./03-post-raw-files.md) — `#bot-feed` + attachments  
4. [04-approve-deny](./04-approve-deny.md) — buttons / modal  
5. [05-auto-intake-verify](./05-auto-intake-verify.md) — poll + verify  

## Config (AMP / Red env)

| Key | Purpose |
|-----|---------|
| `API_BASE_URL` | ProvinceSystem base (e.g. tunnel/staging/local reachable from AMP) |
| `STAFF_KEY` | `X-Staff-Key` |
| `BOT_FEED_CHANNEL_ID` | `#bot-feed` |
| `STAFF_ROLE_ID` / `HELPER_ROLE_ID` | Same pattern as minecraftban |

## Final checkpoint

```text
pending submission on local/staging API
→ appears in #bot-feed with raw PNGs
→ Approve or Deny(+reason)
→ API status matches; message updated; buttons disabled
```
