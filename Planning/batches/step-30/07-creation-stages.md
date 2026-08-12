# Batch 30.07 — Creation stages (web / game)

**Plan + build:** Wardrobe as a creation step with platform gating.

**Repos:** `Workspace/rpcharacters` (`stages.yml` + loaders) · `ProvinceSystem/frontend` (wizard) · pending-create wardrobe on PS  
**Depends on:** [04-ranks-platform-catalog](./04-ranks-platform-catalog.md) · [05-web-wardrobe-ui](./05-web-wardrobe-ui.md)

## Stages

### Game-only tip

`creation_wardrobe_info_stage` — `type: info`, `platform: game` — tip to edit on website / `/rpcharacterwardrobe`.

### Web-only wardrobe

`creation_wardrobe_stage` — `type: wardrobe`, `platform: web` — optional draft uploads; signed against pending create after submit; flushed to live wardrobe on apply.

## Verify

- [x] In-game create: tip only, no upload GUI  
- [x] Web create: wardrobe card, no “go to website” tip  
- [x] Skipping uploads still finishes creation  
- [x] After create, skins uploaded to pending flush on apply → join/switch apply  

## Status

**Done.** Next: [08-docs-verify](./08-docs-verify.md).
