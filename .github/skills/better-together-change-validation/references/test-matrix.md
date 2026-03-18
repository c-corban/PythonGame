# Better-Together test matrix

## Always-on baseline

- From the repository root, prefer the documented baseline before sign-off:
  - `python scripts/build_runtime_assets.py --check`
  - `python -m unittest discover -s tests -v`
- Tests use `unittest`, not `pytest`.

## By change surface

### Docs-only changes

- Usually a review pass is enough.
- Run automated checks only when the docs change accompanies code changes in the same branch or the user explicitly requests full verification.

### Client gameplay, session, render, or prompt logic

- Start with:
  - `tests/test_client_game_loop.py`
  - `tests/test_client_session.py`
  - `tests/test_client_render.py`
- Add a manual smoke test if input, HUD prompts, rendering, or runtime-only behavior changed.

### Shared protocol or transport helpers

- Start with:
  - `tests/test_protocol.py`
  - `tests/test_transport.py`
- Add client/server networking tests if the changed helper affects live socket behavior or room-state parsing.

### Client/server networking and room lifecycle

- Start with:
  - `tests/test_client_network.py`
  - `tests/test_server_network.py`
  - `tests/test_server_protocol.py`
  - `tests/test_room_manager.py`
- Add `tests/test_server_game.py` and `tests/test_server_ai.py` when the change affects room simulation, pirate ships, or AI-owned slots.

### Asset catalog, asset pipeline, or mirrored asset loaders

- If `assets/source/` or `src/better_together_shared/asset_catalog.py` changed, regenerate bundles with `python scripts/build_runtime_assets.py` before running checks.
- Start with:
  - `tests/test_asset_catalog.py`
  - `tests/test_asset_pipeline.py`
  - `tests/test_assets.py`

### Launchers, entrypoints, env/config, or startup flow

- Start with:
  - `tests/test_config.py`
  - `tests/test_package_entrypoints.py`
  - `tests/test_macos_launchers.py`

## Notes and gotchas

- `tests/test_support.py` is the model for dummy SDL setup and workspace `PYTHONPATH` handling in tests.
- `tests/test_server_protocol.py` is a live server integration check; it may skip if port `2911` is already in use.
- The client still needs a graphical desktop session for real runtime smoke tests even though many automated checks run headlessly.
