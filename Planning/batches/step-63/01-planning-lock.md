# Step 63.01 — War end closure lock

**Plan + docs only.** Lock end reasons, detection rules, and pipeline before 63.02+ code.

**Repos:** `Workspace/simplefactions`  
**Depends on:** [step 62](../step-62/00-index.md) (shipped) · [Wars.md](../../../../simplefactions/Documentation/Wars.md)

---

## Locked — end reasons (simplified)

Drop `AUTO_WHITE_PEACE`. One peace reason only.

| `WarEndReason` | When | Winner for chat |
|----------------|------|-----------------|
| `WHITE_PEACE` | Mutual exhaustion, both can't attack, accept peace, Hold → accept, walkover dead-end | None |
| `ATTACKER_VICTORY` | Aggressor wins battle at **defender capital**, failed retake at objective, or **defender surrenders** | Attacker coalition |
| `DEFENDER_VICTORY` | Defender wins battle at **attacker capital**, or **attacker surrenders** | Defender coalition |
| `ADMIN_END` | Staff command | None |

Remove `AUTO_WHITE_PEACE` and `SURRENDER` from the enum. No migration or alias handling in `WarMapper` / `fromJson`.

---

## Locked — chat messages (player-facing)

Broadcast to **both coalitions** (all eligible war members online). No em dashes.

| Reason | Message (example) |
|--------|-------------------|
| `WHITE_PEACE` | `The war has ended in white peace.` |
| `ATTACKER_VICTORY` | `The war has ended. The attacker coalition wins.` |
| `DEFENDER_VICTORY` | `The war has ended. The defender coalition wins.` |
| `ADMIN_END` | `The war has ended.` (unchanged) |

Goal names and reparations are **not** mentioned in 63.

---

## Locked — `WarResolutionService` (single funnel)

Replace ad-hoc `WhitePeaceService` → `endWar` calls with one evaluator.

```text
evaluateAndMaybeEnd(war, context):
  1. Victory checks (context or derived state) → ATTACKER_VICTORY / DEFENDER_VICTORY
  2. Offensive stalemate → WHITE_PEACE
  3. WhitePeaceService.recalculateProposals → if both flags → WHITE_PEACE
  4. return empty (war continues)
```

`CampaignChoiceService.recalculateAndMaybeEnd` becomes a thin delegate to this service.

**Do not end the war** when only one coalition auto-proposed white peace (enemy must accept or stalemate must fire).

---

## Locked — offensive stalemate (“both can’t attack”)

When **all** of:

- `postBattleChoicePhase == NONE` (no Push/Hold / Attack/Peace pending)
- `nextBattleProvince(war)` is present
- **Neither** coalition can mount an offensive at that province:

```text
canMountOffensive(war, coalition, provinceId):
  fuel(coalition) >= 1
  AND offensiveRegiments(war, provinceId, coalition) >= 1
```

**Ignore initiative holder** for this check — we ask whether either side *could* fight offensively at the next node if they had the ball.

→ immediate `WHITE_PEACE` (same message as other white peace).

**Not** the same as `canReachTarget` (fuel vs axis distance). Both may be true; stalemate check runs first.

---

## Locked — battle auto-victory (no goal apply)

Detect **after** a campaign battle resolves (real battle, forfeit, or walkover), **before** opening vote — and **skip** Push/Hold when victory ends the war.

### Capital battles (symmetric)

| Battle province | Winner coalition | Result |
|-----------------|------------------|--------|
| **Defender** war leader capital | **AGGRESSOR** | `ATTACKER_VICTORY` — war ends |
| **Defender** war leader capital | **DEFENDER** | War **continues** (capital held) |
| **Attacker** war leader capital | **DEFENDER** | `DEFENDER_VICTORY` — war ends |
| **Attacker** war leader capital | **AGGRESSOR** | War **continues** (capital held) |

No push-target or objective check required for capital battles — province id vs war leader capital is enough.

**Capital as objective:** when `objectiveProvinceId` is the defender capital, an aggressor win at that province is the same row as above (`ATTACKER_VICTORY`). Skip retake loop; do not enter `RETAKE_OBJECTIVE` or winner Push/Hold.

### Failed retake — aggressor wins war

| Condition | End |
|-----------|-----|
| Before battle: `pushTarget == RETAKE_OBJECTIVE` and `objectiveHeldBy == ATTACKER` | |
| Battle at `objectiveProvinceId` | |
| Battle winner coalition == **AGGRESSOR** (defender failed to retake) | `ATTACKER_VICTORY` |

Replaces current behavior of cursor −1 on retake loss (war ends instead).

**Defender wins retake:** objective returns to defender (`RETAKE_OBJECTIVE` push path) — war **continues** (unchanged).

---

## Locked — voluntary surrender (GUI)

| Rule | Detail |
|------|--------|
| Who | **War leader only** (same eligibility as accept white peace) |
| Where | Campaign view slot **47** (red banner), beside accept peace slot **48** |
| Flow | Click → confirm dialog → end war |
| Effect | Surrendering leader's coalition **loses**; opponent gets victory reason |

| Surrendering leader | End reason |
|---------------------|------------|
| Attacker leader | `DEFENDER_VICTORY` |
| Defender leader | `ATTACKER_VICTORY` |

Surrender is not white peace.

---

## Locked — trigger points

| When | Action |
|------|--------|
| After battle outcome + walkover chain | `evaluateAndMaybeEnd` with battle context |
| After post-battle choice resolves + walkover | `evaluateAndMaybeEnd` |
| Opening campaign view | **Recalculate proposals only** — do **not** auto-end (remove surprise end on open) |
| Surrender confirm | End immediately with victory reason |
| Accept white peace (existing) | `WHITE_PEACE` |

---

## Locked — test scenarios

1. Mutual `!canReachTarget` flags → `WHITE_PEACE`.
2. Neither can mount offensive at next node → `WHITE_PEACE`.
3. Aggressor wins battle at defender capital → `ATTACKER_VICTORY`, no Push/Hold.
4. Defender wins battle at defender capital → war continues.
5. Defender wins battle at attacker capital → `DEFENDER_VICTORY`.
6. Aggressor wins battle at attacker capital → war continues.
7. Defender fails retake at objective → `ATTACKER_VICTORY`.
8. Defender wins retake → war continues.
9. Attacker leader surrenders → `DEFENDER_VICTORY`.
10. Defender leader surrenders → `ATTACKER_VICTORY`.
11. Open campaign view with both flags set does **not** end war until leader accepts or stalemate/victory fires elsewhere.

---

## Out of scope (explicit)

- Goal enforcement (subjugate, annex, transfer)
- Reparations
- `Chronicle` / map export `war_ended` payload
- Fort sieges (step 64)
