# Architecture

This document describes the code as it exists today, not the eventual ideal architecture.

## Runtime overview

Better-Together is a Python/Pygame prototype with three canonical runtime packages in the repo-root `src/` tree:

- `src/better_together_client/game_loop.py` owns the main gameplay loop.
- `src/better_together_client/network.py` owns the client socket protocol.
- `src/better_together_client/render.py` owns the client `RenderRuntime` object and drawing helpers.
- `src/better_together_client/session.py` owns the client gameplay/session state that `game_loop.py` advances each frame.
- `src/better_together_server/game.py` owns the server-side room model.
- `src/better_together_server/room_manager.py` owns room allocation and cleanup state.
- `src/better_together_server/network.py` owns the server accept loop and per-client protocol handling.
- `src/better_together_server/ai.py` owns AI crew movement, pirate ship updates, and the server-side simulation tick helpers.
- `src/better_together_shared/protocol.py` owns the snapshot/message contract used by both sides.

Package entrypoints now bootstrap directly through `src/better_together_client/cli.py` and `src/better_together_server/cli.py`, while the root macOS launchers call those same modules with `src/` added to `PYTHONPATH` for raw-checkout execution.

## Canonical entry points

- **Client:** `python -m better_together_client`
- **Server:** `python -m better_together_server`
- **Installed console scripts:** `better-together-client` and `better-together-server`
- **macOS launchers:** `Launch Better Together Client.command` and `Launch Better Together Server.command`

Role-specific network settings now live beside the runtime packages as `src/better_together_client/.env` and `src/better_together_server/.env`.

The shared config loader also honors `BETTER_TOGETHER_ENV_FILE` as an explicit override, but the package-local role files remain the preferred source of truth.

## Client responsibilities

The client process is responsible for:

- opening the gameplay window,
- collecting keyboard input,
- moving the locally controlled crew member,
- rendering the ship, water, UI, projectiles, and other entities through `RenderRuntime`,
- tracking repair prompts, cannon prompts, local cooldowns, pending repair actions, and game-over display,
- rendering server-authoritative enemy projectile flights and deck damage markers,
- sending the local player state to the server each frame.

Key anchors:

- `src/better_together_client/network.py::Network`
- `src/better_together_client/render.py::refresh`
- `src/better_together_client/render.py::RenderRuntime`
- `src/better_together_client/game_loop.py::main`
- `src/better_together_client/session.py::GameplaySessionState`
- `src/better_together_client/player.py::Player.draw`
- `src/better_together_client/player.py::Player.move`
- `src/better_together_client/player.py::Player.collision`
- `src/better_together_client/app.py::main`

## Server responsibilities

The server process is responsible for:

- accepting TCP connections on the configured bind address (defaults to `localhost:2911`),
- finding or creating a room through `src/better_together_server/room_manager.py::RoomRegistry`,
- assigning a human player to the first AI-controlled slot in that room,
- replacing disconnected human slots with AI,
- running one managed `threading.Thread` worker per connected client session,
- advancing AI crew movement on the server simulation tick,
- advancing pirate ship behavior on the server simulation tick,
- advancing active enemy projectile flights and converting impacts into deck damage markers,
- returning the other entities in the room to each client.

Key anchors:

- `src/better_together_server/room_manager.py::RoomRegistry`
- `src/better_together_server/room_manager.py::default_room_registry`
- `src/better_together_server/game.py::Game`
- `src/better_together_server/room_manager.py::assign_player_slot`
- `src/better_together_server/network.py::client_thread`
- `src/better_together_server/ai.py::ai_move`
- `src/better_together_server/ai.py::ship_ai`
- `src/better_together_server/player.py::Player.move`
- `src/better_together_server/app.py::main`

## Room lifecycle

Room state lives in `src/better_together_server/room_manager.py` inside `RoomRegistry.games`, keyed by numeric room ID.

The module-level `games` dictionary and helper functions still exist, but they now delegate to `default_room_registry` as a compatibility layer while the server runtime moves toward explicit dependency injection.

`RoomRegistry` now also owns the synchronization lock used by the background simulation loop and the per-client protocol handlers.

More room-facing protocol operations now live behind the registry as well, including assignment-message creation, applying incoming crew updates, building room-state replies, and advancing due simulation steps.

Each `Game`:

- starts with four crew slots,
- tracks whether each slot is AI-controlled in `Game.ai`,
- creates four crew `Player` objects in `Game.crew_members`,
- creates pirate ships in `Game.pirate_ships`,
- exposes `Game.players` as a compatibility view that still presents crew first and pirate ships after them.

Current lifecycle behavior:

1. A new connection tries to join an existing room with at least one AI-controlled crew slot.
2. If no such slot exists, the server creates a new room.
3. On disconnect, that crew slot flips back to `AI`.
4. If all four crew slots are AI-controlled again, the room is deleted.

Important convention: `Game.ai[i] == True` currently means the slot is AI-controlled and therefore available for a future human client.

## Simulation ticking

The server no longer advances AI directly inside `src/better_together_server/network.py::client_thread`.

Instead:

- `src/better_together_server/app.py::main` starts a background simulation loop,
- `src/better_together_server/ai.py::run_simulation_loop` polls rooms independently of client traffic,
- each `Game` tracks `tick_interval_seconds` and `last_simulation_tick_at`,
- `src/better_together_server/ai.py::advance_ready_rooms` consumes elapsed time and advances only the rooms with pending simulation steps.

Per-client protocol handlers are now managed `threading.Thread` workers created from `src/better_together_server/network.py` instead of raw `_thread.start_new_thread` calls.

