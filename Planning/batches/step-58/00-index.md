# Step 58 — Initiative & occupation

**Repo:** SF · **Spec:** [Wars.md](../../../../simplefactions/Documentation/Wars.md) · [01-planning-lock.md](./01-planning-lock.md) · [war-build-order.md](../../war-build-order.md)  
**Depends on:** [57](../step-57/00-index.md) · **Next:** [59](../step-59/00-index.md)

> **Runtime progression superseded by [step 62](../step-62/00-index.md)** (capability model: coalition initiative, Push/Hold + Attack/Peace, symmetric white peace). Shipped 58.03 FSM and 58.05 yellow hold/counter GUI are historical; live code follows [62.01 lock](../step-62/01-campaign-progression-lock.md).

## Goal

Full campaign axis (border cursor in middle), initiative pools, cursor movement, occupation bulge, optional counter-push, white peace proposals, **GUI-first Campaign view**.

## Locked (58.01)

| Topic | Rule |
|-------|------|
| Campaign line | **Attacker capital … B … objective** at declare; `cursorIndex` at border **B** |
| GUI control colors | **De facto** belligerent ownership (not de jure, not occupation bulge) |
| Concrete legend | Blue = us, red = enemy, green = next battle, yellow = choice; no gray/white |
| Counter-push | Optional; leftward on existing axis; **hold** when attacker at 0 initiative |
| White peace | Auto-propose when unreachable; accept or both → auto end |
| Battle placement | **59–63** — first battle at **B**, then every **N** + forts/objective/capital |

## Batches

| Batch | Summary | Status |
|-------|---------|--------|
| [58.01 planning lock](./01-planning-lock.md) | Full axis, GUI spec, FSM, fields, config | **done** (2026-08-20) |
| [58.02 domain model](./02-domain-model.md) | Persistence, full axis in `WarCampaignService`, init at declare | **done** (2026-08-20) |
| [58.03 progression core](./03-progression-core.md) | `CampaignProgressionService` + tests | **done** (2026-08-20) |
| [58.04 occupation zone](./04-occupation-zone.md) | `OccupationService` + tests | **done** (2026-08-20) |
| [58.05 Campaign GUI](./05-campaign-gui.md) | `CampaignView`, `WhitePeaceService`, route renderer | **done** (2026-08-20) |
| [58.06 integration](./06-integration.md) | WarView Campaign button, `warstatus`, regen | **done** (2026-08-20) |
| [58.07 docs verify](./07-docs-verify.md) | Tests + staging checklist | **done** (2026-08-20) |

## Status

**Step 58 complete** (2026-08-20). **Next step:** [59 - Battle scheduling](../step-59/00-index.md).
