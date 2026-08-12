# Batch 28.04 — Book pack writer + live apply

**Plan + build:** ArmourShop writes IA items + shop YAML for `book`; pull/apply like other flats.

**Repos:** `Workspace/armourshop` (`PackKind`, `BookWriter`, `PackApplyService`, `ShopSubmissionWriter`, harness, pull)  
**Depends on:** [02-api-storage](./02-api-storage.md); UI can parallel

## Locked

| Piece | Choice |
|-------|--------|
| `PackKind` | Add `BOOK` |
| Writer | New `BookWriter` (do not overload `FlatItemWriter`) |
| Textures | `item/{slug}_unsigned.png`, `item/{slug}_signed.png` |
| IA item `{slug}` | `material: WRITABLE_BOOK`, `generate: true`, `parent: item/generated`, texture unsigned |
| IA item `{slug}_signed` | `material: WRITTEN_BOOK`, same generate/parent, texture signed |
| Shop | `ps_items` (player) / staff category; lists **`{slug}` only**; permission node as other items |
| Apply | Approved → write pack + shop + LP; ack applied |
| Delete | Remove both textures + both IA configs + shop row (same deferred delete path) |
| Pack files map | Pull maps API stems `unsigned`/`signed` → writer stems |
| Base set | `books` → MI `books.LETTER` (writable book) |

## Done

- `PackKind.BOOK` + `BookWriter` (dual PNG + dual items in one yml)
- `PackApplyService` stem map + `writeKind` book
- `ShopSubmissionWriter.isItemKind` includes book
- `PackSubmissionRemover` → `BookWriter.remove`
- `base-sets.yml` `books:` + harness `harness_book`

## Verify

- [x] Harness writes unsigned+signed textures and both IA ids  
- [ ] Live apply: approved book usable as writable-book skin (operator / STAGING)  
- [ ] Shop shows one entry; signed item exists for 28.05 (operator)  
- [ ] Staff curated path works if enabled for kind (operator)  

## Status

**Implemented** (28.04 code + harness). Next: [05-sign-swap](./05-sign-swap.md).
