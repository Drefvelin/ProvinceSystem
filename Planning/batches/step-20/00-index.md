# Step 20 — Starter kits in RPCharacters (Phase 2)

**Repos:** `Workspace/rpcharacters` · `ProvinceSystem` · `frontend`  
**Depends on:** Step 19 Phase 1 live ([step-19](../step-19/00-index.md))  
**Playbook:** [14-character-creator.md](../../14-character-creator.md) Phase 2

## Goal

Move starter kits into RPCharacters (`kit.yml`). Each **character** may receive the kit **once**; **48h** per-player cooldown between successful grants. Sync cooldown / kit status to the website.

**Product amendment (post 20.03 / 21.06):** Kits are generic (`kits.yml` + `KitService`); claim `/rpcharacter kit <id>`; per-kit cooldown. Web customise is character → Kits ([21.08](../step-21/08-kits-yml-and-kit-service.md) / [21.09](../step-21/09-kits-web-character-ui.md)). Playbook Phase 2–3 is product truth.

**Not in this step:** lore-item editor, ArmourShop skin apply for knife customisation, NBT preview UI (Phase 3 / step-21).

## Locked rules (as shipped in 20.01–20.03)

Historical build target; superseded by playbook claim rules + 21.06:

| Piece | Choice (shipped) |
|-------|------------------|
| Config | `plugins/RPCharacters/kit.yml` |
| Per character | Kit at most once |
| Per player | 48h between successful grants |
| Triggers (shipped) | Join; plugin reload (online + active character) |
| Create on cooldown (shipped) | Character **ineligible** (permanent) + create warnings |
| CE `/tfmc starter` | Cut over / disable when RPC grant is live |
| `editable` in kit.yml | Schema reserved; used in Phase 3 |

## Suggested build order

1. **[01-kit-yml-and-grant](./01-kit-yml-and-grant.md)** — `kit.yml`, persistence, join/reload grant, CE cutover note.
2. **[02-cooldown-sync-and-warn](./02-cooldown-sync-and-warn.md)** — Push cooldown/eligibility to API; web + in-game create warnings.
3. **[03-docs-verify](./03-docs-verify.md)** — Playbook hubs + STAGING checklist.

## Later

| Phase | What |
|-------|------|
| 3 | Lore-item + **claim command cutover** ([step-21](../step-21/00-index.md)) |
| 4 | Character skin wardrobe |

## Checkpoint (shipped era)

```text
kit.yml → join/reload grant once/character → 48h player cooldown
  → create while cooling down = ineligible + shared warning (web + MC)
```

**Target after 21.06:** `/rpcharacter kit starter` once/character; create anytime; 48h between claims.

## Status

**20.01–20.03 done** (auto-grant era). Next kit work: [step-21/06](../step-21/06-kit-claim-command.md). Operator Step 20 staging boxes still describe the shipped auto-grant path until 21.06 lands (then update STAGING to claim).
