# Step 31.06 — Discord drink review

**Repos:** `tfmc_bot` (`drinksreview` cog)

## Goal

Staff review drink submissions in Discord with one Approve/Deny.

## Plan

1. Poll drink pending via `GET /drinks/staff/pending`.
2. Embed: names, ingredients, brew steps, effects, alcohol/difficulty, texture yes/no.
3. Attach review sheet: custom texture PNG and/or recoloured base potion for color-only (`GET /drinks/submissions/{id}/review-sheet`).
4. Approve/Deny → PS; player DMs (reuse notify outbox; ack approved/denied without double DM).
5. Config channel: reuse `#bot-feed`.

## Verify

- Color-only and textured submissions appear.  
- Deny with reason DMs player.  
- Approve moves status correctly (`approved` or `pending_pack`).

## Done when

E2E review works on staging Discord.

## Status

**Done** (implementation):

- PS: [`drink_review_sheet.py`](../../../backend/src/skins/drink_review_sheet.py) + staff `GET /drinks/submissions/{id}/review-sheet`
- Bot: [`tfmc_bot/drinksreview/`](../../../../tfmc_bot/drinksreview/) — poll, embed, Approve/Deny, DMs, `/drinksreview ping|pending|post`
- Deploy: copy cog + `config.yml` (same feed channel as skins), load + slash sync
