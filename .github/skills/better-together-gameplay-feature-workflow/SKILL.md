---
name: better-together-gameplay-feature-workflow
description: 'Use when changing Better-Together gameplay flow, HUD prompts, aiming/cannon presentation, GameplaySessionState, RenderRuntime, client-side presentation/state, or triaging whether a bug belongs here, server simulation, or shared/network code.'
argument-hint: 'Describe the gameplay feature, bug symptom, or files you want to change.'
---

# Better-Together Gameplay Feature Workflow

## When to Use

- Gameplay loop, HUD prompt, input, aiming, animation, or client-side presentation/state changes.
- Bugs around repair prompts, cannon prompts, aiming feedback, or “who owns this behavior?”
- Initial triage when a gameplay issue might instead belong to server simulation or shared/network code.
- Changes near `game_loop.py`, `session.py`, `render.py`, or gameplay state mirrored from server replies.

## Procedure

1. Classify ownership first with the [ownership map](./references/ownership-map.md). Do not assume the server is fully authoritative.
2. Start with the smallest client-only surface that can solve the problem. Common anchors are `connect_to_server()`, `sync_remote_players()`, `handle_repairs()`, `handle_cannon_controls()`, `update_game_over_overlay()`, `update_shoot_animation()`, `GameplaySessionState`, and `RenderRuntime`.
3. If the issue is mainly AI movement, pirate ships, projectile or damage-marker simulation, or other server-owned simulation behavior—and not primarily about snapshot/message shape—stop and switch to the `better-together-server-simulation-ai-playbook` skill.
4. If the issue touches authoritative repair/reload/game-over timing or state, or affects data exchanged with the server, room state, other players, or fields inside snapshots/messages, stop expanding client-only logic and switch to the `better-together-network-room-change-playbook` skill.
5. Keep prototype-friendly changes small and note any docs updates needed in `docs/gameplay-status.md` or `docs/architecture.md`.
6. Validate with the [verification guide](./references/verification-guide.md) and summarize what stayed client-only versus what crossed into server/shared behavior.

## References

- [Ownership map](./references/ownership-map.md)
- [Verification guide](./references/verification-guide.md)
