# Step 28 — Book skins + kit journal

**Repos:** `ProvinceSystem` · `frontend` · `Workspace/armourshop` · `Workspace/rpcharacters`  
**Depends on:** Step 27 templates + resetkit ([step-27](../step-27/00-index.md))  
**Playbook:** [05-skins-system.md](../../05-skins-system.md) · [10-armourshop-itemsadder.md](../../10-armourshop-itemsadder.md) · [14-character-creator.md](../../14-character-creator.md)

## Goal

Add first-class **`book`** skin kind (unsigned + signed 16×16 PNGs, no 3D) on `/skins` through Discord review and ArmourShop apply. On book sign, swap to the signed texture. Kits consume books via `2d-template: book` (starter journal) so donators can customise kit journals.

## Locked rules

| Piece | Choice |
|-------|--------|
| Kind | `book` — full `/skins` upload kind (player + staff curated paths) |
| Files | `unsigned` + `signed` PNGs; both **16×16**; no model |
| Disk stems | `{id}_unsigned.png`, `{id}_signed.png` |
| `base_set` | `books` only |
| 3D | Never; kit lines omit `3d-template` |
| Pack | Dedicated `BookWriter`: two textures + two IA items (`{slug}` writable / `{slug}_signed` written) |
| Shop | Sell/apply `{slug}` only (`ps_items`) |
| Sign swap | ArmourShop: writable → written replaces stack with `{slug}_signed`, keep display/PDC |
| Kit grant path | Keep `v.WRITABLE_BOOK`; IA merge for skin |
| Kit customise | Bridge uploads as `book`; two file fields when `2d_template === book` |
| Dup hash | Hash **unsigned** PNG (same pattern as single-texture kinds) |

## Batches (implement in order)

1. **[01-planning-lock](./01-planning-lock.md)** — Hub kind table + unsigned/signed contract  
2. **[02-api-storage](./02-api-storage.md)** — API, validation, meta, review sheet  
3. **[03-upload-ui](./03-upload-ui.md)** — KindPicker + dual files + preview  
4. **[04-pack-apply](./04-pack-apply.md)** — BookWriter + shop + live apply  
5. **[05-sign-swap](./05-sign-swap.md)** — Sign → signed IA item  
6. **[06-kit-journal](./06-kit-journal.md)** — Editable book line + customise bridge  
7. **[07-docs-verify](./07-docs-verify.md)** — Hubs + STAGING  

## Checkpoint

```text
/skins book upload → review → apply
  → kit journal customise → claim
  → sign book → signed texture
```

**Done when:** Book skins work on `/skins` and as kit journals; sign swap works; docs closed.

## Status

**28.01–28.07 done** (code+docs). Operator ticks in STAGING Step 28.
