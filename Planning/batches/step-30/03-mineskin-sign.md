# Batch 30.03 — MineSkin sign + PNG rules

**Plan + build:** On Save, turn 64×64 PNG into signed Mojang texture data.

**Repos:** `ProvinceSystem/backend`  
**Depends on:** [02-data-model-api](./02-data-model-api.md)

## Ops

- Free MineSkin API key in gitignored `backend/.env` as `MINESKIN_API_KEY` (see `.env.example`).
- Loaded via `python-dotenv` in `server.py` + `wardrobe_sign.py`.
- Never commit the real key.

## Flow (Save)

1. Accept multipart PNG.
2. Validate **exactly 64×64** (reject otherwise with clear 400).
3. Detect **slim vs classic** from arm pixels.
4. `POST` MineSkin **v2/queue** with file + variant + `visibility=private`; poll job until complete/fail.
5. Persist `texture_value`, `texture_signature`, `model`, PNG asset (only after sign succeeds).
6. Response: `signed: true` (or 502/429/503).

## Verify

- [x] Non-64×64 rejected before MineSkin  
- [x] Valid PNG path stores value+signature (`signed: true`) when key set  
- [x] Rate-limit → 429 friendly message  
- [x] Key missing → 503 + warning log (no key in logs)  

## Status

**Done.** Next: [04-ranks-platform-catalog](./04-ranks-platform-catalog.md).
