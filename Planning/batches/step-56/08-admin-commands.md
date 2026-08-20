# Step 56.08 — Admin commands

**Step:** 56 · **Repo:** SF

## Goal

Fix broken admin tooling and add debug visibility for War v2.

## Scope

- [x] Fix `/faction endwar <id>`: assign `warId = Integer.parseInt(args[1])`
- [x] `/faction warlist` shows v2 fields: goal, status, leaders
- [x] Admin: `/faction warstatus <id>` — JSON-ish summary (initiative stub null, objective TBD)
- [x] Permission: admin only for endwar (unchanged)

## Verify

- [ ] Manual: `endwar 3` ends war id 3, not 0
- [ ] Manual: War list shows active wars after restart

## Status

**Done** (2026-08-19). **Next batch:** [56.09 — Docs verify](./09-docs-verify.md).
