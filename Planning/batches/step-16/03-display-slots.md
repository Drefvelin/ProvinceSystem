# Batch 16.03 — Held view (Steve + thirdperson)

**Repo:** `ProvinceSystem` frontend

Show the uploaded Java item on a Steve mannequin in the same Three.js canvas, using `display.thirdperson_righthand` (API autofill defaults when the tab is missing). Keep a **Model only** toggle for freestanding mesh inspection.

**Depends on:** [02-json-model-render](./02-json-model-render.md)

**Done when:**
- Default preview mode is **In hand**: Steve holds the item with third-person right-hand transform
- Missing `display.thirdperson_righthand` uses the same defaults as backend `display.py`
- **Model only** drops Steve and orbits the centered mesh
- Optional local player-skin PNG for the mannequin (preview only; not submitted)
- Full gui / FP / head slot picker remains a later batch

**Status:** Done.
