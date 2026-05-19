# Better-Together gameplay ownership map

## Client-owned today

- Opening the gameplay window, collecting input, moving the local crew member, and drawing the ship, water, UI, projectiles, and other entities.
- Prompt/HUD presentation, local cannon aim placement while holding `SPACE`, movement-hint/session state, and client-only overlay or shoot-animation presentation that follows authoritative server state.
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

- Room membership, slot assignment/release, stored crew state, AI movement, pirate ship updates, damage markers, enemy projectile flight, player-fired projectile flight and hits, resource refills, authoritative repair timing/wood use, authoritative cannon reload and fire acceptance, authoritative game-over state/countdown, and server-side simulation timing.
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
  - `advance_game()`
  - `advance_game_over_state()`
  - `advance_player_repairs()`
  - `advance_player_cannon_actions()`
  - `advance_player_projectiles()`
  - `advance_ready_games()`
  - `advance_ready_rooms()`

## Shared boundary

- `src/better_together_shared/protocol.py` owns snapshot and message shape.
- `src/better_together_shared/transport.py` owns the framed socket transport.
- `src/better_together_shared/asset_catalog.py` matters when gameplay-visible entity or asset identifiers change.

## Triage questions

- Is the symptom only a local prompt, HUD string, aim reticle, or overlay presentation? It is probably client-owned.
- Is the displayed repair/reload/game-over countdown or progression wrong? Include server gameplay state, not just client HUD code.
- Does another player see the effect or depend on it? Include server/shared code too.
- Does it change fields sent over the wire or the shape of `player_assignment`, `player_update`, or `room_state`? Include shared protocol and both runtime halves.
- Does it affect room membership, AI slot reuse, damage markers, projectile flight, repair/reload flow, or game-over progression? Include server room/game/network modules.

## Common traps

- Treating repair/reload countdowns or `Game Over` state as local just because the client renders them.
- Expanding client-owned logic without checking whether the server already echoes authoritative state back.
- Forgetting that `room_state` also carries `self_player`, `damage_markers`, `enemy_projectiles`, `player_projectiles`, and gameplay state.
- Treating pirate ships as separate from the normal entity reply shape; the client still receives and renders them through that same payload.
