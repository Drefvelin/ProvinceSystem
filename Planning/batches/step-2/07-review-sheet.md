# Batch 2.07 — Review sheet (2D contact PNG)

**Plan + build:** Staff-key endpoint returns one PNG contact sheet for a submission so Discord (later) can attach it. 2D only — no 3D bake yet.

Parent design: [../../05-skins-system.md](../../05-skins-system.md) (Review preview), [../../11-discord-bot.md](../../11-discord-bot.md).

## Plan

1. `GET /skins/submissions/{id}/review-sheet` — header `X-Staff-Key` → `image/png`.
2. Layout:
   - `armor_set`: six labeled tiles (icons + layers) on one sheet.
   - `item` / `handheld` / `large_handheld`: texture tile plus caption text for kind and `grip_preset` when set.
3. 404 if submission missing; 401 without staff key.
4. Document that Discord cog will fetch this URL and attach the file (no WebGL in Discord).

## Build

| File | Action |
|------|--------|
| `skins/review_sheet.py` (or under `storage`) | compose PNG (Pillow or similar — add dep if needed) |
| `skins_routes.py` | staff GET route returning `Response(content=…, media_type=image/png)` |

## Verify

```bash
curl -o sheet.png http://localhost:8000/skins/submissions/$ID/review-sheet \
  -H "X-Staff-Key: $STAFF_KEY"
```

- [ ] Armor submission → sheet with six tiles  
- [ ] Large handheld → sheet shows texture + grip caption  
- [ ] Missing staff key → 401  

## Out of scope

Discord cog, interactive site viewer, 3D multi-view / shield blocking bake (Track B4).
