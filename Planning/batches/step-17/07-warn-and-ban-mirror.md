# Step 17.07 — `/warning` + Essentials ban mirror

**Plan + build:** In-game warnings and automatic Discord side-effects for Essentials bans.

## API

| Route | Auth | Purpose |
|-------|------|---------|
| `POST /skins/moderation/warnings` | plugin | Store `player_warnings` + enqueue `warn` if Discord linked |
| `POST /skins/moderation/ban-events` | plugin | Enqueue `ban` / `unban` if Discord linked |
| `GET /skins/moderation/notifications` | staff | Undelivered outbox |
| `POST /skins/moderation/notifications/ack` | staff | `{ids:[…]}` |

Self-test: `cd backend && PYTHONPATH=. python -m src.skins.moderation`

## TFMCWeb

| Piece | Detail |
|-------|--------|
| `/warning <player> <reason>` | Perm `tfmcweb.warning` (default false); chat if online; store + mirror |
| Essentials | Soft-depend; `BanStatusChangeEvent` reflection listener |
| Unlinked | Plugin log skip; no outbox row (`mirrored: false`) |

## Bot (`minecraftban`)

Env: `API_BASE_URL`, `STAFF_KEY`, `LOG_CHANNEL_ID`, `BANNED_ROLE_ID` (0 disables role), staff/helper roles.

Polls moderation outbox every ~3s:

| Type | Discord |
|------|---------|
| `warn` | DM + staff log |
| `ban` | DM + staff log + add Banned role |
| `unban` | staff log + remove Banned role (no DM) |

Slash `/minecraftban` / `/minecraftwarn` remain as manual fallback; `/minecraftban` also adds Banned role when configured.

## Verify

1. Linked: `/warning` → chat + Discord DM + staff log; row in `player_warnings`.
2. Unlinked: warn stores; console skip; no DM.
3. `/tempban` (or CE `/tfmc ban`): Discord DM + Banned role + staff log.
4. `/unban`: role cleared + staff log.
5. Manual slash commands still work.

## Done when

One `/tempban` notifies Discord; `/warning` hits game + Discord without manual slash commands.

**Depends on:** [04-tfmcweb-scaffold](./04-tfmcweb-scaffold.md).
