# Step 63 — War end closure

**Repo:** SF · [war-build-order.md](../../war-build-order.md)  
**Depends on:** [62](../step-62/00-index.md) (campaign capability shipped) · **Next:** [64](../step-64/00-index.md) (forts & sieges)

## Goal

Wars actually **end** with clear chat outcomes. No goal apply or reparations yet.

| In scope | Out of scope (later) |
|----------|----------------------|
| `WarEndReason` cleanup (drop `AUTO_WHITE_PEACE`, `SURRENDER`) | Subjugate / de jure / transfer goal apply |
| Winner-aware end messages | Reparations ledger |
| Surrender button (campaign GUI) | Chronicle / map export hooks |
| Both coalitions cannot mount next offensive → white peace | Declare codes (68) |
| Auto victory: capital loss, failed objective retake | Fort ZOC sieges (64) |

## Batches

| Batch | Doc | Scope |
|-------|-----|--------|
| **63.01** | [01-planning-lock.md](./01-planning-lock.md) | End reasons, detection rules, pipeline, GUI slots |
| **63.02** | [02-resolution-service.md](./02-resolution-service.md) | `WarResolutionService`, reason enum, chat broadcast |
| **63.03** | [03-stalemate-peace.md](./03-stalemate-peace.md) | Neither-can-attack + mutual exhaustion white peace |
| **63.04** | [04-surrender-gui.md](./04-surrender-gui.md) | Surrender button + confirm next to accept peace |
| **63.05** | [05-battle-victory.md](./05-battle-victory.md) | Capital loss + failed retake auto victory |
| **63.06** | [06-pipeline-integration.md](./06-pipeline-integration.md) | Wire all triggers; split recalc vs end on GUI open |
| **63.07** | [07-docs-verify.md](./07-docs-verify.md) | Wars.md + regression tests |

## Status

**Done** — shipped 2026-08-22 (step 63 war end closure).

## Note on build order

Step 63 was previously reserved for forts. **Forts & sieges** move to [step 64](../step-64/00-index.md); former 64+ steps shift by one in [war-build-order.md](../../war-build-order.md).
