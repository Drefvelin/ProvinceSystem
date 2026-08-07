# Batch 6.02 — `/armourshop token create` + tab complete

**Plan + build:** In-game mint of skins upload codes with tab completion.

**Repo:** `Workspace/armourshop`

**Depends on:** [01-chat-and-api-client](./01-chat-and-api-client.md)

## Plan

1. Extend [`CommandManager`](../../../../Workspace/armourshop/src/main/java/net/tfminecraft/ArmourShop/managers/CommandManager.java):
   - Keep: no-args → shop GUI; `reload` → admin reload  
   - Add: `token create` → player-only; require `armourshop.token.create` **or** `armourshop.admin`  
   - Async HTTP `issueSkinsCode(uuid)` → sync chat: click-to-copy code + “Redeem on the skins website” + optional expiry  
   - Clear errors if API/config missing (same pattern as `/linkdiscord`)
2. Tab completer (on `CommandManager` or dedicated class like Guides):
   - args length 1: suggest `token`, and `reload` if admin  
   - args length 2 and `token`: suggest `create`  
   - Filter by prefix (Guide-style)
3. Register tab completer in [`ArmourShop.onEnable`](../../../../Workspace/armourshop/src/main/java/net/tfminecraft/ArmourShop/ArmourShop.java) on `armourshop`.
4. [`plugin.yml`](../../../../Workspace/armourshop/src/main/resources/plugin.yml):
   - Document usage `/armourshop token create`  
   - Permission `armourshop.token.create` default `false`  
   - Ensure `armourshop.admin` remains for reload

## Build

| File | Action |
|------|--------|
| `CommandManager.java` | token create + optional TabCompleter |
| `ArmourShop.java` | `setTabCompleter` |
| `plugin.yml` | usage + permission |
| `Permissions.java` | helper `canCreateToken` if useful |

## Verify

- Tab: `/armourshop ` → `token`; `/armourshop token ` → `create`  
- Without perm → denied; with LP node or admin → code issued  
- Click copies code; redeem on staging `/skins` works for that UUID  

## Out of scope

IA apply; website changes; Discord link gate on mint.
