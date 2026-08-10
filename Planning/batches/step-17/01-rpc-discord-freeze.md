# Step 17.01 — RPCharacters Discord freeze API

**Plan + build:** Add an external Discord gate freeze reason that TFMCWeb can set/clear without touching characters.

**Status:** Implemented.

## Locked

| Piece | Choice |
|-------|--------|
| Reason | `FreezeReason.DISCORD_REQUIRED` |
| API | `PlayerManager.setDiscordGate` / `RPCharacters.setDiscordGate` + `reevaluateFreeze` |
| Scope | Existing freeze loop already skips non-`SURVIVAL` — keep that (staff/helpers trusted) |
| Characters | No deactivate / delete / slot changes |

## Done

1. `FreezeReason.DISCORD_REQUIRED` checked **first** in `getFreezeReason`.
2. In-memory UUID gate (not DB); notify points to `/linkdiscord`.
3. Admin verify: `/rpcharacter discordgate <player> <on|off>` (`Permissions.isAdmin`).

## Manual checklist

1. Survival + `discordgate on` → frozen; Discord message; characters unchanged  
2. Switch to Creative → unfrozen (loop clears)  
3. Back to Survival with gate still on → frozen again  
4. `discordgate off` → unfrozen if no other freeze reasons  

**Unblocks:** [04-tfmcweb-scaffold](./04-tfmcweb-scaffold.md).
