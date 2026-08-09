# Batch 5.02 — Submit gate + submitted notifications

**Plan + build:** Uploads require an active Discord link; stamp `discord_user_id` on the submission; enqueue a “submitted” notification for the bot.

**Repo:** ProvinceSystem (tiny frontend error surface only)

**Depends on:** [01-link-api](./01-link-api.md)

## Plan

1. Add `submissions.discord_user_id` (nullable for legacy rows; **required** for new creates).
2. `create_submission`: look up link for session `player_uuid`; if missing → **400**  
   `Link Discord in-game with /linkdiscord first` (no “slug” jargon). Else stamp id on insert.
3. Table `skin_notifications`: `id`, `type` (`submitted`), `submission_id`, `discord_user_id`, `payload` (JSON: display_name, kind, …), `created_at`, `delivered_at`.
4. On successful create → enqueue `type=submitted`.
5. Staff routes (`X-Staff-Key`):
   - `GET /skins/staff/notifications` — undelivered rows (oldest first)
   - `POST /skins/staff/notifications/{id}/ack` — set `delivered_at`
6. `list_pending` / staff pending payload may include `discord_user_id`.
7. Frontend: no new fields; existing upload error display shows the 400 message.

## Build

| File | Action |
|------|--------|
| `schema.sql` / migrate | Column + `skin_notifications` |
| `submissions.py` | Require link; stamp; enqueue |
| `skins_routes.py` | notifications GET + ack |
| Frontend upload (if needed) | Already shows API `detail` |

## Verify

```bash
# Upload without link → 400 with link message
# After 5.01 link for same UUID → upload 200; submission has discord_user_id
curl -H "X-Staff-Key: $STAFF_KEY" http://localhost:8000/skins/staff/notifications
# ack id from list
curl -X POST -H "X-Staff-Key: $STAFF_KEY" \
  http://localhost:8000/skins/staff/notifications/$NID/ack
```

- [ ] No link → friendly 400  
- [ ] Linked → submit OK + `discord_user_id` set  
- [ ] Notification row appears; ack clears it from pending list  

## Out of scope

Cog DMs, ArmourShop, approve/deny DM text (5.03).
