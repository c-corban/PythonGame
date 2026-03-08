# Assets and licensing

This file centralizes the currently known asset sources, attribution notes, and license hints for the prototype.

## How to read this file

- **Current assets** = assets that are referenced by the current repository and runtime.
- **Research/backlog assets** = links collected for possible future use, not proof of current use.
- When local notes and source pages disagree, the discrepancy is called out explicitly instead of being silently “fixed.”

Raw supporting material still lives in:

- `credits/`
- `reference/LICENSE-CC-BY-3.0.txt`
- `reference/LICENSE-CC-BY-4.0.txt`
- `reference/LICENSE-OGA-BY-3.0.txt`
- `reference/sprites.txt`

The runtime asset catalog in `src/better_together_shared/asset_catalog.py` now records logical asset IDs, preferred build inputs, and client/server bundle targets. Canonical checked-in master art now lives under `assets/source/`, while generated runtime bundles live under the package-local `src/better_together_client/Images/` and `src/better_together_server/Images/` trees. The client bundle keeps the visual runtime art, while the server bundle may intentionally store collision-oriented mask variants for assets that are never rendered headlessly. Treat the catalog plus `assets/source/` as the runtime packaging source of truth, and treat this document as the attribution/source-notes source of truth.

## Current assets

| Asset | Used for | Source | Attribution / creator | License notes | Evidence |
| --- | --- | --- | --- | --- | --- |
| Aim | Aim reticle shown during cannon aiming | <https://opengameart.org/content/aim> | `oglsdl` | Source page lists **CC0** | `credits/Aim by oglsdl.txt`, source page fetch |
| Black Sail Ship - Bleed's Game Art | Pirate ship sprites referenced by the runtime and bundled with the split client package | <https://opengameart.org/content/black-sail-ship-bleeds-game-art> | `Bleed` | Source page fetch clearly exposes attribution text (`Credit is Optional. You can use: "Bleed - http://remusprites.carbonmade.com/"`), but the license field was not captured cleanly in the fetched snapshot. Re-check the source page directly before external redistribution. Canonical checked-in ship masters now live under `assets/source/ships/black-sail/`. | `credits/Black Sail Ship by Bleed's Game Art.txt`, source page fetch |
| Cannonball | Cannonball icon / projectile art | <https://opengameart.org/content/cannonball> | Source page currently lists `Flixberry Entertainment` | Source page lists **CC-BY 4.0** and **CC0** and says credit is optional. **Note:** the local credit file names `DanSevenstar.xyz`, so this asset should be re-verified if you need publication-grade attribution. | `credits/Cannonball by Dan Sevenstar -DontMind8-.txt`, source page fetch |
| Sailors & Pirates | Crew sprites in the generated client/server runtime bundles | <https://opengameart.org/content/sailors-pirates> | Svetlana Kushnariova (Cabbit) and Jordan Irwin (AntumDeluge) | Local/source notes list **OGA BY 3.0 or later** and **CC BY 3.0 or later**. Preserve the attribution note for Svetlana Kushnariova and include `lana-chan@yandex.ru` when required. Canonical checked-in crew masters now live under `assets/source/players/48x64/`. | `credits/Sailors & Pirates by Svetlana Kushnariova & Jordan Irwin.txt`, source page fetch, `reference/LICENSE-*.txt` |
| Wood Plank Icon | Wood inventory icon in the client HUD | <https://opengameart.org/content/wood-plank-icon> | `weirdybeardyman` | Source page lists **CC0** | `credits/Wood plank by weirdybeardyman.txt`, source page fetch |
| [LPC] Wooden ship tiles | Ship/deck-related art used by the prototype | <https://opengameart.org/content/lpc-wooden-ship-tiles> | Attribution notice credits Tuomo Untinen; local notes also mention Reemax and AntumDeluge around the submission/edit history | Source page fetch shows **CC-BY 3.0** and **CC-BY-SA 3.0** on the pack page. Local notes also clarify that the preview image includes separate water art and that the ship tiles themselves are attributed to Tuomo Untinen. | `credits/Wooden ship tiles by Tuomo Untinen.txt`, source page fetch |

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

## Known follow-ups

1. Reconcile the cannonball attribution mismatch between the local credit file and the current source page.
2. Re-check the Black Sail Ship source page license field directly if the project needs formal redistribution-ready attribution records.
3. Remember that the split client/server packages now ship different asset subsets: the client bundle carries the full art set, while the server bundle only needs the assets used by collision and AI movement.
4. Some server runtime assets are now generated as simplified collision masks rather than full-color render art. That is an intentional optimization, not a missing-asset bug.
5. If new assets are added, update this file and add or adjust the matching file in `credits/`.
6. If an asset’s preferred build input changes in `src/better_together_shared/asset_catalog.py`, review this file to make sure the attribution/source note still describes the surviving canonical source correctly.