That means client update frequency no longer determines how often AI crew or pirate ships move.

## Network and serialization model

The transport model is intentionally simple and currently fragile:

- raw TCP sockets,
- `pickle` serialization of explicit message dictionaries,
- a `protocol_version` field on every message dictionary,
- a 4-byte length-prefixed frame around each serialized payload,
- a maximum framed payload size of `65535` bytes,
- basic protocol validation for message type, room metadata, and player snapshot shape,
- one initial assignment message followed by frame-by-frame player snapshot updates.

### Connection flow

1. `src/better_together_client/network.py::Network.connect()` opens a TCP connection to the configured client target address (defaults to `localhost:2911`).
2. The server immediately sends a framed `player_assignment` message containing `room_id`, `player_number`, and a snapshot of the assigned crew slot.
3. Each frame, the client sends a framed `player_update` message containing the local player snapshot.
4. The server applies that snapshot to the stored crew slot, applies any repaired room damage markers included in the update, and replies with a framed `room_state` message containing snapshots for every other entity in the room.
5. The `room_state` reply now also carries the server-authoritative snapshot of the local crew slot plus the current room damage markers and active enemy projectile positions.
6. AI crew and pirate ships advance on the server’s background simulation loop rather than once per received client message.

## Critical compatibility contract

The wire contract now lives in `src/better_together_shared/protocol.py`.

Protocol helpers now validate the decoded message shape before the runtime applies it. Invalid snapshots or malformed message payloads are rejected at the protocol boundary instead of failing later in `apply_player_snapshot()` or rendering code.

The snapshot field `char` is now a logical asset identifier rather than a raw package-relative image path. Client and server runtimes resolve those IDs through `src/better_together_shared/asset_catalog.py`.

Multiplayer no longer depends on unpickling a top-level module named `player`. Instead, the shared protocol helpers serialize explicit snapshots and message dictionaries.

That means outer repository layout no longer matters by itself for networking. The new high-risk contract is different:

- `src/better_together_client/player.py` and `src/better_together_server/player.py` still need to expose the state fields read and written by `src/better_together_shared/protocol.py`.
- `src/better_together_shared/protocol.py` defines the snapshot shape and message types that both sides must honor.
- Client logic still expects the room-state payload to include both crew members and pirate ships.

The paired `assets.py` pattern still exists and remains load-bearing for runtime behavior.

## Entity model

`Game` now stores crew members and pirate ships in separate collections:

- `Game.crew_members`
- `Game.pirate_ships`

`Game.players` remains as a compatibility view that presents crew first and pirate ships after them.

Client logic still treats pirate ships as networked entities rendered through the same broad drawing path as players, even though they are AI-controlled world actors.

One implementation detail to keep in mind: pirate ships use `Player` instances with `animation = None`, which changes how they are drawn.

## State ownership today

The current prototype is **not** fully server-authoritative.

The client owns or directly drives several gameplay behaviors, including:

- repair prompts and hold-to-repair timing,
- cannon aiming and reload timing,
- game-over display logic.

Those client-side timers and prompts now live in `src/better_together_client/session.py::GameplaySessionState`, while `src/better_together_client/render.py` owns the runtime resources needed to draw them.

The server owns or advances:

- room membership,
- the latest stored state per crew slot,
- server-authoritative room damage markers,
- active enemy projectile flight,
- inventory refill timing,
- AI crew wandering,
- pirate ship motion.

This split is important whenever you document bugs or plan refactors, because some “game rules” live in the client loop rather than in a single authoritative simulation.

## Asset loading and runtime caveats

Both `src/better_together_client/assets.py` and `src/better_together_server/assets.py`:

- resolve asset paths relative to the module directory,
- resolve shared logical asset IDs through `src/better_together_shared/asset_catalog.py`,
- cache image loads with `lru_cache`,
- expose `load_image()` and `load_scaled_image()` helpers.

The shared asset catalog now also records preferred build inputs and runtime bundle targets. `src/better_together_shared/asset_pipeline.py` and `scripts/build_runtime_assets.py` use that metadata to validate or regenerate the package-local `Images/` trees for the client and server bundles.

Canonical checked-in master art now lives under `assets/source/`, while the package-local `Images/` trees contain the generated runtime-facing bundles consumed by the client and headless server.

The client bundle keeps the visual runtime art, while the server bundle now intentionally stores collision-oriented mask versions for crew and obstacle assets. Those server images are still resolved through the same logical asset IDs, but they are optimized for `pygame.mask` generation rather than for rendering quality.

The canonical asset bundles now live directly beside those packages in `src/better_together_client/Images/` and `src/better_together_server/Images/`.

When a display surface exists, the loaders still use `convert()` / `convert_alpha()` for client-side rendering performance. Without a display surface, they now fall back to the raw loaded image surface.

That lets the server run headlessly while still using Pygame image and mask helpers for collision and AI movement.

## High-risk change areas

Treat these as linked change surfaces:

- `src/better_together_client/network.py` + `src/better_together_server/network.py` + `src/better_together_shared/protocol.py` for networking changes
- `src/better_together_client/player.py` + `src/better_together_server/player.py` + `src/better_together_shared/protocol.py` for player snapshot-shape changes
- `src/better_together_client/assets.py` + `src/better_together_server/assets.py` for asset-loading behavior changes
- `src/better_together_server/game.py` + `src/better_together_server/room_manager.py` + `src/better_together_server/network.py` for room lifecycle changes

If you change any of those, update the relevant docs in this folder as part of the same work.
