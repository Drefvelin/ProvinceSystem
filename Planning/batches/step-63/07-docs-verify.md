# Step 63.07 — Docs & verify

**Repo:** `simplefactions`

## Tasks

1. **`Wars.md`**
   - War end conditions table: single `WHITE_PEACE`; `ATTACKER_VICTORY` / `DEFENDER_VICTORY`.
   - Capital battles: aggressor win at defender capital / defender win at attacker capital.
   - Campaign GUI: surrender slot 47, accept peace slot 48.
   - Failed retake → aggressor victory (update retake loop step 4).
   - Note: goal apply / reparations still future.

2. **`step-62/00-index.md`**
   - Point deferred goal apply to post-63 batch or step 68+ note.

3. **Regression**
   - `mvn test` full suite.
   - Remove `AUTO_WHITE_PEACE` and `SURRENDER` from tests and enum.

4. **Mark step 63 complete** in this index and `war-build-order.md`.

## Done when

All 63.01-63.07 batches implemented and tests green.
