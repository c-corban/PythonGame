# Project Guidelines

## Canonical commands

- Install the repository in editable mode from the repo root with `python -m pip install -e .`.
- Prefer the package entrypoints as the canonical launch path:
  - `python -m better_together_server`
  - `python -m better_together_client`
- Installed console scripts also exist:
  - `better-together-server`
  - `better-together-client`
- The macOS launchers `Launch Better Together Server.command` and `Launch Better Together Client.command` are supported and tested, but they are the raw-checkout convenience path rather than the preferred entrypoint.
- Run the standard automated baseline from the repo root with:
  - `python scripts/build_runtime_assets.py --check`
  - `python -m unittest discover -s tests -v`
- Run a single test module with `python -m unittest tests.test_protocol`.
- Run a single test method with `python -m unittest tests.test_protocol.ProtocolHelperTests.test_protocol_messages_round_trip_through_pickle`.
- Rebuild runtime asset bundles with `python scripts/build_runtime_assets.py`.
- Useful asset-pipeline variants:
  - `python scripts/build_runtime_assets.py --check --strict-staleness`
  - `python scripts/build_runtime_assets.py --dry-run`
  - `python scripts/build_runtime_assets.py --bundle client`
  - `python scripts/build_runtime_assets.py --bundle server`
- Tests use `unittest`, not `pytest`.
- No lint or type-check command is currently configured in this repository.
- If your machine exposes Python as `python3` instead of `python`, substitute that executable.

## Where to look first

- `docs/knowledge-base.md` for documentation ownership, update routing, and `.github` customization discovery.
- `docs/quickstart.md` for setup, the canonical automated baseline, launch order, and smoke-test flow.
- `docs/architecture.md` for runtime boundaries, room lifecycle, protocol/transport details, and asset/runtime caveats.
- `docs/gameplay-status.md` for the current playable loop versus the original concept.
- `docs/contributing.md` for change-risk guidance and change-specific verification flow.
- `AGENTS.md` for the detailed prompt/skill/agent inventory.

## High-level architecture

- Runtime code is split across three canonical packages in `src/`:
  - `better_together_client` owns the gameplay window, input loop, rendering, local prompt/HUD state, and client-side session state.
  - `better_together_server` owns room allocation, AI, authoritative simulation, and per-client protocol handling.
  - `better_together_shared` owns shared config, protocol/snapshot helpers, transport framing, and the asset catalog/pipeline helpers.
- The prototype is intentionally not fully server-authoritative. The client still owns prompt presentation, window/render lifecycle, and cannon aim placement, while the server owns room membership, AI movement, projectile flight, damage markers, repair/reload timing, inventory refills, and authoritative match-over state.
- Networking is raw TCP with 4-byte length-prefixed framed `pickle` message dictionaries. The shared message contract and snapshot validation live in `src/better_together_shared/protocol.py`; framed socket reads/writes live in `src/better_together_shared/transport.py`.
- Room lifecycle is server-owned. `src/better_together_server/room_manager.py::RoomRegistry.games` is the authoritative room store, and the module-level `games` name is only a compatibility alias. Human clients reuse AI-controlled crew slots before new room creation, and empty rooms are deleted so their room IDs can be reused.
- `src/better_together_server/game.py::Game.players` is a compatibility view over `Game.crew_members` and `Game.pirate_ships`, not the primary storage model.
- Asset packaging is a cross-cutting system. `assets/source/` is the canonical editable asset tree, while `src/better_together_client/Images/` and `src/better_together_server/Images/` are generated runtime bundles built from `src/better_together_shared/asset_catalog.py` via `scripts/build_runtime_assets.py`.
- The server is headless-capable, but not asset-free or pygame-free: it still loads images and masks for collision and AI movement.

## Key conventions

- Prefer `python -m better_together_server` and `python -m better_together_client` as the canonical entrypoints. Role-local env files live in `src/better_together_server/.env` and `src/better_together_client/.env`; `BETTER_TOGETHER_ENV_FILE` is an explicit override, not the default path.
- Treat these as linked change surfaces:
  - `src/better_together_client/player.py` + `src/better_together_server/player.py` + `src/better_together_shared/protocol.py`
  - `src/better_together_client/network.py` + `src/better_together_server/network.py` + `src/better_together_server/room_manager.py` + `src/better_together_server/game.py` + `src/better_together_shared/transport.py`
  - `src/better_together_client/assets.py` + `src/better_together_server/assets.py`
- The flat `tests/` suite covers config/package entrypoints/macOS launchers, shared protocol and transport helpers, asset catalog/pipeline/helpers, client network/render/session/game-loop helpers, and server room/network/game/AI behavior.
- If you change `src/better_together_shared/asset_catalog.py` or files under `assets/source/`, regenerate the runtime bundles with `python scripts/build_runtime_assets.py` before running the full baseline.
- Keep the matching docs in sync with the change surface:
  - setup/run flow -> `README.md`, `docs/quickstart.md`
  - networking/room lifecycle/state ownership -> `docs/architecture.md`
  - gameplay loop or shipped feature set -> `docs/gameplay-status.md`
  - assets/provenance -> `docs/assets-licenses.md`, `credits/`
- Treat `docs/` as the live source of truth. Use `reference/` only for background and historical context.

## Copilot workflow routing

- Check `AGENTS.md` for the detailed `.github` agents/skills/prompts map instead of duplicating that inventory here.
- Use the file-targeted `.github/instructions/*.md` guidance when editing matching files.
- When a task is still in planning or triage, prefer the matching skill or prompt first. Use specialized agents when the task is implementation-focused or when you need a read-only impact map across files, docs, and tests.
