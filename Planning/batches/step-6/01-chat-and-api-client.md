# Batch 6.01 — Chat copy helper + skins code client

**Plan + build:** Shared click-to-copy chat; extend ProvinceSystem client for `POST /skins/codes`; polish `/linkdiscord` messaging.

**Repo:** `Workspace/armourshop`

## Plan

1. Add `ChatMessages` (or similar under `utils/`):
   - `sendCopyableCode(Player player, String introLine, String code)`  
   - Bungee `TextComponent` + `ClickEvent.Action.COPY_TO_CLIPBOARD` + hover “Click to copy”  
   - Send with `player.spigot().sendMessage(...)` (not plain `sendMessage`)
2. Extend [`ProvinceSystemClient`](../../../../Workspace/armourshop/src/main/java/net/tfminecraft/ArmourShop/api/ProvinceSystemClient.java):
   - `issueSkinsCode(playerUuid)` → `POST {base}/skins/codes` with plugin key  
   - Body `{"player_uuid":"…"}`; parse `code` / `expires_at` / `detail` (reuse existing JSON helpers)  
   - Same result shape as link start (`ok`, `code`, `expiresAt`, `error`) or shared type
3. Update [`LinkDiscordCommand`](../../../../Workspace/armourshop/src/main/java/net/tfminecraft/ArmourShop/managers/LinkDiscordCommand.java): show link code via `ChatMessages` instead of bold plain text; keep Discord `/linkdiscord CODE` instruction line.

## Build

| File | Action |
|------|--------|
| `…/utils/ChatMessages.java` | create |
| `…/api/ProvinceSystemClient.java` | `issueSkinsCode` |
| `…/managers/LinkDiscordCommand.java` | click-to-copy |

## Verify

- Rebuild ArmourShop (`mvn package`)  
- In game `/linkdiscord` → code is clickable / copies to clipboard  
- Unit/sanity: client method compiles; no token command yet  

## Out of scope

`/armourshop token create`, tab completer.
