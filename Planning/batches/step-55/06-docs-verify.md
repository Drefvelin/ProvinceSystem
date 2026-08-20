# Step 55.06 — Docs and verify

**Repos:** `simplefactions` · `ProvinceSystem` (planning only)

## Docs

| File | Update |
|------|--------|
| [`Installations.md`](../../../../simplefactions/Documentation/Installations.md) | Upkeep, construction queue, GUI, confirm deconstruct, payment rules |
| [08-implementation-checklist.md](../../08-implementation-checklist.md) | M5c step-55 |
| [03-roadmap.md](../../03-roadmap.md) | Track H step 55 |
| [01-current-state.md](../../01-current-state.md) | Next build pointer |
| [batches/README.md](../README.md) | step-55 row |
| [step-43/00-index.md](../step-43/00-index.md) | Depends on 55 for operational forts |
| [step-54/01-planning-lock.md](../step-54/01-planning-lock.md) | Out of scope → done in 55 |
| [STAGING.md](../../../STAGING.md) | Operator checklist Step 55 |

## Smoke (operator)

### Construction

- [ ] Construct fort → not on map until timer completes
- [ ] Second construct while building → rejected
- [ ] Queue slot shows time remaining in GUI

### Upkeep

- [ ] Ledger shows Installations expense line
- [ ] Broke faction loses cheapest installation on new day

### GUI / commands

- [ ] Hub slot 32 → installations list
- [ ] Detail → deconstruct → confirm → removed
- [ ] `/faction deconstruct` opens GUI
- [ ] `/faction deconstruct <id>` opens confirm

### Regression

- [ ] Step 54 construct validation (port sea, one per kind per province) still works
- [ ] Province loss still dissolves installations

## Tests

- [x] `mvn -q package -DskipTests` (simplefactions)

## Status

**Done** (2026-08-19).

## Next

[step-43](../step-43/00-index.md) — fort ZOC overlay (operational forts only).
