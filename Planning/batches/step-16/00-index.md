# Step 16 — Upload 3D model preview

**Repos:** `ProvinceSystem` frontend (`/skins`)  
**Depends on:** [step-13](../step-13/00-index.md), [step-14](../step-14/00-index.md), [step-15](../step-15/00-index.md)

## Goal

Add a live WebGL preview on the skins upload form for Java item models: cubes + UVs + texture, then held on Steve with third-person display.

## Locked rules

| Piece | Choice |
|-------|--------|
| Format | Java item JSON (`elements` / `textures` / `display`) + PNG (same as pack writers) |
| Renderer | Same Three.js canvas for model-only and in-hand (no second viewer lib) |
| Held view | Steve mannequin + `display.thirdperson_righthand` (+ API defaults) |
| First code batch | [02-json-model-render](./02-json-model-render.md) — one model + one texture, correct UVs |
| Later in step | Full display-slot picker; kind variants (gun / bow / …); flat PNG fallback |

**Out of step:** Discord multi-view review-sheet bake; armor body-layer player preview; editing transforms; poseable bow/crossbow arms.

## Batches

1. [01-planning-lock](./01-planning-lock.md) — docs  
2. [02-json-model-render](./02-json-model-render.md) — reliable JSON + PNG render  
3. [03-display-slots](./03-display-slots.md) — Steve held view + thirdperson_righthand  
4. [04-kind-variants](./04-kind-variants.md) — gun poses, bow frames, etc.  
5. [05-upload-ui](./05-upload-ui.md) — embed on `/skins` upload  
6. [06-docs-verify](./06-docs-verify.md) — checklist  

## Checkpoint

```text
docs → json render → held view → kind variants → upload UI → verify
```

**Status:** Batches 02–03 done (JSON+PNG + Steve in-hand on upload). Kind variants / polish still planned.
