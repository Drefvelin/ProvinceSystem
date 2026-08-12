# Batch 27.02 — RPC templates + catalog

**Plan + build:** Parse `2d-template` / `3d-template` on editable kit lines; push on creation catalog / editable_kit / kits payload.

**Repos:** `Workspace/rpcharacters` (`KitEditableSpec`, `KitLoader`, `CreationCatalogSyncService`, `EditableKitPreviewBuilder`) · `ProvinceSystem` (`creation_catalog.py`)  
**Depends on:** [01-planning-lock](./01-planning-lock.md)

## Locked

| Piece | Choice |
|-------|--------|
| Spec fields | `2dTemplate`, `3dTemplate` (nullable) |
| YAML keys | `2d-template`, `3d-template` |
| Catalog keys | `2d_template`, `3d_template` |
| Starter knife | `handheld` + `item_3d` |
| Invalid / missing 2d | Fail-loud: kit not loaded (severe log) |

## Done

- `kits.yml` knife: `2d-template: handheld`, `3d-template: item_3d`
- `KitEditableSpec` + `KitLoader.parseEditable` (missing 2d → severe + kit rejected)
- `EditableKitPreviewBuilder.Row` + catalog `2d_template` / optional `3d_template`
- PS `_normalize_editable_kit` preserves template fields

## Verify

- [x] Reload kits.yml with templates; catalog JSON includes both fields for knife
- [x] Editable line without `3d-template` omits / nulls `3d_template`
- [x] Existing `skin_png` / `base_set` still sync

## Status

**Implemented** (27.02). Next: [03-customise-limits](./03-customise-limits.md).
