# Step 17.02 — Identity API + 1h guild leave grace

**Plan + build:** ProvinceSystem owns durable Discord identity + grace; skins keep working via existing `/skins/discord` routes.

**Status:** Implemented (routes under `/skins/discord/…` until TFMCWeb cutover).

## Locked

| Piece | Choice |
|-------|--------|
| Leave | `grace_until = now + 1 hour` (`IDENTITY_GUILD_GRACE_MINUTES`, default 60); link row kept |
| Rejoin | Clear grace; stay linked |
| Expiry | Unlink + notice `grace_expired` (on status / notices list) |
| Alts | Reject complete if Discord id already on another UUID |
| Notices | `guild_left_grace`, `guild_rejoined`, `grace_expired` (+ `link_success`) |

## Routes

| Method | Path | Auth |
|--------|------|------|
| POST | `/skins/discord/guild/left` | `X-Staff-Key` |
| POST | `/skins/discord/guild/joined` | `X-Staff-Key` |
| GET | `/skins/discord/status/{player_uuid}` | `X-Plugin-Key` |

## Verify

```text
python -m src.skins.discord_link
```

(from `backend/` with `PYTHONPATH` set) — includes grace leave/join/expire + alt checks.

**Unblocks:** [03-bot-guild-events](./03-bot-guild-events.md), [04-tfmcweb-scaffold](./04-tfmcweb-scaffold.md).
