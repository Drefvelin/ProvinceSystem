# Batch 2.04 — Submissions upload

**Plan + build:** Authenticated session creates `armor_set` or `item_2d` submission; files saved with fixed stems.

> **Superseded for kinds:** [06-asset-rules](./06-asset-rules.md) replaces `item_2d` with `item` / `handheld` / `large_handheld` and exact pixel sizes. Keep this batch as the historical upload scaffold.

## Plan

1. `storage.py`: given `submission_id` + `slug` + `kind`, write PNGs under `data/skins/{id}/`, ignore client filenames, write `meta.json`.
2. PNG checks: magic bytes `\x89PNG`, max size (e.g. 2MB each), optional max dimension later.
3. `POST /skins/submissions` — `Authorization: Bearer <session>` (or `X-Session-Token`):
   - fields: `kind`, `slug`, `display_name`
   - files: armor → `helmet`, `chestplate`, `leggings`, `boots`, `layer_1`, `layer_2`; item_2d → `texture`
4. Validate slug (`assert_slug` + uniqueness among pending/approved/applied).
5. Insert `submissions` row `status=pending`, `dir_path` set.
6. `GET /skins/submissions/{id}` — owner session only (or public status fields without paths for later UI).

## Build

| File | Action |
|------|--------|
| `backend/src/skins/storage.py` | create |
| `backend/src/skins/submissions.py` | create |
| `backend/src/api/skins_routes.py` | add submit + get |

## Verify

Redeem `TEST-CODE-1`, then:

```bash
curl -X POST http://localhost:8000/skins/submissions \
  -H "Authorization: Bearer $SESSION" \
  -F kind=armor_set -F slug=blue_knight -F display_name="Blue Knight" \
  -F helmet=@h.png -F chestplate=@c.png -F leggings=@l.png -F boots=@b.png \
  -F layer_1=@l1.png -F layer_2=@l2.png
```

- [ ] Directory contains `blue_knight_helmet.png` … `blue_knight_layer_2.png` + `meta.json`  
- [ ] Bad slug → 400; duplicate slug → 409  
- [ ] `item_2d` with one `texture` → `{slug}.png`  

## Out of scope

Staff approve, Discord notify, plugin pull body.
