# Batch 28.02 — Book API + storage

**Plan + build:** Accept `book` submissions with two PNGs; persist; review sheet shows both.

**Repos:** `ProvinceSystem/backend` (`submissions.py`, `storage.py`, `review_sheet.py`, skins routes, e2e/fixtures if present)  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Locked

| Piece | Choice |
|-------|--------|
| Allowed kinds | Add `book` to `ALLOWED_KINDS` |
| `BASE_SETS` | `"book": frozenset({"books"})` |
| Files | Require `unsigned` + `signed`; reject missing either |
| Dimensions | Each PNG exactly **16×16** (reuse existing PNG size helpers) |
| Disk stems | `{id}_unsigned.png`, `{id}_signed.png` |
| Meta | `kind: book`; no model / grip fields |
| Dup hash | `texture_hash` from **unsigned** bytes |
| Review sheet | Dual-tile unsigned + signed |
| Name colours/styles | Same optional fields as other item skins |
| Approved payload | Include both file URLs/stems for ArmourShop pull |

## Done

- `ALLOWED_KINDS` / `BASE_SETS["book"]` = `books`
- `create_submission` requires `BOOK_FIELDS`; `texture_sha256` falls back to `unsigned`
- `write_submission_files` writes `{slug}_unsigned.png` / `{slug}_signed.png`
- Review sheet `_book_body` dual tiles
- `skins_e2e_smoke.py` book negative + happy + approved files

## Verify

- [x] Upload missing one PNG → 400  
- [x] Wrong dimensions → 400  
- [x] `base_set` other than `books` → 400  
- [x] Pending list + review sheet include both textures  
- [x] Approved pull payload lists both files  

## Status

**Implemented** (28.02). Next: [03-upload-ui](./03-upload-ui.md).
