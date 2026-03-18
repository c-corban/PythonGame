# Better-Together

A multiplayer co-op pirate-ship prototype built with Python and Pygame.

The repository currently contains a playable local client/server prototype where crew members move around a ship, repair incoming damage, reload and fire cannons, and hand disconnected player slots back to AI. The broader design goal is still the original “organize and prioritize tasks together” concept described in `reference/game-concept.md`.

## Quick start

This project targets Python 3.11 or newer and currently has one runtime dependency: `pygame`.

1. Install Python 3.11 or newer from <https://www.python.org/downloads/>.
2. From the repository root, install the project in editable mode:

```bash
python -m pip install -e .
```

That editable install also installs `pygame` plus the `better-together-server` and `better-together-client` console scripts.

3. Start the server and client with the canonical package entrypoints:

```bash
python -m better_together_server
python -m better_together_client
```

For separate computers, check out the repository on each machine, install it from the repository root, then run only the runtime that machine needs.

On macOS, you can also double-click the repo-root launchers instead of starting both runtimes from a terminal:

- `Launch Better Together Server.command`
- `Launch Better Together Client.command`

Those launchers prefer the local `.venv`, fall back to `python3` / `python`, prepend `src/` to `PYTHONPATH` for raw-checkout launches, and automatically point each runtime at the package-local `.env` file inside `src/better_together_server/` or `src/better_together_client/` when those files exist.

The canonical runtime packages live in the repo-root `src/` tree:

- `src/better_together_client/`
- `src/better_together_server/`
- `src/better_together_shared/`

The editable install also exposes `better-together-server` and `better-together-client`, but the `python -m ...` entrypoints above remain the preferred launch path.

If the client and server will run on different computers, edit `src/better_together_server/.env` on the server machine and `src/better_together_client/.env` on the client machine so the bind/connect host settings match your LAN.

The server runtime is now headless-capable, so it no longer needs to open a Pygame window just to host multiplayer state.

Optional but recommended before larger code changes: use the canonical automated baseline in [`docs/quickstart.md#canonical-automated-baseline`](docs/quickstart.md#canonical-automated-baseline).

If you change the shared asset catalog or any runtime image sources, regenerate the package-local runtime bundles from the repository root:

```bash
python scripts/build_runtime_assets.py
```

If your machine exposes Python as `python3` instead of `python`, substitute that command name.

For full setup notes, launch caveats, and smoke-test steps, see [`docs/quickstart.md`](docs/quickstart.md).

## Documentation

If you're not sure where a fact lives or which document should move with a change, start with [`docs/knowledge-base.md`](docs/knowledge-base.md).

- [`docs/knowledge-base.md`](docs/knowledge-base.md) — map of the live docs, the `.github` customization layer, and update ownership by topic.
- [`docs/quickstart.md`](docs/quickstart.md) — installation, canonical automated baseline, launch order, and local smoke-test flow.
- [`docs/architecture.md`](docs/architecture.md) — client/server boundaries, room lifecycle, transport contract, and runtime caveats.
- [`docs/gameplay-status.md`](docs/gameplay-status.md) — original concept versus the currently implemented prototype.
- [`docs/contributing.md`](docs/contributing.md) — repo map, safe-change guidance, and manual verification checklist.
- [`docs/assets-licenses.md`](docs/assets-licenses.md) — current asset inventory, attribution record, and open follow-up notes.

## Repository map

- `.github/` — workspace-shared Copilot instructions, agents, prompts, and skills for AI-assisted work.
- `AGENTS.md` — quick human-readable map of the workspace-shared Copilot customization layer.
- `src/` — canonical Python package tree containing `better_together_client`, `better_together_server`, and `better_together_shared`.
- `assets/source/` — primary checked-in master art used to regenerate most runtime bundles; a few catalog entries still point at legacy package-local client images until they are migrated.
- `reference/` — concept notes, raw license texts, and an asset wish list / research list.
- `credits/` — one file per currently tracked asset attribution source.
- `docs/` — live project knowledge base for contributors and future AI-assisted work; start with `docs/knowledge-base.md`.

## Current project status

The project vision and the codebase are related but not identical:

- **Vision:** a four-player co-op game about prioritizing tasks under pressure.
- **Current prototype:** a local multiplayer ship-defense loop with movement, repair, cannon use, pirate ship pressure, and AI fallback on disconnect.

See [`docs/gameplay-status.md`](docs/gameplay-status.md) for the detailed gap between the vision and the implementation.

## Assets

Current asset attributions are documented in [`docs/assets-licenses.md`](docs/assets-licenses.md), with raw source notes preserved in `credits/`.

Logical runtime asset IDs now live in `src/better_together_shared/asset_catalog.py`. Most canonical master art now lives under `assets/source/`, while the catalog still builds `ui.aim`, `world.water`, and `world.ship-deck` from legacy files in `src/better_together_client/Images/` until those inputs are migrated. The package-local client/server runtime bundles can be validated or regenerated with `scripts/build_runtime_assets.py`.
