# Better-Together gameplay ownership map

## Client-owned today

- Opening the gameplay window, collecting input, moving the local crew member, and drawing the ship, water, UI, projectiles, and other entities.
- Repair prompts, cannon prompts, local cooldowns, pending repaired damage markers, and game-over display logic.
- Key files:
  - `src/better_together_client/game_loop.py`
  - `src/better_together_client/session.py`
  - `src/better_together_client/render.py`
  - `src/better_together_client/player.py`
  - `src/better_together_client/network.py`
- Key anchors:
  - `connect_to_server()`
  - `sync_remote_players()`
  - `handle_repairs()`
  - `handle_cannon_controls()`
  - `update_game_over_overlay()`
  - `update_shoot_animation()`
  - `GameplaySessionState`
  - `FramePromptState`

## Server-owned today

- Room membership, slot assignment/release, AI movement, pirate ship updates, damage markers, active enemy projectiles, stored crew state, and server-side simulation timing.
- Key files:
  - `src/better_together_server/room_manager.py`
  - `src/better_together_server/game.py`
  - `src/better_together_server/network.py`
  - `src/better_together_server/ai.py`
- Key anchors:
  - `RoomRegistry`
  - `build_assignment_message()`
  - `build_room_state_message()`
  - `assign_player_slot()`
  - `release_player_slot()`
  - `advance_ready_games()`
  - `advance_ready_rooms()`

## Shared boundary

- `src/better_together_shared/protocol.py` owns snapshot and message shape.
- `src/better_together_shared/transport.py` owns the framed socket transport.
- `src/better_together_shared/asset_catalog.py` matters when gameplay-visible entity or asset identifiers change.

## Triage questions

- Is the symptom only a local prompt, HUD string, or timer? It is probably client-owned.
- Does another player see the effect or depend on it? Include server/shared code too.
- Does it change fields sent over the wire or the shape of `player_assignment`, `player_update`, or `room_state`? Include shared protocol and both runtime halves.
- Does it affect room membership, AI slot reuse, damage markers, or enemy projectiles? Include server room/game/network modules.

## Common traps

- Expanding client-owned logic without checking whether the server already echoes authoritative state back.
- Forgetting that `room_state` also carries `self_player`, `damage_markers`, and `enemy_projectiles`.
- Treating pirate ships as separate from the normal entity reply shape; the client still receives and renders them through that same payload.
