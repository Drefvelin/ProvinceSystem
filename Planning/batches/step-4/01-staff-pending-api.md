# Batch 4.01 — Staff pending API

**Plan + build:** Staff-key endpoints so the Discord cog can list pending submissions and download raw PNGs.

**Repo:** ProvinceSystem  

## Plan

1. `GET /skins/staff/pending` — header `X-Staff-Key` → list submissions with `status=pending`, ordered by `created_at` ASC. Each item: `id`, `player_uuid`, `slug`, `kind`, `display_name`, `grip_preset`, `created_at`, `files` (PNG names on disk, same helper as plugin approved list).
2. `GET /skins/staff/submissions/{id}/files/{filename}` — `X-Staff-Key`; safe resolve via existing `resolve_submission_file`; `FileResponse` image/png. 401 without staff key; 404 if missing.
3. Reuse approve/deny/review-sheet already present; no Discord calls in API.

## Build

| File | Action |
|------|--------|
| `backend/src/skins/submissions.py` | `list_pending()` |
| `backend/src/api/skins_routes.py` | staff pending + staff file routes |

## Verify

```bash
curl -H "X-Staff-Key: $STAFF_KEY" http://localhost:8000/skins/staff/pending
curl -H "X-Staff-Key: $STAFF_KEY" -o out.png \
  http://localhost:8000/skins/staff/submissions/$ID/files/$FILENAME
```

- [ ] Pending row appears after upload  
- [ ] File download is a valid PNG  
- [ ] Missing staff key → 401  

## Out of scope

Cog code, review-sheet changes, plugin routes.
