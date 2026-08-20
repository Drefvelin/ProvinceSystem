# Step 56.07 — war_id stubs

**Step:** 56 · **Repo:** SF

## Goal

Introduce `war_id` on military/levy commit structures so later steps can scope casualties without refactors.

## Scope

- [x] `WarCommitment` record (or extend existing): `warId`, `factionId`, `regimentId`, `count`, `committedAt`
- [x] `WarManager.commitForWar(warId, faction)` — no-op or empty commit at declare (full levy logic in step 61)
- [x] Tag wars in API used by battle system later (`getWarId()` on active campaign)

## Verify

- [x] Unit test: commitment record serializes with war id
- [x] New war has retrievable `war_id` for debug command

## Status

**Done** (2026-08-19). **Next batch:** [56.08 — Admin commands](./08-admin-commands.md).
