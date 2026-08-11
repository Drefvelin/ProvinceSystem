# Batch 21.05 — Docs + staging verify (Phase 3)

**Status:** **Implemented** (hubs + STAGING Code lines closed; operator ticks remain unchecked).

**Depends on:** 21.01–21.04, 21.06–21.07 (historical), and **21.08–21.09**

## Hubs updated when closing

| Doc | Change |
|-----|--------|
| [14-character-creator.md](../../14-character-creator.md) | Phase 2 multi-kit claim + Phase 3 character kits UI **implemented** |
| [03-roadmap.md](../../03-roadmap.md) | E3 / Step 21 code+docs done; tick staging |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | Step 21 done; next staging / Phase 4 |
| [batches/README.md](../README.md) | step-21 row done |
| This step `00-index` | Status **21.01–21.09 + 05 done** (note 07 superseded) |
| [STAGING.md](../../../STAGING.md) | Step 20–21 Code lines for kits.yml + character kits UI; leave operator `- [ ]` |
| [AgentHandoff.md](../../../../Documentation/Agent/AgentHandoff.md) | Phase 3 code+docs done; next staging / Phase 4 |

## Staging checklist (operator, unchecked)

- [ ] `kits.yml` loaded; `/rpcharacter kit <id>` claims; join does not auto-grant
- [ ] Per-kit cooldown from config; once-per-character enforced for starter
- [ ] Web: ALIVE character → Kits → starter → Edit knife (not create wizard)
- [ ] Non-editable items listed without Edit
- [ ] Claimed once-per-character kit cannot be customised
- [ ] `pending_skin` blocks that kit’s claim; approve → claim delivers skin + lore
- [ ] No staff / `tfmc_armorshop` path for knife

Also mirrored under [STAGING.md](../../../STAGING.md).

## Out of scope

Phase 4 wardrobe; claiming staging green without human ticks.
