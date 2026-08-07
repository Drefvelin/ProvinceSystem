# Batch 5.04 — ArmourShop `/linkdiscord`

**Plan + build:** In-game command starts Discord link via ProvinceSystem plugin API.

**Repo:** [`Workspace/armourshop`](../../../../Workspace/armourshop)

**Depends on:** [01-link-api](./01-link-api.md)

## Plan

1. Register Bukkit command **`/linkdiscord`** (player-only; no console).
2. Config: API base URL + plugin key (`X-Plugin-Key`) — same secrets style as planned skins code mint ([10](../../10-armourshop-itemsadder.md)).
3. On command: `POST /skins/discord/link/start` with online player UUID + name; show plaintext code and instruction: run `/linkdiscord <code>` in TFMC Discord.
4. Clear errors for API down / 401 / 400.
5. Do **not** ask for Discord id in game. Skins code mint can stay as today; website enforces link on upload.

## Build

| File | Action |
|------|--------|
| `plugin.yml` | Register `linkdiscord` |
| `CommandManager` (or dedicated executor) | Handle `/linkdiscord` |
| HTTP client + config | `link/start` |
| `config.yml` / example | `api_base`, plugin key |

## Verify

- [ ] In game `/linkdiscord` prints a code  
- [ ] Discord `/linkdiscord` that code (5.03) completes link  
- [ ] Same UUID can upload on site after redeem  

## Out of scope

Full IA apply / pull approved (B3); refusing skins code if unlinked (site gate is enough).
