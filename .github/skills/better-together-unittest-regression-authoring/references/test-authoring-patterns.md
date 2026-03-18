# Better-Together test authoring patterns

## Core repo style

- Tests use `unittest`, not `pytest`.
- Reuse `tests/test_support.py` for dummy SDL defaults and workspace `PYTHONPATH` helpers.
- Prefer focused `unittest.TestCase` methods with descriptive names over large scenario tests.

## Common patterns already in the repo

### Import-safe module tests

- Use `add_workspace_package_paths()` before importing project modules when the test may run as either `tests.*` or a top-level module.
- Use `importlib.import_module()` in `setUpClass()` when import-time behavior matters.
- Examples:
  - `tests/test_package_entrypoints.py`
  - `tests/test_client_game_loop.py`
  - `tests/test_client_network.py`

### Mock-driven unit tests

- Prefer `unittest.mock.patch` to isolate pygame, sockets, random choices, and subprocess behavior.
- Examples:
  - `tests/test_client_network.py`
  - `tests/test_server_ai.py`
  - `tests/test_asset_pipeline.py`
  - `tests/test_macos_launchers.py`

### Headless pygame expectations

- Many tests rely on dummy SDL environment defaults from `tests/test_support.py`.
- Do not assume a display surface exists unless the test explicitly creates one.
- Asset helper tests already model the display/no-display split.

### Live integration tests

- Use them sparingly when helper-level tests cannot prove the behavior.
- `tests/test_server_protocol.py` is the template for a real server-process integration test with output capture and cleanup.

## Good habits

- Match the nearest existing test file instead of inventing a new testing idiom.
- Keep one regression per test method when practical.
- If a bug crosses multiple layers, add the smallest test at each layer that buys confidence rather than one huge end-to-end test.
