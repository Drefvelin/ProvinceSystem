# Batch 2.05 — Review and plugin pull

**Plan + build:** Staff approve/deny; plugin lists approved-not-applied payloads (for ArmourShop later).

## Plan

1. `POST /skins/submissions/{id}/approve` — `X-Staff-Key` → `status=approved`, `reviewed_at`.
2. `POST /skins/submissions/{id}/deny` — body `{ "reason": "…" }` → `denied` + reason.
3. `GET /skins/plugin/approved?since=…` — `X-Plugin-Key` → list approved where not `applied`, include id, uuid, slug, kind, display_name, file list / URLs.
4. File download for plugin: either signed paths or `GET /skins/plugin/submissions/{id}/files/{stem}` with plugin key (keep simple: plugin key + path under data dir).
5. `POST /skins/plugin/applied` — body `{ "submission_ids": ["…"] }` → mark `applied` (ArmourShop will call later; implement now so Step 2 API is complete).

No Discord calls in this batch (log “would notify” optional).

## Build

| File | Action |
|------|--------|
| `skins_routes.py` | approve, deny, approved list, file fetch, applied |
| `submissions.py` | status transitions |

## Verify

```bash
curl -X POST http://localhost:8000/skins/submissions/$ID/approve \
  -H "X-Staff-Key: $STAFF_KEY"

curl http://localhost:8000/skins/plugin/approved \
  -H "X-Plugin-Key: $PLUGIN_KEY"
```

- [ ] Pending → approved appears in plugin list  
- [ ] Deny stores reason; GET status shows it  
- [ ] Applied ack removes/omits from approved list  

## Out of scope

Discord cog, ArmourShop Java, frontend.
