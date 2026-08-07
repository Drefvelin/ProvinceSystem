# Batch 5.03 — Cog `/linkdiscord` + player DMs

**Plan + build:** Discord slash completes the link; bot DMs players for submitted / approved / denied.

**Repo:** `tfmc_bot` (extend [`skinsreview`](../../../../tfmc_bot/skinsreview/) — same config / staff key)

**Depends on:** [01-link-api](./01-link-api.md), [02-submit-and-notify](./02-submit-and-notify.md)

## Plan

1. Slash **`/linkdiscord`** with required `code` string → `POST /skins/discord/link/complete` with `interaction.user.id`; ephemeral success/fail (no public code leak).
2. Poller (alongside pending intake or shared interval): `GET /skins/staff/notifications` → DM “We received your skin submission (**Item name**).” → `ack`. If DM fails (closed DMs), still ack (or ack after log) so the queue does not stick — match minecraftban style logging.
3. After successful **Approve** in existing handler: DM “Your skin **Item name** was approved.”
4. After successful **Deny**: DM “Your skin **Item name** was denied.” + reason.
5. Use `discord_user_id` from pending payload / notification / fetch submission as needed; never ask the player for an id.
6. Cog README: `/linkdiscord`, slash enable/sync, DM behavior.

## Build

| File | Action |
|------|--------|
| `tfmc_bot/skinsreview/skinsreview.py` | Slash + notify poll + approve/deny DMs |
| `tfmc_bot/skinsreview/README.md` (or cog docs) | Player + staff notes |

## Verify

- [ ] `/linkdiscord CODE` links (after curl/in-game start)  
- [ ] Upload → player gets **submitted** DM  
- [ ] Approve → **approved** DM  
- [ ] Deny → **denied** DM with reason  
- [ ] Closed DMs: no crash; staff review still works  

## Out of scope

ArmourShop `/linkdiscord`, OAuth, applied DM.
