# Step 27 — Kit skin templates + `resetkit`

**Repos:** `Workspace/rpcharacters` · `ProvinceSystem` · `frontend`  
**Depends on:** Step 26 kit asset sync + status ([step-26](../step-26/00-index.md))  
**Playbook:** [14-character-creator.md](../../14-character-creator.md)

## Goal

Declare per-editable-item **2D / optional 3D skin templates** on `kits.yml` so the website validates uploads like `/skins` (size + kind). Add staff **`/rpcharacter resetkit`** so a character can reclaim / re-customise a kit without remaking the character.

## Locked rules

| Piece | Choice |
|-------|--------|
| Templates | On `editable`: `2d-template` (required when editable), `3d-template` optional; omit 3D = no 3D checkbox |
| Vocabulary | Values are skin kind ids (`handheld`, `item_3d`, later `book`, …) |
| Keep | Existing `skin-png`, `base-set` |
| Catalog JSON | `2d_template`, `3d_template` (snake) on editable / lore-item rows |
| Website | Kind + PNG size from templates; reuse skins size rules |
| Knife starter | `2d-template: handheld`, `3d-template: item_3d` |
| `resetkit` | `/rpcharacter resetkit <player> <character_id> <kit_id>` (staff) |
| Reset clears | Kit status → `ELIGIBLE`; that kit’s cooldown; character `kit-customisations` for that kit’s editable keys; matching PS `lore_item_customisations` |
| Reset does not | Delete character; wipe unrelated kits |

## Batches

1. **[01-planning-lock](./01-planning-lock.md)** — Playbook YAML + vocabulary  
2. **[02-rpc-templates](./02-rpc-templates.md)** — `KitEditableSpec` + catalog sync fields  
3. **[03-customise-limits](./03-customise-limits.md)** — PS bridge + FE kind/size / hide 3D  
4. **[04-resetkit](./04-resetkit.md)** — Staff command + PS wipe  
5. **[05-docs-verify](./05-docs-verify.md)** — Hubs + STAGING  

## Checkpoint

```text
kits.yml templates → catalog → knife 16×16 / optional 3D
  → /rpcharacter resetkit … → claim/customise again
```

**Done when:** Templates drive kit upload validation; resetkit restores claim/customise for that kit; docs closed.

## Status

**27.01–27.05 done** (code+docs). Operator ticks in [STAGING.md](../../../STAGING.md) Step 27.
