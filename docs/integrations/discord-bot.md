# Discord bot (tfmc_bot)

**Canonical documentation for tfmc_bot lives in [`tfmc_bot/docs/`](../../tfmc_bot/docs/)**. This page is a pointer for ProvinceSystem readers.

## Role

[Red-DiscordBot](https://github.com/cog-creators/red-discordbot) cogs on AMP (CubeCoders):

| Cog area | Purpose |
|----------|---------|
| Skins review | Pending notify → `#bot-feed`, Approve/Deny → ProvinceSystem staff API |
| Drinks review | `drinksreview` cog - same pattern for `/drinks` submissions |
| Link | `/linkdiscord <code>` completes MC ↔ Discord bind |
| Moderation | Ban/warn DMs, **Banned** role add/clear, guild leave/join for 1h grace |
| Precedent | `/case-log` (staff) logs a case, `/precedent <info>` (staff+helper) searches precedent — see [precedent.md](./precedent.md) |

The bot does **not** execute in-game bans (Essentials owns MC bans).

## ProvinceSystem API surface (staff)

Bot calls ProvinceSystem with `X-Staff-Key`. Full route list:

- Skins: [cosmetics/skins.md](../cosmetics/skins.md) (staff pending, approve/deny, notifications, file download)
- Drinks: [cosmetics/drinks.md](../cosmetics/drinks.md) (staff pending, approve/deny)
- Identity: [identity/tfmcweb.md](../identity/tfmcweb.md) (link complete, guild events)
- Precedent: [precedent.md](./precedent.md) (log case, search precedent)

Player-facing mint and link **start** run in-game via TFMCWeb, not the bot.

## Configuration (summary)

| Env / config | Purpose |
|--------------|---------|
| `API_BASE_URL` | ProvinceSystem API (use local/staging URL for dev) |
| `STAFF_KEY` | Matches backend `STAFF_KEY` |
| `BOT_FEED_CHANNEL_ID` | `#bot-feed` for review embeds |

## Local development

Run bot against local API with test `STAFF_KEY`. Create pending submissions via `/skins` or curl. See [ops/local-dev.md](../ops/local-dev.md) and [tfmc_bot/docs/local-dev.md](../../../tfmc_bot/docs/local-dev.md).

For cog structure, deploy on AMP, and moderation details, see [tfmc_bot/docs/hosting.md](../../tfmc_bot/docs/hosting.md) and [tfmc_bot/docs/local-dev.md](../../tfmc_bot/docs/local-dev.md).
