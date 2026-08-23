# Step 70d.08 — Docs and verify

**Depends on:** 70d.07, [70d.09](./09-siege-chronology.md) (siege chronology fix required before operator sign-off)  
**Status:** **done** (2026-08-23)

## Tasks

1. Update [`Wars.md`](../../../../simplefactions/Documentation/Wars.md) schedule construction: FB legs, axis insertion, naval prepend, no new `NAVAL_INVASION`.
2. Mark step 70d done in [00-index.md](./00-index.md) and [war-build-order.md](../../war-build-order.md).
3. Manual smoke:
   - `/faction warpath <id>` on Brume vs Lantan
   - Campaign GUI row matches geographic order
   - First marker under 709 FB field

## Automated verify

```bash
cd simplefactions && mvn test -Dtest="me.Plugins.SimpleFactions.War.**"
```

- [x] War package tests green (519 run, 0 failures, 0 skipped)

## Manual smoke (operator)

After deploy + plugin reload:

1. **Config** - live `plugins/SimpleFactions/config.yml` has `provinces_between_battles: 3`
2. **Regen** - `/faction warpath <Brume-Lantan war id>` on dev server
3. **Campaign GUI**
   - [ ] Geographic row: `452 - 782 - 672 - [709] - 713 siege - 705`
   - [ ] First-battle marker under border **709** FB field (not siege or capital)
   - [ ] No pagination; no `Counter-push schedule` lore
4. **warstatus / war JSON**
   - [ ] Invasion list: `709 FIELD` → `713 SIEGE` → `705 required` (optional `795 NAVAL` prefix if harbour covers sea)
   - [ ] No invasion slot after **705** (no off-axis Lan_Airfield siege after capital)
   - [ ] No new `NAVAL_INVASION` slots in regenerated schedule
   - [ ] Counter list includes cadence at 672, 782 and required 452

## Done when

- [x] Docs merged
- [ ] Live regen verified on dev server (operator)
