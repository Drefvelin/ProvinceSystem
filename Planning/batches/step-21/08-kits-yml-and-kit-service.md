# Batch 21.08 — kits.yml + KitService (generic multi-kit)

**Plan + build:** Replace starter-hardcoded grant with configurable kits. Rename service/command surface to kit-id based. Per-kit cooldown and once-per-character from YAML.

**Repos:** `Workspace/rpcharacters` · ProvinceSystem roster/kit meta as needed  
**Depends on:** [06](./06-kit-claim-command.md) claim plumbing  
**Supersedes:** Starter-only naming in 06; single global `kit.yml` cooldown shape from step-20

## Locked

| Piece | Choice |
|-------|--------|
| File | `plugins/RPCharacters/kits.yml` (migrate from `kit.yml`) |
| Service | `KitService` (retire `StarterKitService` name) |
| Command | `/rpcharacter kit <kitId>` (e.g. `starter`); tab-complete kit ids |
| Per kit | `cooldown-hours` (player × kit); `once-per-character: true|false` |
| Starter defaults | `once-per-character: true`, `cooldown-hours: 48`, current item list + knife `editable` |
| Repeatable kits | `once-per-character: false` → claim again after that kit’s cooldown expires |
| Persistence | Per character per kit: claim status (`eligible` / `granted` / …); per player per kit: `last_claim_at` |
| Pending gate | Before claim: if any customise for that kit+character is `pending_skin`, abort with reason |
| Ready | Pull/apply customise for that kit then grant items |
| Messaging | Command feedback only; no tip nudges |

### Illustrative `kits.yml`

```yaml
kits:
  starter:
    display-name: Starter
    cooldown-hours: 48
    once-per-character: true
    items:
      - path: m.tools.IRON_HUNTING_KNIFE
        amount: 1
        editable:
          skin-png: knife_skin
          base-set: knives
      - path: m.currency.GOLD_COIN
        amount: 32
      # … churro, boat, book, bundle, bed
  # example future kit:
  # season_pass:
  #   cooldown-hours: 168
  #   once-per-character: false
  #   items: [...]
```

## Plan

1. Load `kits.yml`; migrate/ship default `starter` from current `kit.yml`.
2. Refactor `StarterKitService` → `KitService.tryClaim(player, kitId)`.
3. Character kit status map keyed by kit id (not a single global `kit_status` if that blocks multi-kit — prefer per-kit fields on character + roster sync).
4. Player cooldown stamps keyed by kit id.
5. Wire claim-status / pending_skin checks to **kit id**.
6. Update CommandManager + tab complete for kit ids.
7. Push kit definitions + per-character kit states + per-kit cooldown remaining in catalog/roster sync for the web (full payload shape finished in 09 if needed).

## Status

**Implemented** (RPC `kits.yml` + `KitService`; PS claim-status `kit_id`; catalog `kits` + roster maps).

## Verify

- [x] `/rpcharacter kit starter` claims once per character; second claim rejected *(code path)*
- [x] Per-kit cooldown independent of other kits *(player × kit id stamps)*
- [x] Repeatable kit (`once-per-character: false`) claimable again after cooldown *(status stays eligible)*
- [x] `pending_skin` scoped by kit editable keys via claim-status `kit_id`
- [x] No `StarterKit*` public API left; no auto-grant on join

## Out of scope

Web character kits UI (09); 05 docs.
