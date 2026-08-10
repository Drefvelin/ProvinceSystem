# Step 17.04 — TFMCWeb scaffold + Survival Discord gate

**Plan + build:** New [`Workspace/tfmcweb`](../../../../Workspace/tfmcweb/) plugin: HTTP, link cache, `/linkdiscord`, notice poller, Survival gate via RPCharacters.

## Config

`plugins/TFMCWeb/config.yml` (see jar `config.yml`):

```yaml
api:
  base-url: "http://127.0.0.1:18001"   # no trailing slash
  plugin-key: "dev-plugin-key"
```

Header: `X-Plugin-Key`. Soft-depend **RPCharacters** (gate via reflection); if missing, link/HTTP still work and gate is skipped with a warning.

## Behaviour

| Piece | Detail |
|-------|--------|
| HTTP | `POST /skins/discord/link/start`, `…/unlink`, `GET /skins/discord/status/{uuid}`, notices list/ack |
| Cache | UUID → linked, eligible, in_grace, discord ids, grace_until |
| Gate | Survival + !eligible → `RPCharacters.setDiscordGate(true)`; else clear |
| Join | Async status sync → apply gate |
| Notices | `link_success` (ack if online), `guild_left_grace` / `guild_rejoined` / `grace_expired` (ack after cache update) |
| Coexistence | ArmourShop softdepends TFMCWeb; if TFMCWeb enabled, AS skips link/unlink + notice poller |

## Commands

| Command | Perm | Action |
|---------|------|--------|
| `/linkdiscord` | `tfmcweb.linkdiscord` (default true) | Issue link code (async) |
| `/unlinkdiscord` | same | Unlink + gate if Survival |
| `/web status` | `tfmcweb.admin` | API ping + cache stats |
| `/web reload` | admin | Reload config.yml |
| `/web lookup <player>` | admin | Cache + live status |
| `/web unlink <player>` | admin | Force unlink |
| `/web reconcile` | admin | Status + gate for all online |

## Build

```text
cd Workspace/tfmcweb && mvn -q package
# jar → Builds/TFMCWeb/tfmcweb-1.0-SNAPSHOT.jar
```

Requires rebuilt **RPCharacters** with `setDiscordGate` (17.01) on the server.

## Verify (staging)

1. Drop TFMCWeb + updated RPC + TLibs; set `api.*` to staging API.
2. With TFMCWeb loaded, ArmourShop logs yield of link/notices.
3. Survival unlinked join → frozen (`DISCORD_REQUIRED`); non-Survival not gated.
4. `/linkdiscord` → Discord `/linkdiscord <code>` → unfrozen.
5. Leave guild (bot 17.03) → playable in grace; after `grace_expired` → frozen; rejoin within 1h → clear.
6. `/web reconcile` refreshes online players.

## Done when

Fresh Survival player without link is frozen; `/linkdiscord` → Discord complete → unfrozen; leave grace behaves per [13](../../13-tfmcweb.md).

**Depends on:** [01-rpc-discord-freeze](./01-rpc-discord-freeze.md), [02-identity-api](./02-identity-api.md), [03-bot-guild-events](./03-bot-guild-events.md).

**Out of this batch:** `/token` (landed in [05](./05-token-scopes.md)), full ArmourShop cutover (06), warn/ban (07).
