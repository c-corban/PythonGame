# Assets and licensing

This file centralizes the currently known asset sources, attribution notes, and license hints for the prototype, while keeping confirmed current records separate from open follow-up items.

## How to read this file

- **Current assets** = assets that are referenced by the current repository and runtime.
- **Research/backlog assets** = links collected for possible future use, not proof of current use.
- **Open follow-ups** = unresolved attribution or packaging questions that still need confirmation.
- **Maintenance expectations** = routine doc-sync work to do when assets or build inputs change.
- When local notes and source pages disagree, the discrepancy is called out explicitly instead of being silently “fixed.”

Raw supporting material still lives in:

- `credits/`
- `reference/LICENSE-CC-BY-3.0.txt`
- `reference/LICENSE-CC-BY-4.0.txt`
- `reference/LICENSE-OGA-BY-3.0.txt`
- `reference/sprites.txt`

The runtime asset catalog in `src/better_together_shared/asset_catalog.py` now records logical asset IDs, preferred build inputs, and client/server bundle targets. Most checked-in master art now lives under `assets/source/`, while generated runtime bundles live under the package-local `src/better_together_client/Images/` and `src/better_together_server/Images/` trees. A few current catalog entries still build from legacy client package files: `ui.aim`, `world.water`, and `world.ship-deck`. The client bundle keeps the visual runtime art, while the server bundle may intentionally store collision-oriented mask variants for assets that are never rendered headlessly. Treat the catalog as the runtime packaging source of truth, treat `assets/source/` as the primary checked-in master-art tree, and treat this document as the attribution/source-notes source of truth.

## Confirmed current asset record

| Asset | Used for | Source | Attribution / creator | License notes | Evidence |
| --- | --- | --- | --- | --- | --- |
| Aim | Aim reticle shown during cannon aiming | <https://opengameart.org/content/aim> | `oglsdl` | Source page lists **CC0** | `credits/Aim by oglsdl.txt`, source page fetch |
| Black Sail Ship - Bleed's Game Art | Pirate ship sprites referenced by the runtime and bundled with the split client package | <https://opengameart.org/content/black-sail-ship-bleeds-game-art> | `Bleed` | Source page fetch clearly exposes attribution text (`Credit is Optional. You can use: "Bleed - http://remusprites.carbonmade.com/"`). Canonical checked-in ship masters now live under `assets/source/ships/black-sail/`. See the open follow-up section below for the outstanding license-field re-check. | `credits/Black Sail Ship by Bleed's Game Art.txt`, source page fetch |
| Cannonball | Cannonball icon / projectile art | <https://opengameart.org/content/cannonball> | Source page currently lists `Flixberry Entertainment` | Source page lists **CC-BY 4.0** and **CC0** and says credit is optional. See the open follow-up section below for the outstanding creator-name mismatch with the local credit file. | `credits/Cannonball by Dan Sevenstar -DontMind8-.txt`, source page fetch |
| Sailors & Pirates | Crew sprites in the generated client/server runtime bundles | <https://opengameart.org/content/sailors-pirates> | Svetlana Kushnariova (Cabbit) and Jordan Irwin (AntumDeluge) | Local/source notes list **OGA BY 3.0 or later** and **CC BY 3.0 or later**. Preserve the attribution note for Svetlana Kushnariova and include `lana-chan@yandex.ru` when required. Canonical checked-in crew masters now live under `assets/source/players/48x64/`. | `credits/Sailors & Pirates by Svetlana Kushnariova & Jordan Irwin.txt`, source page fetch, `reference/LICENSE-*.txt` |
| Wood Plank Icon | Wood inventory icon in the client HUD | <https://opengameart.org/content/wood-plank-icon> | `weirdybeardyman` | Source page lists **CC0** | `credits/Wood plank by weirdybeardyman.txt`, source page fetch |
| [LPC] Wooden ship tiles | Ship/deck-related art used by the prototype | <https://opengameart.org/content/lpc-wooden-ship-tiles> | Attribution notice credits Tuomo Untinen; local notes also mention Reemax and AntumDeluge around the submission/edit history | Source page fetch shows **CC-BY 3.0** and **CC-BY-SA 3.0** on the pack page. Local notes also clarify that the preview image includes separate water art and that the ship tiles themselves are attributed to Tuomo Untinen. | `credits/Wooden ship tiles by Tuomo Untinen.txt`, source page fetch |

## Runtime asset ID mapping notes

- `ui.aim` currently builds from `src/better_together_client/Images/aim.png`; its attribution is the same OpenGameArt `Aim` record listed above.
- `world.ship-deck` currently builds from `src/better_together_client/Images/ocean_e_new_ship_small.png`; its current attribution trail is the `[LPC] Wooden ship tiles` entry above, including the local note that the ship tiles themselves are made by Tuomo Untinen.
- `world.water` currently builds from `src/better_together_client/Images/water.png`; the best current local provenance trail is the separate water-tile note in `credits/Wooden ship tiles by Tuomo Untinen.txt` (`Water tile by Sharm aka Lanea Zimmerman`). The direct source re-check still appears below as an open follow-up before external redistribution.

## Current runtime packaging caveats

- The split client/server packages now ship different asset subsets: the client bundle carries the full art set, while the server bundle only needs the assets used by collision and AI movement.
- Some server runtime assets are now generated as simplified collision masks rather than full-color render art. That is an intentional optimization, not a missing-asset bug.

## Research / backlog asset list

`reference/sprites.txt` contains a larger list of OpenGameArt links for:

- additional ships,
- treasure chests,
- explosions,
- pirate art packs,
- music,
- sound effects,
- steering wheels,
- and other possible prototype resources.

Treat that file as a **research list**, not as proof that those assets are present in the repository or already cleared for use.

## Open attribution and packaging follow-ups

1. Reconcile the cannonball attribution mismatch between the local credit file and the current source page.
2. Re-check the Black Sail Ship source page license field directly if the project needs formal redistribution-ready attribution records.
3. Re-verify the current `world.water` provenance trail directly if the project needs redistribution-ready attribution records.
4. Migrate the remaining legacy catalog build inputs (`ui.aim`, `world.water`, and `world.ship-deck`) into `assets/source/` or document them as long-term exceptions if they are meant to stay package-local.

## Maintenance expectations

- If new assets are added, update this file and add or adjust the matching file in `credits/`.
- If an asset’s preferred build input changes in `src/better_together_shared/asset_catalog.py`, review this file to make sure the attribution/source note still describes the surviving canonical source correctly.
