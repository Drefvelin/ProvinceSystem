# Step 13 — Item 3D, shield, helmet 3D

**Repos:** `ProvinceSystem` + `Workspace/armourshop`  
**Depends on:** [step-12](../step-12/00-index.md)

## Goal

Upload and apply **`item_3d`**, **`shield`**, and **`helmet_3d`** (standalone + per-tier armor flag), with display autofill and shield blocking auto-clone.

## Locked rules

| Kind | Files | `base_set` |
|------|-------|------------|
| `item_3d` | `texture` + `model` → `{id}.png` + `{id}.json` | handheld ∪ large_handheld |
| `shield` | same | `shields` |
| `helmet_3d` | same | `helmets` |
| `armor_set` | per tier flat **or** 3D helmet | `tiers` + `helmet_3d_tiers` |

**Display after autofill** (player values win): both thirdperson, both firstperson, `ground`, `gui`, `fixed`.  
`head` required for `shield`, `helmet_3d`, and armor-tier 3D helmets only.

**Shield blocking:** ArmourShop clones mesh + locked **round** display Δ (not uploaded).

**Out of step:** guns; multi-view review bake; quotas beyond 512 KiB JSON.

## Batches

1. [01-planning-lock](./01-planning-lock.md) — docs + this index  
2. [02-display-api](./02-display-api.md) — display merge + API + storage  
3. [03-upload-ui](./03-upload-ui.md) — KindPicker + 3D Helmet checkbox  
4. [04-pack-3d](./04-pack-3d.md) — item_3d / helmet_3d / armor branch  
5. [05-pack-shield](./05-pack-shield.md) — ShieldWriter + round Δ  
6. [06-live-apply](./06-live-apply.md) — pull + shop + delete  
7. [07-docs-verify](./07-docs-verify.md) — checklist + smoke  

## Checkpoint

```text
docs → API/storage → UI → pack 3D → pack shield → live apply → verify
```

**Status (2026-08-08):** Batches 01–07 implemented (API/UI/writers/apply). Staging E2E boxes in [07](./07-docs-verify.md) remain for live server smoke.
