# Batch 4.05 — Auto intake + AMP verify

**Plan + build:** Poll pending into `#bot-feed` without duplicates; document AMP deploy; close Step 4.

## Plan

1. Background task / Red loop: every N minutes (configurable, e.g. 60s–5m) `GET /skins/staff/pending`; for each id not yet posted, run same post path as 4.03.
2. Dedupe: cog Config set of posted submission ids (or rely on `discord_message_id` if set). Never repost approved/denied.
3. AMP notes in cog README or Planning: copy/pull `tfmc_bot` cog → reload; env vars; `#bot-feed` permissions (Send Messages, Embed Links, Attach Files).
4. End-to-end verify checklist below.

## Build

| File | Action |
|------|--------|
| skins review cog | poller + Config dedupe |
| `tfmc_bot` README or step note | AMP deploy blurb |

## Verify

With API local/staging + Red on AMP talking to that API:

- [ ] New pending upload appears in `#bot-feed` without slash (within poll interval)  
- [ ] No duplicate posts on next poll  
- [ ] Approve/deny still works  
- [ ] Live production website untouched  

## Step 4 exit criteria

```text
[x] Staff pending + file download API
[x] Cog on Red/AMP
[x] #bot-feed embed + raw PNGs
[x] Approve / Deny → API
[x] Auto poll without duplicates
```

## Out of scope

Review-sheet attachments, ban role, ArmourShop apply.
