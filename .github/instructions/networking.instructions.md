---
description: "Use when editing networking, sockets, pickle serialization, player state sync, room lifecycle, matchmaking, transport helpers, or client/server protocol code in Better-Together."
name: "Networking and serialization guardrails"
applyTo: "src/better_together_client/network.py, src/better_together_server/network.py, src/better_together_server/room_manager.py, src/better_together_server/game.py, src/better_together_server/ai.py, src/better_together_shared/protocol.py, src/better_together_shared/transport.py, src/better_together_client/player.py, src/better_together_server/player.py, docs/architecture.md"
---

# Networking and serialization guardrails

- Treat `src/better_together_client/network.py::Network`, `src/better_together_server/network.py::client_thread`, `src/better_together_server/room_manager.py`, `src/better_together_server/game.py`, and `src/better_together_shared/protocol.py` as one change surface.
- Treat `src/better_together_shared/transport.py` as part of the same surface whenever message framing, payload sizing, or socket read/write behavior changes.
- The current protocol is raw TCP plus `pickle` of explicit message dictionaries with a `protocol_version` field: one initial `player_assignment` message followed by frame-by-frame `player_update` and `room_state` messages.
- Runtime network configuration lives in `src/better_together_client/.env` and `src/better_together_server/.env`.
- `src/better_together_client/player.py` and `src/better_together_server/player.py` no longer need matching module names for deserialization, but both classes must stay compatible with the snapshot fields defined in `src/better_together_shared/protocol.py`.
- `Game.players` is a compatibility view over `Game.crew_members` and `Game.pirate_ships`. Client logic still expects the reply payload to include those non-human entities.
- If you change room assignment or disconnect behavior, verify how `src/better_together_server/game.py`, `src/better_together_server/room_manager.py`, `src/better_together_server/network.py`, `Game.ai`, `RoomRegistry.games`, and the module-level `games` compatibility alias work together.
- Update `docs/architecture.md` whenever you intentionally change the protocol, room lifecycle, or state ownership split.
