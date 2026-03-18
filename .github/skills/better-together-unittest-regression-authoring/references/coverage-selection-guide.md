# Better-Together coverage selection guide

## Prefer the narrowest credible test first

### Pure helper or state-shape bug

- Start with:
  - `tests/test_protocol.py`
  - `tests/test_transport.py`
  - `tests/test_client_session.py`
  - `tests/test_client_game_loop.py`
  - `tests/test_asset_pipeline.py`

### Client module behavior

- Start with:
  - `tests/test_client_network.py`
  - `tests/test_client_render.py`
  - `tests/test_client_game_loop.py`
  - `tests/test_client_session.py`

### Server room or simulation behavior

- Start with:
  - `tests/test_room_manager.py`
  - `tests/test_server_game.py`
  - `tests/test_server_ai.py`
  - `tests/test_server_network.py`

### Launch/config behavior

- Start with:
  - `tests/test_config.py`
  - `tests/test_package_entrypoints.py`
  - `tests/test_macos_launchers.py`

### Live socket or handshake regressions

- Add `tests/test_server_protocol.py` when the bug truly depends on real framed socket flow or disconnect cleanup.

## Escalate only when needed

- If a pure helper test proves the bug, do not jump straight to a live process test.
- If the bug only appears when several layers interact, add the narrow tests first and then one higher-level integration test if needed.

## Manual smoke escalation

- Add a manual smoke expectation when the bug concerns rendering, input, HUD prompts, or other behavior that the existing automated tests do not fully observe.
