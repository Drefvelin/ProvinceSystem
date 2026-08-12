# Batch 28.06 — Kit journal (editable book)

**Plan + build:** Mark starter book line editable with `2d-template: book`; customise UI + bridge for two PNGs.

**Repos:** `Workspace/rpcharacters` (`kits.yml`) · `ProvinceSystem` lore customise · `frontend` `LoreItemEditor`  
**Depends on:** Step 27 templates · [02-api-storage](./02-api-storage.md) · [05-sign-swap](./05-sign-swap.md) preferred for E2E

## Locked

| Piece | Choice |
|-------|--------|
| Starter line | `path: v.WRITABLE_BOOK` + `editable` with `skin-png: journal_skin`, `base-set: books`, `2d-template: book`; **no** `3d-template` |
| Default asset | RPC `assets/journal_skin.png` as **unsigned** default for preview/catalog only; player must upload both covers on customise |
| Customise UI | Two PNG fields when `2d_template === book`; no 3D checkbox |
| Size | 16×16 each via `expectedSizeForField("book", …)` |
| Bridge | `create_submission` kind `book` with `unsigned` + `signed` |
| Pick existing | Pickable `book` skins for `base_set: books`; preview uses `_unsigned.png` |
| Claim apply | KitCustomiseApply merges book skin (`{slug}`); unsigned until signed in-game |

## Done

1. `kits.yml` — starter `v.WRITABLE_BOOK` editable (`journal_skin`, `books`, `2d-template: book`); `assets/journal_skin.png` + `saveResource` in RPC.
2. BE — `_submission_texture_path` falls back to `{sid}_unsigned.png`; customise accepts multipart `unsigned`+`signed`, bridges kind `book`.
3. FE — `LoreItemEditor` dual pickers when `flatKind === "book"`; hide 3D; api + edit page wire `unsignedFile`/`signedFile`.

## Verify

- [ ] Character kits show editable journal  
- [ ] Customise upload → pending book skin → ready → claim  
- [ ] Sign claimed journal → signed texture  
- [ ] `resetkit` (Step 27) allows re-customise journal  

## Status

**Implemented** (28.06 code). Operator ticks above. Next: [07-docs-verify](./07-docs-verify.md).
