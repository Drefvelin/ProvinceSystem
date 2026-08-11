# Implementation batches

Each batch is **one plan + one build**: small enough to finish and verify before the next.

| Batch | Step | Title | Done when |
|-------|------|-------|-----------|
| [step-2/00-index](./step-2/00-index.md) | 2 | Skins API overview | — |
| [step-2/01–08](./step-2/00-index.md) | 2 | Data → smoke | Step 2 checkpoint green |
| [step-3/00-index](./step-3/00-index.md) | 3 | Shell + skins UI overview | — |
| [step-3/01-shell-and-hub](./step-3/01-shell-and-hub.md) | 3 | Shell, hub, nav | `/` hub; Map/Skins; r3b1rth unlisted |
| [step-3/02-skins-redeem](./step-3/02-skins-redeem.md) | 3 | Redeem + session | Code → session in browser |
| [step-3/03-skins-upload](./step-3/03-skins-upload.md) | 3 | Kind forms + upload | Armor / large+grip submit OK |
| [step-3/04-skins-status-verify](./step-3/04-skins-status-verify.md) | 3 | Status + verify | Browser checklist green |
| [step-4/00-index](./step-4/00-index.md) | 4 | Discord skins review overview | — |
| [step-4/01-staff-pending-api](./step-4/01-staff-pending-api.md) | 4 | Staff pending + file GET | curl pending + PNG |
| [step-4/02-cog-scaffold](./step-4/02-cog-scaffold.md) | 4 | Red cog scaffold | Cog loads on Red/AMP |
| [step-4/03-post-raw-files](./step-4/03-post-raw-files.md) | 4 | Embed + raw PNG attach | Message in `#bot-feed` |
| [step-4/04-approve-deny](./step-4/04-approve-deny.md) | 4 | Buttons + deny modal | API status matches Discord |
| [step-4/05-auto-intake-verify](./step-4/05-auto-intake-verify.md) | 4 | Poll + AMP verify | E2E local API + TFMC Discord |
| [step-5/00-index](./step-5/00-index.md) | 5 | Discord link + player DMs overview | — |
| [step-5/01-link-api](./step-5/01-link-api.md) | 5 | Link start/complete API | curl start → complete |
| [step-5/02-submit-and-notify](./step-5/02-submit-and-notify.md) | 5 | Require link + submitted outbox | Upload gated; notify GET/ack |
| [step-5/03-cog-link-and-dms](./step-5/03-cog-link-and-dms.md) | 5 | `/linkdiscord` + DMs | Link + submitted/approve/deny DMs |
| [step-5/04-armourshop-linkdiscord](./step-5/04-armourshop-linkdiscord.md) | 5 | MC `/linkdiscord` | In-game code → Discord complete |
| [step-5/05-e2e-verify](./step-5/05-e2e-verify.md) | 5 | Smoke + staging | Checkpoint green |
| [step-6/00-index](./step-6/00-index.md) | 6 | In-game skins token overview | — |
| [step-6/01-chat-and-api-client](./step-6/01-chat-and-api-client.md) | 6 | Click-to-copy + codes client | `/linkdiscord` copies |
| [step-6/02-token-command](./step-6/02-token-command.md) | 6 | `/armourshop token create` + tab | Mint + redeem on site |
| [step-6/03-docs-verify](./step-6/03-docs-verify.md) | 6 | Staging checklist | Checkpoint green |
| [step-7/00-index](./step-7/00-index.md) | 7 | Pack writer overview | — |
| [step-7/01-scaffold](./step-7/01-scaffold.md) | 7 | `tfmc_submissions` scaffold + paths | Namespace + config keys |
| [step-7/02-armor-writer](./step-7/02-armor-writer.md) | 7 | `armor_set` writer | Fixture armor YAML+PNGs |
| [step-7/03-flat-item-writers](./step-7/03-flat-item-writers.md) | 7 | `item` + `handheld` | `generate: true` + parent |
| [step-7/04-grip-templates](./step-7/04-grip-templates.md) | 7 | Grip JSONs + `large_handheld` | `generate: false` + templates |
| [step-7/05-harness-verify](./step-7/05-harness-verify.md) | 7 | Fixture harness | All four kinds on disk |
| [step-7/06-docs](./step-7/06-docs.md) | 7 | Docs + dry-run | Checklist green |
| [step-8/00-index](./step-8/00-index.md) | 8 | Plugin integrate overview | — |
| [step-8/01-base-set-api](./step-8/01-base-set-api.md) | 8 | `base_set` API | Validate + approved payload |
| [step-8/02-base-set-ui](./step-8/02-base-set-ui.md) | 8 | Tier/type dropdowns | Enabled kinds; filtered `base_set` |
| [step-8/03-pull-and-write](./step-8/03-pull-and-write.md) | 8 | Pull + pack write | Approved → `tfmc_submissions` |
| [step-8/04-shop-and-lp](./step-8/04-shop-and-lp.md) | 8 | Shop YAML + LP | `ps_armor`/`ps_items` + permission |
| [step-8/05-reload-and-ack](./step-8/05-reload-and-ack.md) | 8 | Deferred reload + applied | Ack after IA reload |
| [step-8/06-docs-e2e](./step-8/06-docs-e2e.md) | 8 | Docs + staging E2E | Armor/melee Flow 2 green |
| [step-8/07-bow-crossbow-writers](./step-8/07-bow-crossbow-writers.md) | 8 | Bow / crossbow writers | Harness + apply for bow kinds |
| [step-9/00-index](./step-9/00-index.md) | 9 | Name colour / encoding / web | Gradient + Apply name |
| [step-10/00-index](./step-10/00-index.md) | 10 | Player key / delete / bot names | Prefixed slug + staff delete |
| [step-11/00-index](./step-11/00-index.md) | 11 | IGN ids / multi-tier armor | Human ids + tier packs |
| [step-12/00-index](./step-12/00-index.md) | 12 | Staff review sheet + submit UX | One composite sheet; site + bot |
| [step-13/00-index](./step-13/00-index.md) | 13 | Item 3D / shield / helmet 3D | Upload → apply for 3D kinds |
| [step-14/00-index](./step-14/00-index.md) | 14 | Gun skins | carry/reload/aim upload + apply |
| [step-15/00-index](./step-15/00-index.md) | 15 | Gun IA ids | GaG `ia.…`; no CMD dual-write |
| [step-16/00-index](./step-16/00-index.md) | 16 | Upload 3D model preview | JSON+PNG WebGL viewer on `/skins` |
| [step-17/00-index](./step-17/00-index.md) | 17 | TFMCWeb identity + Discord gate | **17.01–17.08 done**; tick staging [08](./step-17/08-docs-verify.md) |
| [step-18/00-index](./step-18/00-index.md) | 18 | Staff skins → `tfmc_armorshop` | **18.01–18.07 done**; tick staging [06](./step-18/06-docs-verify.md) / [STAGING](../../STAGING.md) |
| [step-19/00-index](./step-19/00-index.md) | 19 | Web character creator (Phase 1) | **19.01–19.06 done**; staging verified |
| [step-20/00-index](./step-20/00-index.md) | 20 | Starter kits in RPCharacters (Phase 2) | **20.01–20.03 done**; claim cutover [21.06](./step-21/06-kit-claim-command.md) |
| [step-21/00-index](./step-21/00-index.md) | 21 | Kits + lore customise (Phase 3) | **done** (21.01–04 + 06–09 + 05; 07 superseded) |

**Repos:** Step 2–3 ProvinceSystem; Step 4 = Discord review; Step 5 = Discord link + DMs; Step 6 = token mint; Step 7 = pack writer; Step 8 = live apply (`base_set` → shop); Step 13 = 3D kinds; Step 14 = guns; Step 15 = GaG IA; Step 16 = upload model preview; Step 17 = TFMCWeb; Step 18 = staff curated skins; Step 19 = character creator Phase 1; Step 20 = starter kits; Step 21 = lore-item + kit claim.

**Later:** Phase 4 character skins; SimpleFactions via TFMCWeb; migrate legacy `tfmc_armor` if desired.

Parent playbook: [../README.md](../README.md) · TFMCWeb: [../13-tfmcweb.md](../13-tfmcweb.md) · Characters: [../14-character-creator.md](../14-character-creator.md) · Checklist: [../08-implementation-checklist.md](../08-implementation-checklist.md)
