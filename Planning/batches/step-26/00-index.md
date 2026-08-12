# Step 26 — Kit asset sync + post-submit status

**Repos:** `Workspace/rpcharacters` · `ProvinceSystem` · `frontend`  
**Depends on:** Step 25 kit submit/deny ([step-25](../step-25/00-index.md))  
**Playbook:** [14-character-creator.md](../../14-character-creator.md)

## Goal

Sync RPC `assets/{skin_png}.png` to ProvinceSystem on creation-catalog sync so default kit preview needs no website-side asset config; after kit item submit, redirect to a skins-style status page.

## Locked rules

| Piece | Choice |
|-------|--------|
| Asset ownership | RPC `plugins/RPCharacters/assets/` only |
| Sync trigger | Same as creation catalog (enable, reload, catalog sync) |
| Website store | `backend/assets/kit_skins/{stem}.png` |
| Missing file | Warn + skip; catalog push still succeeds |
| After submit | Status page (character session); not stay on editor |

## Batches

1. **[01-kit-skin-sync](./01-kit-skin-sync.md)** — Plugin PUT + RPC push after catalog — **done**
2. **[02-status-page](./02-status-page.md)** — FE redirect + status UI — **done**
3. **[03-docs-verify](./03-docs-verify.md)** — Hubs + STAGING — **done**

## Status

**Code+docs closed.** Operator ticks remain in [STAGING.md](../../../STAGING.md) Step 26.
