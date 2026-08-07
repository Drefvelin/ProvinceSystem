# 11 — Discord bot (`tfmc_bot`)

Red Discord bot for TFMC staff tooling. Repo: `tfmc_bot/` (sibling of `ProvinceSystem/`).

Skins API contracts: [05-skins-system.md](./05-skins-system.md).  
Apply after approve: [10-armourshop-itemsadder.md](./10-armourshop-itemsadder.md).

## Current cogs

| Cog | Path | What it does today |
|-----|------|--------------------|
| **minecraftban** | `tfmc_bot/minecraftban/` | Slash `/minecraftban`, `/minecraftwarn`: ephemeral preview, DM user, log embed to staff channel |
| **tfmcbotstaus** | `tfmc_bot/tfmcbotstaus/` | Rotates bot presence / activity |

Ban cog is **notification + logging only**. It does not ban players on the Minecraft server. Staff ban in-game with server commands (e.g. LiteBans); Discord is for telling the user and (soon) muting them in Discord.

## Planned: skins review cog

New cog (name e.g. `skinsreview` / `tfmcskins`):

1. Receive pending submissions (webhook from API, or poll `pending` with staff key).  
2. Post embed: submission id, slug, display name, kind, player UUID, preview image(s).  
3. Buttons: **Approve** / **Deny**.  
4. Deny opens modal for reason.  
5. Call ProvinceSystem staff API (`X-Staff-Key`).  
6. Edit original message to show outcome (prevent double-clicks).

Permissions: Staff (and Helper if desired)—same pattern as minecraftban role checks.

Does not write ItemsAdder files; ArmourShop pulls after status is `approved`.

## Planned: banned role on ban / clear on unban

Extend moderation Discord side:

| Action | Bot behavior |
|--------|----------------|
| Ban notify (`/minecraftban` or dedicated flow) | Existing DM + log **and** add configured **Banned** role |
| Unban / clear (`/minecraftunban` or similar) | Remove **Banned** role; optional log |

Channel mute = Discord permission overwrites on that role (deny Send Messages in selected channels). Configure role id via env/config (same style as `LOG_CHANNEL_ID`, `STAFF_ROLE_ID`).

**Non-goals**

- Syncing with LiteBans / automatic MC ban from Discord  
- Replacing in-game punishment commands  

## Config / secrets

| Secret | Where |
|--------|-------|
| Bot token | Red / hosting env |
| `STAFF_KEY` | Bot env only — calls ProvinceSystem |
| API base URL | Bot env |
| Role / channel ids | Env or Red config (log channel, staff, helper, banned role) |

Never put staff keys in ProvinceSystem frontend.

## Local / staging

- Run Red with the cogs loaded against staging API.  
- Skins review can be tested with curl-created pending submissions.  
- Ban role: test on a private Discord guild first.

Website skins MVP does not require the bot ([06](./06-local-development.md)); approve via curl until this cog exists.

## Implementation checklist (bot track)

- [ ] Skins cog: notify + approve/deny + message update  
- [ ] Ban: add role on ban notify  
- [ ] Unban command: remove role  
- [ ] Document required Discord permission setup for banned role  
- [ ] Keep status cog as-is unless unwanted  

## See also

- [12-end-to-end-flows.md](./12-end-to-end-flows.md) — skins + ban journeys  
- [08-implementation-checklist.md](./08-implementation-checklist.md) — Bot track  
