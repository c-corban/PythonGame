# Better-Together server simulation verification checklist

## Targeted automated checks

- `tests/test_server_ai.py` for room ticking, resource refills, enemy attacks, and projectile-to-damage-marker behavior.
- `tests/test_server_game.py` for room invariants, crew slots, pirate ships, and simulation-step accounting.
- `tests/test_room_manager.py` when room assignment, cleanup, or AI slot availability changes.
- `tests/test_server_protocol.py` when the server-owned simulation change affects behavior visible through live room replies.

## Runtime follow-up

- If the change is visible in gameplay, start the server and client and confirm the new server-owned behavior appears as expected.
- For multiplayer-sensitive changes, connect multiple clients and confirm room simulation still behaves consistently across reused AI slots.

## Docs to update

- Update `docs/gameplay-status.md` when the playable loop or visible enemy/AI behavior changes.
- Update `docs/architecture.md` when simulation ownership, room ticking, or room-lifecycle semantics change.

## Reporting

- Explain whether the fix stayed entirely in server-owned simulation code or crossed into protocol/client behavior.
