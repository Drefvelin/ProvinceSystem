# Grave Insurance item audit

**Snapshot:** 2026-09-11  
**Scope:** Determine whether RPCharacters' Grave Insurance has a verified texture and acquisition method for a dedicated player-facing wiki page.

## Result

No public item page or link should be added from this snapshot. RPCharacters expects `m.miscellanea.grave_insurance`, but no matching MMOItems definition, texture mapping, or acquisition source was found. The similarly named Insurance Ticket is a different item tied to AngelChest. Using its artwork or Tool Station acquisition for Grave Insurance would conflate distinct item identifiers.

## RPCharacters item and behaviour

- `C:\Users\MSI\Desktop\plugins\RPCharacters\graves.yml:28-32` excludes `m.miscellanea.grave_insurance` from graves, identifies it as the insurance item, says right-clicking recovers the newest grave from anywhere, and sets `consume: true`.
- `C:\Users\MSI\Desktop\plugin-src\rpcharacters\src\main\java\net\tfminecraft\RPCharacters\grave\GraveInsuranceListener.java:31-46` checks the held item through `GraveLoader.isInsuranceItem`, finds the owner's newest grave, recovers it at the player's location, and consumes one item only after successful recovery when consumption is enabled.
- `C:\Users\MSI\Desktop\plugin-src\rpcharacters\src\main\java\net\tfminecraft\RPCharacters\grave\GraveLoader.java:233-237` compares the held item against the configured TLibs path.

## Distinct AngelChest Insurance Ticket

- `C:\Users\MSI\Desktop\plugins\MMOItems\item\utils.yml:267-272` defines `INSURANCE_TICKET` under MMOItems type `UTILS`, names it Insurance Ticket, assigns PAPER with custom model data 8, and explicitly calls it an AngelChest placeholder. Its TLibs path is therefore `m.utils.insurance_ticket`, not `m.miscellanea.grave_insurance`.
- `C:\Users\MSI\Desktop\plugins\MMOItems\crafting-stations\tool-station.yml:537-548` defines the Tool Station entry for that Insurance Ticket. It requires one `POUCH_OF_COINS` and runs `acadmin giveitem insurance-ticket %player% 1`, which identifies the resulting real item as AngelChest content.
- `C:\Users\MSI\Desktop\plugins\ItemsAdder\contents\tfmc_pack\resourcepack\assets\minecraft\models\item\paper.json:36-37` maps PAPER custom model data 8 to `item/miscellaneous/insurance_ticket`.
- `C:\Users\MSI\Desktop\plugins\ItemsAdder\contents\tfmc_pack\resourcepack\assets\minecraft\models\item\miscellaneous\insurance_ticket.json:1-3` maps that model to `item/miscellaneous/insurance_ticket`.
- The corresponding textures are `C:\Users\MSI\Desktop\plugins\ItemsAdder\contents\tfmc_pack\resourcepack\assets\minecraft\textures\item\miscellaneous\insurance_ticket.png` and its mirrored copy at `C:\Users\MSI\Desktop\plugins\ItemsAdder\contents\tfmc_pack\resourcepack\assets\minecraft\textures\tfmc_pack\miscellaneous\insurance_ticket.png`.

## Exhausted locations

Exact searches for `grave_insurance` and `Grave Insurance` covered the live plugin tree excluding generated ItemsAdder caches, all repositories under `C:\Users\MSI\Desktop\plugin-src`, the live MMOItems `item` and `crafting-stations` directories, MMOItems `drops.yml`, and the archived `MMOItems\item.zip`. Only RPCharacters' configured references were found. Filename searches across `ItemsAdder\contents` found no grave-insurance asset; the only insurance asset was the distinct Insurance Ticket above.
