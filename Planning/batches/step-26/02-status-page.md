# Batch 26.02 — Post-submit status page

**Repos:** ProvinceSystem frontend  

## Locked

| Piece | Choice |
|-------|--------|
| Route | `/character/[id]/kits/[kitId]/edit/[kitKey]/status` |
| After submit | `router.push` to status (upload and pick) |

## Done

- Status page loads lore item via `listLoreItems`; skins-style copy for pending_skin / ready / denied / applied
- Refresh status; Back to kit; Edit again when denied
- Editor redirects on successful customise (UI-dev included)

## Status

**Done.**
