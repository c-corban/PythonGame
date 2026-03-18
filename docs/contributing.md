# Contributing

This repository is still prototype-shaped, so the fastest way to help is to understand which changes are low risk, which ones are tightly coupled, and which docs should move with the code.

## Repo map

- `src/` — canonical package tree containing `better_together_client`, `better_together_server`, and `better_together_shared`.
- `assets/source/` — primary checked-in master art used to generate most runtime bundles; a few asset-catalog entries still build from legacy package-local client images.
- `reference/` — historical concept notes, raw license texts, and asset research links.
- `credits/` — asset attribution source notes.
- `docs/` — contributor-facing knowledge base. Start with `docs/knowledge-base.md` when you need the doc map or update-routing guide.
- `.github/` — Copilot instructions, custom agents, prompts, and skills that implement the repo's AI guidance layer.
- `AGENTS.md` — quick human-readable map of the workspace-shared Copilot customization layer.
- `tests/` — lightweight automated checks for startup/config, protocol/transport, client render/session/game-loop helpers, server room/simulation invariants, mirrored asset helpers, and a basic live server flow.

## Change-impact guide

| Area | Risk | Why |
| --- | --- | --- |
| `README.md` and `docs/` | Low | Documentation-only changes do not affect runtime behavior. |
| UI text and prompts in `src/better_together_client/game_loop.py` | Low to medium | Visible behavior changes, but usually no protocol impact. |
| `src/better_together_client/network.py` / `src/better_together_server/network.py` | Medium to high | These modules now own the live socket protocol. |
| `src/better_together_server/game.py` | High | The room model defines the crew slots, pirate ships, and initial room state. |
| `src/better_together_server/room_manager.py` | High | Matchmaking, reconnect behavior, and room cleanup all depend on it. |
| `src/better_together_client/cli.py` / `src/better_together_server/cli.py` / `src/better_together_client/app.py` / `src/better_together_server/app.py` | Medium | These modules front the canonical package entry flow. |
| `src/better_together_shared/protocol.py` | Very high | This file defines the message types and snapshot shape shared by both runtime halves. |
| Client-only gameplay timing or HUD behavior | Medium | Easy to change, but may widen the gap between client-owned and server-owned state. |
| `src/better_together_client/player.py` / `src/better_together_server/player.py` | High | Their field layout still needs to stay compatible with the shared snapshot helpers. |
| `src/better_together_client/assets.py` / `src/better_together_server/assets.py` | High | Both sides rely on mirrored asset-loader behavior. |
| Network protocol or socket behavior | Very high | Client and server must be updated together. |

## Safe first contributions

Good starter improvements include:

- documentation updates,
- clarifying prompts or comments,
- reorganizing asset/license notes,
- small client-side UI polish,
- adding missing architecture notes when you discover a new convention.

## AI-assisted workflows

This repo ships workspace-shared Copilot customizations for the main high-risk change surfaces.

Start with `AGENTS.md` for the quick map of agents, instructions, prompts, and skills, and use `docs/knowledge-base.md` when you need to understand how the `.github` layer fits into the broader repository documentation.

- `.github/copilot-instructions.md` provides always-on repo guidance.
- `.github/instructions/` holds file-targeted guardrails for risky surfaces.
- `.github/agents/` holds specialized multi-file workflows by change surface.
- `.github/skills/` holds on-demand workflows plus supporting references.
- `.github/prompts/` holds narrow repeatable tasks like change triage, doc sync, and regression planning.

Use the most specific customization that matches the task, and still review the matching docs/tests listed below before merging high-risk changes.

## High-risk conventions to preserve

Before changing these, stop and inspect both sides of the client/server split:

1. **Shared snapshot contract** — `src/better_together_shared/protocol.py` defines the message types and player snapshot fields used over the network.
2. **`src/better_together_client/player.py` and `src/better_together_server/player.py` state shape** — networking now uses explicit snapshots, so both classes must still expose compatible fields even though they no longer need matching module names for deserialization.
3. **Mirrored `assets.py` modules** — both sides currently resolve paths and cache images the same way.
4. **Room lifecycle modules** — `src/better_together_server/game.py`, `src/better_together_server/room_manager.py`, and `src/better_together_server/network.py` together define the room model, slot reuse, room creation, and room cleanup.
5. **Entity list shape** — pirate ships live in `Game.pirate_ships`, while `Game.players` remains a compatibility view that still returns crew first and pirate ships after them. Clients still receive those pirate ships through the normal entity reply payload.
6. **Server asset requirement** — the server is now headless-capable, but its collision and AI movement still depend on loading images from the server asset tree.
7. **Asset catalog and bundle builder** — `src/better_together_shared/asset_catalog.py`, `src/better_together_shared/asset_pipeline.py`, `scripts/build_runtime_assets.py`, and `assets/source/` now define the logical asset IDs plus how client/server runtime bundles are generated from preferred master files, with a few temporary legacy build inputs still coming from package-local client images.

## Docs to update when code changes

If you're not sure which document owns a topic, check `docs/knowledge-base.md` first.

When you change these areas, update the matching docs in the same branch:

- setup / run flow → `README.md`, `docs/quickstart.md`
- networking / room behavior → `docs/architecture.md`
- gameplay loop / current feature set → `docs/gameplay-status.md`
- assets / attribution → `docs/assets-licenses.md`, `credits/`

When you change the asset catalog or runtime bundle generation rules, also run `python scripts/build_runtime_assets.py --check` from the repository root and update the docs if the generated layout or source-of-truth expectations changed.

If you change a high-risk area, also review the focused Copilot instruction files in `.github/instructions/` so future AI-assisted edits keep the right guardrails.

## Manual verification checklist

Start with the canonical automated baseline in [`quickstart.md#canonical-automated-baseline`](quickstart.md#canonical-automated-baseline).

Treat `docs/quickstart.md` as the shared source of truth for the baseline commands so this section can stay focused on the change-specific smoke checks below.

Then use this smoke-test flow for runtime changes that touch rendering, input, or networking:

1. Start `python -m better_together_server`.
2. Start `python -m better_together_client`.
3. Confirm the client connects successfully.
4. Move the player around the deck.
5. Confirm cannon and repair prompts appear in the expected zones.
6. Close the client and confirm the server logs the disconnect.

For networking or room-lifecycle changes, also:

1. connect multiple clients,
2. verify new clients reuse AI slots before creating a new room,
3. verify a disconnected slot returns to AI,
4. verify an empty room is deleted.

## Source material versus live docs

`reference/game-concept.md` is valuable project history, but it is not the same thing as the current implementation. Treat the files in `docs/` as the current working knowledge base, use `docs/knowledge-base.md` as the navigation map across docs and `.github`, and treat `reference/` as source/reference material.
