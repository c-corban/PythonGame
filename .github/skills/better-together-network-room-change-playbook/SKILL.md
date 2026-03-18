---
name: better-together-network-room-change-playbook
description: 'Use when reviewing or planning Better-Together protocol messages, room lifecycle, handshake flow, player_assignment/player_update/room_state behavior, matchmaking, disconnect cleanup, AI slot reuse, or client/server snapshot compatibility.'
argument-hint: 'Describe the protocol change, room-lifecycle bug, or networking files involved.'
---

# Better-Together Network and Room Change Playbook

## When to Use

- Protocol or transport changes.
- Room assignment, disconnect cleanup, matchmaking, or AI slot reuse changes.
- Bugs in handshake flow or authoritative room-state replies.

## Procedure

1. Inventory the coupled change surface with the [network change surface](./references/network-change-surface.md). Treat client, server, and shared protocol files as one unit.
2. Sequence edits carefully:
   - shared snapshot/message helpers first when the wire contract changes
   - server room/game/network logic next
   - client consumption and rendering expectations after that
   - tests and docs last, in the same branch
3. Preserve compatibility shims intentionally: `RoomRegistry.games` remains authoritative, module-level `games` is only a compatibility alias, and `Game.players` remains a compatibility view over crew and pirate ships.
4. Validate with the [network verification checklist](./references/network-verification-checklist.md). Prefer targeted protocol/network tests plus the live server integration flow when behavior crosses the socket boundary.
5. Summarize the contract change clearly: which messages changed, which fields changed, how room lifecycle behavior changed, and which docs/tests were updated.

## References

- [Network change surface](./references/network-change-surface.md)
- [Network verification checklist](./references/network-verification-checklist.md)
