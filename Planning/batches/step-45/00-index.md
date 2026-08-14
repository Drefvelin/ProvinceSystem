# Step 45 — Map chronicle

**Repos:** `ProvinceSystem` (+ SF event emission)  
**Depends on:** [step-38](../step-38/00-index.md)  
**Playbook:** [16-map-platform.md](../../16-map-platform.md) — requirement 11

## Goal

Daily composited map snapshot plus structured changelog (events since previous day) for season recap, slideshow, and future animation tooling.

## Locked rules

| Piece | Choice |
|-------|--------|
| Snapshot | Daily copy of composited master (base + political); retention policy TBD |
| Events | Prefer SF `events[]` emission; supplement with nation.json diffs |
| Storage | `snapshots/{map}/{YYYY-MM-DD}/` + `chronicle/{map}/events.jsonl` |
| Slideshow | Frame URLs + event log sufficient for v1; video gen out of scope |

## Batches (when step starts)

1. **01-planning-lock**  
2. **02-snapshot-job** — Cron/post-regen hook  
3. **03-event-log** — SF events + diff fallback  
4. **04-chronicle-api** — List snapshots + events for frontend  
5. **05-docs-verify** — STAGING Step 45  

## Status

**Planned.**
