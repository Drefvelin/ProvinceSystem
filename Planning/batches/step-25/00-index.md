# Step 25 — Kit customise submit + deny UX

**Repos:** `ProvinceSystem` · `frontend`  
**Depends on:** Step 23 kit editor polish ([step-23](../step-23/00-index.md))  
**Playbook:** [14-character-creator.md](../../14-character-creator.md)

## Goal

Polish kit item customise UX: **Submit item** CTA, success copy (5 minutes + Discord DM; approval when uploading), styled file pickers; on skin deny mark the whole customise as **denied** while keeping name/lore so the player must re-choose a skin.

## Locked rules

| Piece | Choice |
|-------|--------|
| Primary CTA | **Submit item** / **Submitting…** |
| Success (pick) | Submitted; up to 5 minutes; Discord DM when kit ready to claim |
| Success (upload) | Same + custom skin needs staff approval |
| File inputs | Skins-upload `file:` chip + Selected filename |
| Skin deny | Customise → `denied` (not ready); keep name/lore/colours; keep submission_id for status/reason |
| Resubmit after deny | New skin required (upload or pick) |

## Suggested build order

1. **[01-deny-customise](./01-deny-customise.md)** — BE denied state + resubmit requires skin  
2. **[02-editor-ux](./02-editor-ux.md)** — FE Submit item / copy / file chips / denied banner  
3. **[03-docs-verify](./03-docs-verify.md)** — Hubs + STAGING  

## Checkpoint

```text
Submit item → pick/upload success copy
  → deny skin → customise denied (name/lore kept)
  → resubmit needs new skin → pending/ready
```

**Done when:** Locked UX + deny behaviour shipped; docs closed.

## Status

**25.01–25.03 done.** Operator [STAGING](../../../STAGING.md) Step 25 when ready; Phase 4 wardrobe as capacity allows.
