# Gameplay status

This file keeps two truths visible at the same time:

1. the original design direction,
2. the prototype that currently exists in code.

## Original design vision

The concept note in `reference/game-concept.md` describes a four-player cooperative game focused on coordination and prioritization:

- players organize themselves around multiple objectives,
- poor prioritization can lose the match,
- some tasks become urgent and force reprioritization,
- helping another player can complete a task faster than working alone,
- surviving for a fixed amount of time produces victory,
- disconnected players are replaced by AI,
- and if one match is already full of humans, new connections create another parallel match.

## Current prototype in code

The current implementation is narrower and more concrete:

- players move around a ship deck,
- pirate ships act as hostile pressure and fire animated cannonballs at the deck,
- players repair hit locations using wood,
- players reload and fire cannons using cannonball inventory,
- unrepaired hits accumulate until the ship loses,
- disconnected crew slots fall back to AI,
- and rooms are created or reused depending on available AI-controlled slots.

The prototype already captures the “cooperate under pressure” spirit, but it does not yet implement the broader task-management design from the concept note.

## Concept versus implementation

| Topic | Design vision | Current implementation |
| --- | --- | --- |
| Core activity | Multiple task types that must be prioritized | Ship movement, repair, cannon use, and pirate-ship pressure |
| Failure condition | Poor organization / wrong prioritization | Too many unrepaired hit markers on the ship |
| Victory condition | Survive a fixed amount of time | No full victory loop is currently implemented in code |
| AI fallback | AI replaces disconnected players and adjusts in strength | AI replaces disconnected players, but behavior is currently lightweight wandering |
| Parallel matches | New rooms open when existing ones are full of humans | Implemented through room allocation in `src/better_together_server/room_manager.py` |
| Task collaboration | Helping another player accelerates shared tasks | Not yet represented as a generalized task system |

## Current gameplay loop

At a high level, the current play session looks like this:

1. The server assigns each connected client a crew slot.
2. The client moves its local player around the deck.
3. The server background simulation loop advances AI crew and pirate ships inside the active room state.
4. The client shows local prompts for repair and cannon interactions.
5. Cannon shots and animated pirate-ship cannonballs create pressure on the deck.
6. If too many hit markers accumulate, the client displays `Game Over`.

## Glossary

### Room

A multiplayer match stored in `src/better_together_server/room_manager.py::RoomRegistry.games`, usually reached through `default_room_registry`. The module-level `games` name still exists as a compatibility alias.

### Crew slot

One of the four human/AI player positions created in `src/better_together_server/game.py::Game`.

### AI slot

A crew slot marked `True` in `Game.ai`, meaning the slot is currently AI-controlled and can be taken by a newly connected human client.

### Pirate ship

A hostile entity created on the server in `Game.pirate_ships`. `Game.players` remains a compatibility view that still exposes crew first and pirate ships after them, and those pirate ships are sent back to clients as part of the normal entity reply payload.

### Repair cycle

The client-side interaction where a player stands near a hit marker, holds `SPACE`, and spends wood to remove that damage marker.

### Cannon cycle

The client-side interaction where a player stands near a cannon, aims, reloads, and spends cannonball inventory to fire.

### Authoritative state

The part of the game that decides what is “really true.” In this prototype, authority is split: room membership and AI movement live on the server, while several gameplay interactions and timers live in the client loop.

## Recommended next documentation habit

Whenever the playable loop changes, update this file at the same time so the “what exists now?” answer stays easy to trust.
