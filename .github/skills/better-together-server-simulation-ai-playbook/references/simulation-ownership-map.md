# Better-Together server simulation ownership map

## Server-owned simulation today

- AI crew movement and obstacle-aware pathing in `src/better_together_server/ai.py`.
- Pirate ship motion and frame updates.
- Enemy attack timing, projectile creation, projectile flight, and conversion into damage markers.
- Resource refill timing for wood and cannonball inventory.
- Room ticking and simulation cadence through `advance_ready_rooms()` and `run_simulation_loop()`.

## Primary files and anchors

- `src/better_together_server/ai.py`
  - `advance_ai_crew()`
  - `advance_enemy_attacks()`
  - `advance_enemy_projectiles()`
  - `advance_pirate_ships()`
  - `advance_resource_refills()`
  - `advance_game()`
  - `advance_ready_rooms()`
  - `run_simulation_loop()`
- `src/better_together_server/game.py`
- `src/better_together_server/room_manager.py`
- `src/better_together_server/app.py`

## When to widen the surface

- If a server behavior change modifies values sent inside snapshots or `room_state`, also include `src/better_together_shared/protocol.py` and both runtime networking modules.
- If a visible gameplay behavior changes from the player’s perspective, update `docs/gameplay-status.md`.
- If authority or room lifecycle semantics change, update `docs/architecture.md`.

## Common traps

- Treating room tick cadence as if it were driven by client message frequency; the current server simulation loop is independent.
- Forgetting that server AI and collision logic still rely on server asset loading even when the server is headless.
- Fixing a symptom in the client when the root cause lives in `advance_enemy_attacks()` or `advance_enemy_projectiles()`.
