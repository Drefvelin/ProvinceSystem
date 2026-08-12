# Batch 28.03 — Book upload UI

**Plan + build:** `/skins` KindPicker entry + dual file fields + preview for `book`.

**Repos:** `ProvinceSystem/frontend` (`KindPicker`, `KindHelp`, `UploadForm`, sizes/helpers used by skins + lore editor)  
**Depends on:** [02-api-storage](./02-api-storage.md) (API field names locked)

## Locked

| Piece | Choice |
|-------|--------|
| Kind label | **Book** — unsigned + signed covers |
| Fields | Two PNG pickers: `unsigned`, `signed`; no 3D / model / grip |
| `base_set` | Select from `books` only (single option OK) |
| Size check | Client **16×16** each via `expectedSizeForField` / assert helpers |
| Preview | Side-by-side thumbnails; no WebGL model |
| Staff upload | Same kind available on staff path |
| Help copy | Unsigned = closed/writable look; signed = after player signs the book |

## Done

- `SkinKind` + `BOOK_FIELDS` / sizes / `baseSets.book`
- KindPicker + KindHelp for Book
- UploadForm dual slots + side-by-side thumbnails (not ModelPreview)
- `KNOWN_SKIN_KINDS` includes `book` (lore dual UI still 28.06)

## Verify

- [x] KindPicker lists Book  
- [x] Submit sends both files; wrong size blocked in UI  
- [x] Help copy mentions unsigned vs signed  
- [x] Staff path can select Book  

## Status

**Implemented** (28.03). Next: [04-pack-apply](./04-pack-apply.md).
