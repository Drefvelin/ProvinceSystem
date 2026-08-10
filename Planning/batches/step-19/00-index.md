# Step 19 — Web character creator (Phase 1 of 4)

**Repos:** `Workspace/rpcharacters` · `ProvinceSystem` · `Workspace/tfmcweb` · `frontend`  
**Depends on:** TFMCWeb identity + character token mint ([step-17](../step-17/00-index.md)); prefer Step 17 staging green  
**Playbook:** [14-character-creator.md](../../14-character-creator.md) · identity [13-tfmcweb.md](../../13-tfmcweb.md)

## Goal

Ship **Phase 1**: website character create + manage that mirrors `/rpcharacter create` / menu — stages synced from the server, single-use in-game token → session (Remember me = longer TTL), attribute **point-buy sheet** (12 points, escalating cost), list alive and dead characters. No lore knife, no Mojang skins.

## Locked rules

See [14-character-creator.md](../../14-character-creator.md). Summary:

| Piece | Choice |
|-------|--------|
| Auth | `/token create character` → single-use redeem → Bearer session; default **1h**; Remember me **30d**; **Log out** revokes |
| Attributes | New point-buy stage: 6 stats, pool **12** (spend exactly), max **+2**/stat, cost of *n*-th rank = **n** |
| Sync | RPCharacters PUT creation catalog on reload (+ command); web GET only |
| Truth | Characters live in RPCharacters; API holds sessions + create/list bridge; no direct web→disk writes |
| UI | **Character** nav tab; skins-quality wizard + character list |
| Phases 2–4 | Kit, lore knife, player skins — **out of this step** |

## Suggested build order (Phase 1)

1. **[01-attribute-point-buy](./01-attribute-point-buy.md)** — RPCharacters: replace attributes selection with point-buy sheet (in-game first).
2. **[02-creation-catalog-sync](./02-creation-catalog-sync.md)** — Push stages/options/slot/point-buy formula to ProvinceSystem; public/session GET.
3. **[03-character-session-api](./03-character-session-api.md)** — Implement character redeem (un-501); Remember me TTL; logout/revoke; session auth for Characters routes.
4. **[04-character-ingest](./04-character-ingest.md)** — Create/list API + RPCharacters apply of web-created characters; dead/alive list.
5. **[05-web-character-ui](./05-web-character-ui.md)** — Nav tab, redeem + Remember me + logout, wizard, my characters.
6. **[06-docs-verify](./06-docs-verify.md)** — Docs hubs + STAGING checklist.

**Immediate next action:** tick human staging on live ([STAGING.md](../../../STAGING.md) Step 19 / [06-docs-verify](./06-docs-verify.md)). Phases 2–4 deferred.

## Later phases (not Step 19 builds)

| Phase | Doc anchor | When |
|-------|------------|------|
| 2 | Starter kit in RPC | After Phase 1 live |
| 3 | Ascended lore knife | After kit owner is RPC |
| 4 | Character skin wardrobe | Separate systems work |

## Out of this step

- ConditionalEvents kit migration details beyond noting Phase 2  
- Item `/skins` changes  
- Identity path rename to `/v1/identity/…`  
- Removing in-game `/rpcharacter create`

## Checkpoint

```text
attribute sheet in-game → catalog sync → redeem + Remember me
  → web wizard create → RPC ingest → /character list alive/dead
```

**Done when:** Playbook Phase 1 checkpoint is green on staging.

## Status

**19.01–19.06 done** (Phase 1 code + docs). Tick operator checklist on [STAGING.md](../../../STAGING.md). Next: Phase 2+ later (kit / lore knife / character skins) — not Step 19 builds.
