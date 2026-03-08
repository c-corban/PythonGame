# Better-Together

A multiplayer co-op pirate-ship prototype built with Python and Pygame.

The repository currently contains a playable local client/server prototype where crew members move around a ship, repair incoming damage, reload and fire cannons, and hand disconnected player slots back to AI. The broader design goal is still the original “organize and prioritize tasks together” concept described in `reference/game-concept.md`.

## Quick start

This project currently has one runtime dependency: `pygame`.

1. Install Python from <https://www.python.org/downloads/>.
2. Install Pygame from <https://www.pygame.org/wiki/GettingStarted#Pygame%20Installation>.
3. From the repository root, install the project in editable mode:

```bash
python -m pip install -e .
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

If the client and server will run on different computers, edit `src/better_together_server/.env` on the server machine and `src/better_together_client/.env` on the client machine so the bind/connect host settings match your LAN.

The server runtime is now headless-capable, so it no longer needs to open a Pygame window just to host multiplayer state.

Optional but recommended before larger code changes:

```bash
python scripts/build_runtime_assets.py --check
python -m unittest discover -s tests -v
```

If you change the shared asset catalog or any runtime image sources, regenerate the package-local runtime bundles from the repository root:

```bash
python scripts/build_runtime_assets.py
```

If your machine exposes Python as `python3` instead of `python`, substitute that command name.

For full setup notes, launch caveats, and smoke-test steps, see [`docs/quickstart.md`](docs/quickstart.md).

## Documentation

- [`docs/quickstart.md`](docs/quickstart.md) — installation, launch order, and local smoke-test flow.
- [`docs/architecture.md`](docs/architecture.md) — client/server boundaries, room lifecycle, transport contract, and runtime caveats.
- [`docs/gameplay-status.md`](docs/gameplay-status.md) — original concept versus the currently implemented prototype.
- [`docs/contributing.md`](docs/contributing.md) — repo map, safe-change guidance, and manual verification checklist.
- [`docs/assets-licenses.md`](docs/assets-licenses.md) — current asset inventory, attribution, and license notes.

## Repository map

- `src/` — canonical Python package tree containing `better_together_client`, `better_together_server`, and `better_together_shared`.
- `assets/source/` — canonical checked-in master art used to regenerate runtime bundles.
- `reference/` — concept notes, raw license texts, and an asset wish list / research list.
- `credits/` — one file per currently tracked asset attribution source.
- `docs/` — project knowledge base for contributors and future AI-assisted work.

## Current project status

The project vision and the codebase are related but not identical:

- **Vision:** a four-player co-op game about prioritizing tasks under pressure.
- **Current prototype:** a local multiplayer ship-defense loop with movement, repair, cannon use, pirate ship pressure, and AI fallback on disconnect.

See [`docs/gameplay-status.md`](docs/gameplay-status.md) for the detailed gap between the vision and the implementation.

## Assets

Current asset attributions are documented in [`docs/assets-licenses.md`](docs/assets-licenses.md), with raw source notes preserved in `credits/`.

Logical runtime asset IDs now live in `src/better_together_shared/asset_catalog.py`, canonical master art now lives under `assets/source/`, and the package-local client/server runtime bundles can be validated or regenerated with `scripts/build_runtime_assets.py`.
