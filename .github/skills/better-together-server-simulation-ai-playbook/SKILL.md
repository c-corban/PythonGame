---
name: better-together-server-simulation-ai-playbook
description: 'Use when reviewing or planning Better-Together AI movement, pirate ships, simulation ticks, advance_ready_rooms, enemy projectile flight, damage markers, inventory refill timing, or other server-owned simulation behavior.'
argument-hint: 'Describe the server-simulation bug, feature, or files you want to inspect.'
---

# Better-Together Server Simulation and AI Playbook

## When to Use

- Server-only behavior around AI crew, pirate ships, room ticking, enemy attacks, or resource refills.
- Bugs where authority clearly belongs to the server, but the change does not primarily alter the wire contract.
- Planning or triaging changes in `src/better_together_server/ai.py`, `game.py`, `room_manager.py`, or server-owned state described in `docs/architecture.md`.

## Procedure

1. Start with the [simulation ownership map](./references/simulation-ownership-map.md) and confirm the behavior is server-owned rather than client-owned or wire-contract-driven.
2. Follow the smallest server-side path that can fix the issue. Common anchors are `advance_ai_crew()`, `advance_enemy_attacks()`, `advance_enemy_projectiles()`, `advance_resource_refills()`, `advance_game()`, `advance_ready_rooms()`, and `run_simulation_loop()`.
3. If the change alters snapshot fields, message flow, or room-state payload shape, switch to the `better-together-network-room-change-playbook` skill for the contract portion.
4. Keep `docs/gameplay-status.md` and `docs/architecture.md` aligned when server-owned behavior changes in visible ways.
5. Validate with the [simulation verification checklist](./references/simulation-verification-checklist.md) and summarize what remained server-owned versus what required wider changes.

## References

- [Simulation ownership map](./references/simulation-ownership-map.md)
- [Simulation verification checklist](./references/simulation-verification-checklist.md)
