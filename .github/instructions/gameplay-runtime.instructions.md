---
description: "Use when editing Better-Together gameplay flow, HUD prompts, repair timing, cannon reload timing, GameplaySessionState, RenderRuntime, or deciding whether a gameplay bug belongs in client, server, or shared code."
name: "Gameplay runtime ownership guardrails"
applyTo: "src/better_together_client/game_loop.py, src/better_together_client/render.py, src/better_together_client/session.py, src/better_together_client/player.py, src/better_together_server/game.py, src/better_together_server/ai.py, src/better_together_shared/protocol.py, docs/architecture.md, docs/gameplay-status.md"
---
# Gameplay runtime ownership guardrails

- Treat `src/better_together_client/game_loop.py`, `src/better_together_client/session.py`, `src/better_together_client/render.py`, and `src/better_together_client/player.py` as one gameplay surface.
- The prototype is **not** fully server-authoritative. Preserve the current ownership split unless a task explicitly changes it.
- Client-owned behaviors currently include prompt/HUD presentation, local cannon aim placement, render/window flow, and the frame-to-frame client session state that supports those displays.
- Server-owned behaviors currently include room membership, AI movement, pirate ship motion, deck damage markers, projectile flight, authoritative repair/reload timing and state progression, authoritative game-over timing/state progression, and other simulation state.
- Keep `GameplaySessionState` as the home for frame-to-frame client gameplay state, and keep `RenderRuntime` responsible for the runtime resources needed to draw prompts/HUD elements.
- Do not smuggle protocol changes into UI-only tasks. If the change affects snapshots, `room_state`, or player-update payloads, also review `.github/instructions/networking.instructions.md`.
- When the playable loop changes, update `docs/gameplay-status.md`. When the ownership split changes, update `docs/architecture.md`.
