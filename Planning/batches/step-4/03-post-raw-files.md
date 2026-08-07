# Batch 4.03 — Post raw files to `#bot-feed`

**Plan + build:** Post a pending submission into `#bot-feed` with embed + raw PNG attachments.

## Plan

1. Slash e.g. `/skinsreview post <submission_id>` (staff/helper): fetch pending metadata + each file via staff file API; post to `BOT_FEED_CHANNEL_ID`.
2. Embed fields: id, slug, display_name, kind, grip_preset, player_uuid, created_at.
3. Attach all listed `*.png` files (Discord limits — six armor icons/layers is OK). Filename = server stem.
4. Optional: `/skinsreview pending` lists ids from staff pending (ephemeral) to copy into post.
5. Do **not** call review-sheet yet.

## Build

| File | Action |
|------|--------|
| skins review cog | post + download helpers |

## Verify

- [ ] Message appears in `#bot-feed`  
- [ ] Attachments open as correct textures  
- [ ] Unknown id / non-pending → friendly error  

## Out of scope

Approve/deny UI, auto-poll.
