# Step 6 — In-game skins token (batch index)

**Repos:** `Workspace/armourshop` (ProvinceSystem codes API already exists)  
**Depends on:** Step 5 Discord link (required before mint)

Parent: [../../10-armourshop-itemsadder.md](../../10-armourshop-itemsadder.md), [../../05-skins-system.md](../../05-skins-system.md).

## Goal

Players run **`/armourshop token create`**, get a UUID-bound skins code with **click-to-copy** chat, redeem it on the website, and upload — no curl, no typing UUID. Mint requires an active Discord link.

## Locked rules

| Rule | Detail |
|------|--------|
| Command | `/armourshop token create` (player-only) |
| Tab complete | `token` → `create` |
| API | `POST /skins/codes` + `X-Plugin-Key` (no API changes) |
| Permission | `armourshop.token.create` (default false) or `armourshop.admin` |
| Chat | Bungee `COPY_TO_CLIPBOARD` via `player.spigot().sendMessage` |
| Mint vs link | Discord link **required** to mint (`POST /skins/codes` returns 400 if unlinked) |
| Also | `/linkdiscord` uses same click-to-copy for its code |

## Scope

| In | Out |
|----|-----|
| Chat helper + `issueSkinsCode` client | IA apply / pull approved |
| `/armourshop token create` + tab completer | Website redeem UI changes |
| Click-to-copy on link + token codes | OAuth |
| Docs + staging checklist | |

## Batch order

1. [01-chat-and-api-client](./01-chat-and-api-client.md) — copy helper + codes HTTP + `/linkdiscord` polish  
2. [02-token-command](./02-token-command.md) — command + tab complete  
3. [03-docs-verify](./03-docs-verify.md) — docs + in-game → website checklist  

**Process:** one batch = one plan + implement; stop after verify; start the next only when asked.

## Config

Reuse Step 5 `skins-api` in ArmourShop `config.yml`:

| Key | Purpose |
|-----|---------|
| `skins-api.base-url` | ProvinceSystem base (no trailing slash) |
| `skins-api.plugin-key` | `X-Plugin-Key` |

## Final checkpoint

```text
/linkdiscord (optional first) → Discord complete
→ /armourshop token create → click code to copy
→ redeem on /skins → upload
→ Discord review as today
```

## Verify

Tick after staging is green (see [STAGING.md](../../../STAGING.md) mint checklist):

- [ ] Tab complete works  
- [ ] Code redeems on website  
- [ ] Upload succeeds (Discord already linked)  
