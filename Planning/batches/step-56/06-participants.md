# Step 56.06 — Participants

**Step:** 56 · **Repo:** SF

## Goal

Repurpose sides, subjects, and ally call-to-arms for War v2.

## Scope

- [x] `Participant` creation: auto subjects + ally map from `RelationManager`
- [x] `Participant.update(War)` on war view open (sync subjects/allies)
- [x] `WarManager.sendRequest` / `acceptRequest` / `WarRequest` — keep behavior, save after call
- [x] `WarView` / `WarCreator`: remove per-participant multi goal UI; show single war goal on war header
- [x] Remove **Switch sides** war GUI (slot 31); subject rebellion → **movement system** only (2026-08-20)
- [x] Declined ally stability debuff: config stub only (`war.declined_ally_stability_penalty: -30`) — apply in step 62 or small follow-up if time

## Out of scope

- Muster / Warbands button behavior changes → step 60

## Verify

- [ ] Manual: ally call accepted → ally on side, persisted (deferred)
- [x] Manual: `/faction endwar <id>` ends correct war
- [x] Manual: war persists across restart
- [ ] Manual: subjects appear on participant view without manual add

## Status

**Done** (2026-08-19). **Next batch:** [56.07 — war_id stubs](./07-war-id-stubs.md).
