# Better-Together gameplay verification guide

## Targeted automated tests

- `tests/test_client_game_loop.py` for gameplay loop helpers such as `update_shoot_animation()`.
- `tests/test_client_session.py` for `GameplaySessionState`, `FramePromptState`, and prompt-state transitions.
- `tests/test_client_render.py` when render/UI/runtime setup changes.
- Add `tests/test_client_network.py`, `tests/test_protocol.py`, `tests/test_server_game.py`, or `tests/test_server_ai.py` when the gameplay change crosses into networked or server-driven state.

## Manual smoke expectations

- Run the server first, then the client.
- Confirm movement, HUD counters, repair prompts, cannon prompts, and clean shutdown/disconnect logging.
- For networked gameplay changes, confirm room state still syncs damage markers, enemy projectiles, and pirate ships.

## Docs to keep in sync

- Update `docs/gameplay-status.md` when the playable loop or implemented feature set changes.
- Update `docs/architecture.md` when ownership shifts between client and server or when network-visible behavior changes.

## Reporting

- Be explicit about which behavior remains client-owned versus server-owned after the change.
