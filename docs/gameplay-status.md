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
- server-side refill timers restore depleted wood and cannonball inventories after a delay,
- unrepaired hits accumulate until the ship loses,
- disconnected crew slots fall back to AI,
- rooms are created or reused depending on available AI-controlled slots,
- and empty rooms are deleted once all crew slots return to AI.

The prototype already captures the “cooperate under pressure” spirit, but it does not yet implement the broader task-management design from the concept note.

## Concept versus implementation

| Topic | Design vision | Current implementation |
| --- | --- | --- |
| Core activity | Multiple task types that must be prioritized | Ship movement, repair, cannon use, and pirate-ship pressure |
| Failure condition | Poor organization / wrong prioritization | Too many unrepaired hit markers on the ship (currently 30) |
| Victory condition | Survive a fixed amount of time | No full victory loop is currently implemented; the current match-over flow is server-authoritative `Game Over` state/countdown that the client renders |
| AI fallback | AI replaces disconnected players and adjusts in strength | AI replaces disconnected players with lightweight wandering crew behavior; pirate ships, attacks, and refill timing remain server-driven |
| Parallel matches | New rooms open when existing ones are full of humans | Implemented through room allocation in `src/better_together_server/room_manager.py`, with room IDs reused once empty rooms are deleted |
| Task collaboration | Helping another player accelerates shared tasks | Not yet represented as a generalized task system |
| Resource economy | Task pressure implies shared resource use, but the concept note does not define a concrete refill loop | Wood and cannonball inventories can deplete to 0 and refill on the server after a delay |
| State ownership | The concept assumes shared cooperative systems but does not pin every rule to one runtime | Authority is still split, but more gameplay now lives on the server: the client owns prompt presentation and cannon aim placement, while the server owns rooms, AI, damage markers, enemy projectiles, player-fired projectile flight and hits, repair timing, cannon reload/fire acceptance, and match-over state |

## Current gameplay loop

At a high level, the current play session looks like this:

1. The server assigns each connected client a crew slot and sends the initial `player_assignment` snapshot plus authoritative gameplay state for that slot.
2. Each frame, the client sends its local player snapshot together with interaction intent such as the `SPACE` hold state, requested repair target, and cannon aim target.
3. The server background simulation loop advances AI crew, pirate ships, enemy attacks, enemy projectile flight, player-fired projectile flight, cannon hit resolution, empty-inventory refills, repair timing, cannon reload timing, cannon-fire acceptance, and match-over state inside the active room state.
4. The `room_state` reply contains the rest of the room, the authoritative local snapshot, current damage markers, active enemy projectile positions, active player projectile positions, and authoritative gameplay state for repair/reload/game-over behavior.
5. The client still shows prompts locally, but the displayed repair/reload countdowns now come from the server-owned gameplay state.
6. If too many hit markers accumulate (currently 30), the server flips the room into `Game Over` and the client displays that authoritative state until the server countdown expires.

## Glossary

### Room

A multiplayer match stored in `src/better_together_server/room_manager.py::RoomRegistry.games`, usually reached through `default_room_registry`. The module-level `games` name still exists as a compatibility alias. Rooms reuse AI-controlled slots before creating new rooms and are deleted once all four crew slots return to AI.

### Crew slot

One of the four human/AI player positions created in `src/better_together_server/game.py::Game`.

### AI slot

A crew slot marked `True` in `Game.ai`, meaning the slot is currently AI-controlled and can be taken by a newly connected human client.

### Pirate ship

A hostile entity created on the server in `Game.pirate_ships`. `Game.players` remains a compatibility view that still exposes crew first and pirate ships after them, and those pirate ships are sent back to clients as part of the normal entity reply payload.

### Damage marker

A server-authoritative repair target stored in `Game.damage_markers` and mirrored to the client each frame. Players clear these markers by spending wood, and the match currently flips to `Game Over` once 30 markers accumulate.

### Enemy projectile

A server-authoritative in-flight cannonball stored in `Game.enemy_projectiles`. The client renders these projectile positions each frame until they land and become damage markers.

### Repair cycle

The interaction where a player stands near a hit marker, holds `SPACE`, and requests a repair target from the client, but the server owns the countdown, wood consumption, and final damage-marker removal.

### Cannon cycle

The interaction where a player stands near a cannon and aims locally, but the server owns reload progress, shot acceptance on release, cannonball inventory consumption, player projectile flight, pirate-ship hit resolution, and the projectile positions mirrored back to the client.

### Authoritative state

The part of the game that decides what is “really true.” In this prototype, authority is still split, but more of the gameplay loop now lives on the server: room membership, stored crew state, repair timing, cannon reload/fire state, player projectile flight, pirate-hit resolution, damage markers, enemy projectiles, pirate-ship behavior, empty-inventory refills, and game-over state live on the server, while prompt presentation, local movement input, and cannon aim placement still live in the client loop.

## Recommended next documentation habit

Whenever the playable loop changes, update this file at the same time so the “what exists now?” answer stays easy to trust. If the client/server ownership split changes too, update `docs/architecture.md` in the same branch.
