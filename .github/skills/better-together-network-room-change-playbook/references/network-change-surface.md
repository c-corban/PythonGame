# Better-Together network change surface

## Shared protocol first when the contract changes

- `src/better_together_shared/protocol.py` defines message types, snapshot shape, validation, and normalization.
- `src/better_together_shared/transport.py` defines the 4-byte framed transport and max message size behavior.
- If snapshot fields change, keep `src/better_together_client/player.py` and `src/better_together_server/player.py` compatible with the shared helpers.

## Server room lifecycle surface

- `src/better_together_server/room_manager.py` owns `RoomRegistry.games`, slot assignment/release, room cleanup, and room-facing message helpers.
- `src/better_together_server/game.py` owns crew slots, pirate ships, and `Game.players` compatibility behavior.
- `src/better_together_server/network.py` owns `client_thread()`, session threads, and socket reply flow.
- `src/better_together_server/ai.py` or `Game` ticking matters when message cadence or room simulation timing changes.

## Client consumption surface

- `src/better_together_client/network.py` must still parse assignment and room-state replies.
- `src/better_together_client/game_loop.py` and `src/better_together_client/render.py` still expect synced `self_player`, `damage_markers`, `enemy_projectiles`, and other entities.

## Behavior to preserve unless intentionally changed

- `player_assignment` followed by frame-by-frame `player_update` and `room_state`.
- Room replies include pirate ships as normal entities.
- Disconnect flips the crew slot back to AI and deletes rooms that become fully AI-controlled.
- `Game.ai[i] == True` means the slot is currently AI-controlled and available for a human client.

## High-risk questions

- Does this change modify a field validated by `validate_message()` or consumed by the `extract_*` helpers?
- Does it change how rooms are created, reused, or deleted?
- Does it change what the client expects in `room_state`?
- Does it require `docs/architecture.md` to explain a new state ownership split or protocol flow?
