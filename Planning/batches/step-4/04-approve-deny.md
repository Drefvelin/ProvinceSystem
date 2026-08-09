# Batch 4.04 — Approve / Deny

**Plan + build:** Message components call staff approve/deny; update Discord message.

## Plan

1. On post (4.03), add **Approve** / **Deny** buttons (custom_ids include submission id).
2. Approve → `POST /skins/submissions/{id}/approve` with staff key; edit embed to Approved; disable buttons.
3. Deny → modal for reason → `POST …/deny` with `{reason}`; edit embed with reason; disable buttons.
4. Role-gate button interactions (staff/helper). Ignore if already terminal status (API 400 → tell user).
5. Store `discord_message_id` on API if easy (optional column already exists) — nice-to-have, not blocking.

## Build

| File | Action |
|------|--------|
| skins review cog | View/button/modal handlers |
| Optional API | set `discord_message_id` on post/approve |

## Verify

- [ ] Approve → API `approved`; message updated  
- [ ] Deny with reason → API `denied` + reason; message updated  
- [ ] Second click does not double-apply  

## Out of scope

Auto-poll, ArmourShop.
