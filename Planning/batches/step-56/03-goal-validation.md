# Step 56.03 — Goal validation

**Step:** 56 · **Repo:** SF

## Goal

Central `WarGoalValidator` used at declare time so invalid wars are rejected before creation.

## Rules (locked)

| Goal | Validates |
|------|-----------|
| `de_jure_annex` | Attacker rank ≥ title rank; partial de jure control; **no settlements** in target region |
| `subjugate` | Valid target faction; settlements present OR explicit subjugate intent |
| `transfer_subject` | Subject exists; ticket target overlord change plausible (configurable strictness in tests) |

- De jure rank gate: kingdom → kingdom max; county → county only.
- Settlement check: any `settlements[]` / faction capital in title provinces blocks annex.

## Scope

- [x] `WarGoalValidator` service (`War/validation/`)
- [x] `WarDeclareRequest` + `WarValidationResult` types
- [x] Player-facing error messages (why declare failed)
- [x] Integration hook documented on `WarGoalValidator` (wire in **56.05**)

## Files

| File | Role |
|------|------|
| `War/validation/WarGoalValidator.java` | Validates all three v2 goals |
| `War/validation/WarDeclareRequest.java` | Declare input DTO |
| `War/validation/WarValidationResult.java` | ok / fail + message |
| `src/test/java/.../WarGoalValidatorTest.java` | Unit tests |

## Verify

- [x] Unit tests: annex blocked when settlement in region
- [x] Unit tests: county cannot de jure war on kingdom title
- [x] Unit tests: subjugate allowed when settlement present
- [x] Unit tests: transfer_subject requires defender as overlord

## Status

**Done** (2026-08-19). **Next batch:** [56.04 — Persistence](./04-persistence.md).
