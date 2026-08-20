# Step 44.01 — Planning lock (war map layer + SF contract)

**Status:** **Done** (2026-08-19)  
**Authoritative spec:** [simplefactions/Documentation/Wars.md](../../../../simplefactions/Documentation/Wars.md) (planning lock v1.0)

## Goal

Lock the SimpleFactions automated war system and the **map export contract** so SF implementation phases and PS map-layer batches can proceed without re-litigating design.

## Locked decisions (summary)

| Area | Lock |
|------|------|
| Declaration | Ticket → code in-game (**step 68**); test declare without code in steps 56–67 |
| Goals | One war = one goal: `de_jure_annex` (no settlements in region), `subjugate`, `transfer_subject` — no generic conquest goal |
| Objective | Single **objective province** per target; capital > largest settlement > geometric center |
| Route | Border-first start; priority land → sea → land+neutral; new `ProvincePathfinder` |
| Occupation | Per-battle province adds (bulge front); export `occupied_by_*` for web tint — **do not infer from territory diffs** |
| Initiative | 4 per side; offensive spends per fought battle; postpone does not spend |
| Attacker at 0 init | Defender: white peace **or** counter-push; unreachable capital → auto white peace |
| Reparations | **Attacker only** on surrender or capital loss; % main guild ledger income for X days |
| Voting | `min(attacker_votes, defender_votes)` per hour; tie → earliest; autoresolve only if both leaders agree |
| Militia | Own faction land only; overlord militia not in vassal land |
| Raid war type | One battle, border distance limit, no occupation tint |
| Inter-battle raids | Naval/air/fort between campaign battles (not a war type) |

## Map export (PS)

Schema: [`map-export-schema.json`](../../assets/map-export-schema.json) — `$defs/war` extended with occupation, campaign, initiative, objective fields.

**PS rule:** Frontline/occupation overlay reads **only** from SF `wars[]` export. No territory-diff inference.

## Implementation phases

See [Wars.md § Implementation phases](../../../../simplefactions/Documentation/Wars.md#implementation-phases). Step-44 PS batches align with **P9** (export + FE tint). SF phases **P1–P8** precede full map layer.

## Batches after this lock

| # | Batch | Repo | Depends on |
|---|-------|------|------------|
| — | SF P1–P8 | SF | This lock |
| 02 | SF war export | SF | SF P3+ (occupation in export) |
| 03 | PS war compile / tint | PS | 02 |
| 04 | FE war mode overlay | PS FE | 03 |
| 05 | Docs + STAGING | Both | 04 |

## Checklist

- [x] Full war system spec in `simplefactions/Documentation/Wars.md`
- [x] `map-export-schema.json` war `$defs` updated
- [x] step-44/00-index.md references lock + phases
- [ ] STAGING Step 44 operator checklist (batch 05)
- [ ] SF phase/batch index (when P1 batch files created)
