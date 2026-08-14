# 11 — Discord bot (`tfmc_bot`)

Staff tooling as **[Red-DiscordBot](https://github.com/cog-creators/red-discordbot)** V3 cogs. Repo: `tfmc_bot/` (sibling of `ProvinceSystem/`). No separate bot framework — same Red instance as today.

Skins API: [05-skins-system.md](./05-skins-system.md).  
Apply after approve: [10-armourshop-itemsadder.md](./10-armourshop-itemsadder.md).  
Batches: [batches/step-4/00-index.md](./batches/step-4/00-index.md) (staff review), [batches/step-5/00-index.md](./batches/step-5/00-index.md) (Discord link + player DMs).

## Hosting

- **AMP (CubeCoders)** runs the Red instance.
- Deploy: update files under `tfmc_bot/` on the instance → `[p]reload <cog>` or restart Red in AMP.
- Point the skins cog at **local/staging** ProvinceSystem while developing — live website is not required for Discord review tests.

## Current cogs

| Cog | Path | What it does today |
|-----|------|--------------------|
| **skinsreview** | `tfmc_bot/skinsreview/` | `#bot-feed` composite review sheet; Approve/Deny; poll pending; `/linkdiscord`; player DMs (submitted / approved / denied) |
| **minecraftban** | `tfmc_bot/minecraftban/` | Slash `/minecraftban`, `/minecraftwarn` (manual); polls moderation outbox for auto warn/ban/unban + Banned role |
| **tfmcbotstaus** | `tfmc_bot/tfmcbotstaus/` | Rotates bot presence / activity |

Ban cog is **notification + logging only**. It does not ban players on the Minecraft server. Staff ban in-game with **Essentials**; Discord DMs + **Banned** role are mirrored automatically via TFMCWeb ([13-tfmcweb.md](./13-tfmcweb.md), [step-17.07](./batches/step-17/07-warn-and-ban-mirror.md)). Config: `minecraftban/config.yml` (`api_base_url`, `staff_key`, `banned_role_id`) — env overrides still work.

## Guild leave / join (Step 17) — bot half implemented

Leave/join → identity grace is wired in **skinsreview** (`guild_id` / `GUILD_ID`; `on_member_remove` / `on_member_join`). See [step-17.03](./batches/step-17/03-bot-guild-events.md).

| Event | Behaviour |
|-------|-----------|
| Member leaves TFMC guild | `POST` identity `guild/left` → **1h grace** (link kept) |
| Member rejoins within grace | `POST` identity `guild/joined` → clear grace |
| Grace expires | Unlink + notice → TFMCWeb freezes Survival via RPCharacters |

See [13-tfmcweb.md](./13-tfmcweb.md). In-game half is **TFMCWeb** (`/linkdiscord`, notices, Survival gate).

## Planned: skins review cog (Step 4) — implemented

New cog (e.g. `skinsreview` / `tfmcskins`) in `tfmc_bot/`:

1. Discover pending submissions: poll `GET /skins/staff/pending` (`X-Staff-Key`) and/or slash post-by-id.
2. Post to **`#bot-feed`**: embed with the human **Submission id** shown prominently, Item name, kind, **Tiers** (armor, comma-joined) or **Base set** (non-armor), grip, **Minecraft name**, **Discord mention/username**. No `player_key` anywhere (Step 11 removed it) — footer is unused unless `slug` ever differs from `id`. Do **not** show raw MC UUID or Discord snowflake as fields.
3. **Attach one composite `review_sheet.png`** (NN-upscaled textures + coloured display name) via staff file download or `GET …/review-sheet`. Do **not** dump raw 16×16 PNGs into Discord.
4. Buttons: **Approve** / **Deny**.
5. Deny opens modal for reason.
6. Call `POST …/approve` or `POST …/deny` with `X-Staff-Key`.
7. Edit original message to show outcome; disable buttons (prevent double-clicks).

Permissions: Staff (and Helper if desired) — same pattern as `minecraftban` role checks.

Does not write ItemsAdder files; ArmourShop pulls after status is `approved`.

## Step 5 — `/linkdiscord` + player DMs

Batches: [step-5](./batches/step-5/00-index.md).

| Piece | Behavior |
|-------|----------|
| `/linkdiscord <code>` | Call `POST /skins/discord/link/complete` with the invoking user’s Discord id; ephemeral result |
| Submitted DM | Poll `GET /skins/staff/notifications` → DM “submission received” → ack |
| Approved / denied DM | After successful staff approve/deny; deny includes reason |
| Closed DMs | Log failure; do not break review flow |

In-game half: TFMCWeb `/linkdiscord` → `link/start` ([13](./13-tfmcweb.md); pack apply still [10](./10-armourshop-itemsadder.md)).

## Banned role on ban / clear on unban (Step 17.07)

| Action | Bot behavior |
|--------|----------------|
| Ban notify (auto outbox or `/minecraftban`) | DM + log **and** add `BANNED_ROLE_ID` when set |
| Unban (auto outbox from Essentials) | Remove **Banned** role + staff log (no player DM) |

Channel mute = Discord permission overwrites on that role.

**Non-goals**

- Syncing with LiteBans / automatic MC ban from Discord  
- Replacing in-game punishment commands  

## Config / secrets (AMP / Red env)

| Secret / setting | Where |
|------------------|--------|
| Bot token | Red / AMP |
| `STAFF_KEY` | AMP/Red env only — ProvinceSystem staff API |
| `API_BASE_URL` | AMP/Red env (local or staging API while testing) |
| `BOT_FEED_CHANNEL_ID` | `#bot-feed` |
| `STAFF_ROLE_ID` / `HELPER_ROLE_ID` | Same pattern as minecraftban |
| `LOG_CHANNEL_ID` | Ban cog (existing) |

Never put staff keys in the ProvinceSystem frontend or public repo config.

## Local / staging

1. Run ProvinceSystem API locally (`SKINS_DEV=1` or real `STAFF_KEY`).  
2. Create a pending submission (local `/skins` or curl).  
3. Red on AMP (or a local Red for cog dev) with `API_BASE_URL` → that API and `BOT_FEED_CHANNEL_ID` → `#bot-feed`.  
4. Confirm message + composite `review_sheet.png` in Discord; approve/deny; API status updates.

Live production website can stay unchanged during this work.

## Implementation checklist (bot track)

- [x] Skins cog: pending intake + **composite review_sheet.png** in `#bot-feed` + approve/deny + message update  
- [x] Staff API: pending list + staff file download ([step-4/01](./batches/step-4/01-staff-pending-api.md))  
- [x] `/linkdiscord` + submitted/approve/deny DMs ([step-5](./batches/step-5/00-index.md))  
- [x] Ban: add role on ban notify ([step-17.07](./batches/step-17/07-warn-and-ban-mirror.md))  
- [x] Unban: remove role on unban notify  
- [ ] Document Discord permission setup for banned role  
- [ ] Keep status cog as-is unless unwanted  

## See also

- [12-end-to-end-flows.md](./12-end-to-end-flows.md) — skins + ban journeys  
- [08-implementation-checklist.md](./08-implementation-checklist.md) — Bot track  
- [06-local-development.md](./06-local-development.md) — local API + bot  
- [batches/step-12/00-index.md](./batches/step-12/00-index.md) — unified review sheet + submit UX  
