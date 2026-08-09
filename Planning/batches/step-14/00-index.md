# Step 14 — Gun skins (carry / reload / aim)

**Repos:** `ProvinceSystem` + `Workspace/armourshop` (+ live GunsAndGadgets `skins.yml`)  
**Depends on:** [step-13](../step-13/00-index.md)

## Goal

Upload and apply **gun** skins: shared texture + three models (carry / reload / aim), GaG `skins.yml` material.CMD dual-write, shop `gunskin({id})`.

## Locked rules

| Piece | Choice |
|-------|--------|
| Kind | `gun` |
| Files | `texture` + `carry_model` / `reload_model` / `aim_model` |
| Disk | `{id}.png`, `{id}_carry.json`, `{id}_reload.json`, `{id}_aim.json` |
| `base_set` | `rifles` \| `pistols` \| `shotguns` \| `launchers` → GaG `types` |
| Display | Same as `item_3d` (7 tabs; no `head`) per model |
| Apply | CMD on stone_hoe (carry+reload) + crossbow (aim); append `skins.yml`; shop `gunskin({id})` |

**Out of step:** patching GaG for IA ids; scoped options; multi-view bake.

## Batches

1. [01-planning-lock](./01-planning-lock.md) — docs  
2. [02-api](./02-api.md) — kind + storage + display  
3. [03-upload-ui](./03-upload-ui.md) — KindPicker + form  
4. [04-pack](./04-pack.md) — GunWriter + CMD registry + skins.yml  
5. [05-live-apply](./05-live-apply.md) — apply + shop + delete  
6. [06-docs-verify](./06-docs-verify.md) — checklist  

## Checkpoint

```text
docs → API → UI → pack → live apply → verify
```

**Status:** Step 14 implemented (API `gun` kind, upload UI, GunWriter CMD dual-write, shop `gunskin({id})`, delete frees CMDs). Pack harness green including gun fixture.
