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

**Repos:** Step 2–3 ProvinceSystem; Step 4 = staff routes + `tfmc_bot`; Step 5 = link API + bot DMs + ArmourShop `/linkdiscord`.

**Later:** ArmourShop IA apply; ban-role mute; review-sheet in Discord.

Parent playbook: [../README.md](../README.md) · Checklist: [../08-implementation-checklist.md](../08-implementation-checklist.md)
