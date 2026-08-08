# Batch 8.05 — Deferred reload + applied ack

**Plan + build:** Queue ItemsAdder reload when safe; then `POST /skins/plugin/applied`.

**Repos:** `Workspace/armourshop`

**Depends on:** [04-shop-and-lp](./04-shop-and-lp.md)

## Plan

1. After pack + shop + LP succeed, mark submission pending reload (in-memory or small state file).
2. When `onlineCount == 0` or on server restart/enable → run IA reload/rebuild (document exact command/API used on TFMC).
3. On successful reload for those ids → `POST /skins/plugin/applied` with `{ "submission_ids": [...] }`.
4. Prefer **ack after reload**, not after file write alone.
5. Failures / skipped bow kinds: leave unacked so next poll retries (or stays pending until 07); log clearly.

## Build

| File | Action |
|------|--------|
| Reload queue / listener | empty-server + restart hooks |
| `ProvinceSystemClient` | `POST /plugin/applied` |
| Apply pipeline | wire ack after reload |

## Verify

**IA command on TFMC:** console `iazip` (reload configs + regenerate resourcepack). Ack on `ItemsAdderPackCompressedEvent`.

```bash
cd Workspace/armourshop
mvn -DskipTests package
```

- [x] `ProvinceSystemClient.markApplied`  
- [x] `PendingReloadQueue` + `DeferredIaReloadService` (`iazip`, empty/enable, pack-compressed ack)  
- [x] Pack pull enqueues only shop+LP success; enable flush  
- [ ] In game: approve → pull → files exist → (empty server or restart) reload → id leaves approved list  
- [ ] IA custom item resolvable; player can open shop and apply  

**Implemented:** deferred `iazip` + `POST /plugin/applied` after pack compress; queue file `pending-reload.yml`.

## Out of scope

Tuning grip `display`; bow writers (07); `item_3d` / `shield`.
