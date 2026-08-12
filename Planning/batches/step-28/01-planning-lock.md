# Batch 28.01 — Planning lock (book kind)

**Plan + build:** Lock `book` in skins + ArmourShop + character playbooks; unsigned/signed contract matches this step index.

**Repos:** Planning hubs only (no product code)  
**Depends on:** [00-index](./00-index.md)

## Locked contract

| Field | Rule |
|-------|------|
| `kind` | `book` |
| Multipart | `unsigned`, `signed` (filenames ignored; stems from id) |
| Size | Both PNGs exactly **16×16** |
| Model | None |
| `base_set` | `books` |
| Pack IA | `{slug}` = `WRITABLE_BOOK` + unsigned tex; `{slug}_signed` = `WRITTEN_BOOK` + signed tex |
| Shop / pack | Player `ps_items` (+ staff path); shop lists `{slug}` only |
| Runtime | Unsigned on writable; signed after sign (28.05) |
| Kit | `2d-template: book`; no `3d-template`; grant stays `v.WRITABLE_BOOK` |

## Done

1. [05-skins-system.md](../../05-skins-system.md) — kind row, disk stems, validation, review, IA shape for `book`.  
2. [10-armourshop-itemsadder.md](../../10-armourshop-itemsadder.md) — BookWriter, two IA ids, shop `{slug}` only, sign swap.  
3. [14-character-creator.md](../../14-character-creator.md) — kit journal note + illustrative commented editable book block.  
4. STAGING operator ticks left unchecked (28.07).

## Verify

- [x] 05 kind table lists `book` with `unsigned`+`signed` @ 16×16  
- [x] 10 notes two IA items + sign-time swap  
- [x] 14 points kit journal at Step 28  

## Status

**Implemented** (28.01). Next: [02-api-storage](./02-api-storage.md).
