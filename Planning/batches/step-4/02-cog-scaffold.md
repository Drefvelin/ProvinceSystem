# Batch 4.02 — Cog scaffold

**Plan + build:** Red V3 skins review cog loads on Red (AMP or local) with config and HTTP client stubs.

**Repo:** `tfmc_bot/`  

## Plan

1. New cog package (e.g. `skinsreview/`) with `__init__.py`, `info.json`, main cog module — follow `minecraftban` layout.
2. Config / env: `API_BASE_URL`, `STAFF_KEY`, `BOT_FEED_CHANNEL_ID`, staff/helper role ids (env defaults like minecraftban).
3. Shared helpers: `staff_headers()`, `api_get/post`, role check `has_staff_or_helper`.
4. Minimal slash command e.g. `/skinsreview ping` → hits `GET {API}/ping` or pending with staff key and replies ephemeral OK/error (proves connectivity from AMP to API).
5. Document in cog docstring: Red + AMP reload steps.

## Build

| File | Action |
|------|--------|
| `tfmc_bot/skinsreview/` (name may vary) | create cog package |

## Verify

- [ ] `[p]load skinsreview` (or install path used on AMP) succeeds  
- [ ] Slash ping / connectivity check works against local/staging API  
- [ ] Wrong `STAFF_KEY` → clear error  

## Out of scope

Posting embeds, attachments, approve/deny buttons.
