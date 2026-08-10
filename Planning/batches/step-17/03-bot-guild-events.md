# Step 17.03 — Bot guild leave / join → identity API

**Plan + build:** `tfmc_bot` SkinsReview notifies ProvinceSystem when a member leaves or rejoins the TFMC guild.

## Config

In `tfmc_bot/skinsreview/config.yml` (see `config.example.yml`):

```yaml
guild_id: 0   # TFMC Discord guild; required for leave/join grace
# or env GUILD_ID
```

If `guild_id` is `0` / unset, leave/join API calls are skipped and the cog logs a one-shot warning on load.

## Behaviour

| Event | API |
|-------|-----|
| `on_member_remove` | `POST /skins/discord/guild/left` body `{"discord_user_id": "<snowflake>"}` |
| `on_member_join` | `POST /skins/discord/guild/joined` same body |

- Cog: [`skinsreview/skinsreview.py`](../../../../tfmc_bot/skinsreview/skinsreview.py) (`X-Staff-Key` + `api_post`).
- Ignore bots and events from other guilds.
- Unlinked users: API `400` “No Minecraft link…” → debug log only (expected).
- **No** player DMs and **no** staff channel log in this batch.

## Verify (staging)

1. Set `guild_id` + staff key pointing at API with [02-identity-api](./02-identity-api.md) deployed.
2. Link a test Discord account to a MC UUID (`/linkdiscord`).
3. Leave TFMC guild → `GET /skins/discord/status/{uuid}` shows `in_grace: true`.
4. Rejoin within 1h → `in_grace: false`, still `linked`.
5. Unlinked Discord leave → bot logs debug only; API unchanged.

No Minecraft / TFMCWeb required for this batch.

## Done when

Leave starts 1h grace in DB; rejoin clears it.

**Depends on:** [02-identity-api](./02-identity-api.md).
