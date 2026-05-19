# Better-Together agent map

This repository ships workspace-shared Copilot customizations so contributors can use the most specific workflow for high-risk change surfaces.

Use this file when you want the shortest path to the right agent, instruction, prompt, or skill.

For the broader documentation and update-ownership map, start with `docs/knowledge-base.md`.

## Start here

- Documentation ownership and update routing → `docs/knowledge-base.md`
- Quick customization routing → `AGENTS.md`
- Always-on AI guardrails → `.github/copilot-instructions.md`

## Custom agents

- **Runtime Network & Protocol** — use for `player_assignment`, `player_update`, `room_state`, snapshot compatibility, framed transport / `protocol_version`, and other wire-visible gameplay-state changes; if the wire shape stays stable and the bug is really server-owned simulation, start with **Server Simulation & AI Playbook**; hand off room allocation/reuse/cleanup policy to **Runtime Room Lifecycle**.
- **Runtime Room Lifecycle** — use for room allocation and reuse, AI slot reuse, disconnect cleanup, room ID reuse, and empty-room deletion behavior; if the issue is pure server simulation cadence without room-policy changes, start with **Server Simulation & AI Playbook**.
- **Runtime State Ownership** — use when deciding whether behavior belongs in client presentation, server simulation, or shared helper/protocol code, especially before shifting authority across that boundary.
- **Client Gameplay & HUD** — use for prompts/HUD, aim presentation, repair/cannon prompt text, shoot animation, game-over overlays, and other `GameplaySessionState` / `RenderRuntime` client gameplay polish driven by authoritative state.
- **Client Headless-Safe Runtime** — use for Pygame display setup, image conversion, mirrored client/server asset loading, render initialization, and protecting headless server support.
- **Runtime Asset Bundle & Pipeline** — use for asset IDs, bundle generation, `build_runtime_assets.py`, mirrored client/server asset loaders/helpers, collision-mask assets, and other runtime asset/pipeline changes; route attribution-only follow-up through the narrower prompt/docs path.
- **Delivery & Launch Config** — use for canonical entrypoints, `pyproject.toml` / installed console scripts, `.env` lookup, `BETTER_TOGETHER_ENV_FILE`, runtime-role startup flow, macOS launchers, and setup-flow docs.
- **Repo Change Surface Map** — use as a read-only planning agent to map files, docs, tests, risks, and likely next workflow before editing, especially across risky client/server/shared boundaries.

## Instruction files

- **Project-wide:** `.github/copilot-instructions.md`
- **Networking:** `.github/instructions/networking.instructions.md`
- **Player snapshot compatibility:** `.github/instructions/player-snapshot-compatibility.instructions.md`
- **Assets/runtime:** `.github/instructions/assets-runtime.instructions.md`
- **Gameplay ownership:** `.github/instructions/gameplay-runtime.instructions.md`
- **Launch/config:** `.github/instructions/launch-config.instructions.md`

Use the most specific instruction or agent when a task crosses one of those change surfaces.

## Skills

- **Change Validation** — choose the right automated baseline and manual smoke checks for a change.
- **Unittest Regression Authoring** — add repo-style `unittest` coverage, mocks, and bug repro tests.
- **Gameplay Feature Workflow** — review gameplay/HUD changes and client-vs-server ownership questions.
- **Network Room Change Playbook** — review protocol, room lifecycle, handshake, matchmaking, and snapshot compatibility work.
- **Server Simulation & AI Playbook** — review server-owned AI movement, pirate ships, simulation ticks, and other server-owned state.
- **Asset Pipeline Maintainer** — review asset catalog, runtime bundle generation, mirrored asset helpers, and attribution work.
- **Launcher Config Entrypoints** — review launchers, `.env` lookup, entrypoints, and startup-flow behavior.

## Prompt files

- **Change Surface Triage** — route a bug, feature, or refactor to the right files, tests, docs, and repo customizations before editing.
- **Regression Matrix** — suggest the right automated checks and manual smoke steps for a change.
- **Doc Sync** — draft the documentation delta after code changes.
- **Asset Attribution Update** — prepare `docs/assets-licenses.md` and `credits/` follow-up for art changes.

## Choosing the right primitive

- Use a **skill** when you want planning, triage, validation, or a reusable workflow before editing.
- Use the **Repo Change Surface Map** agent when you want a read-only files/docs/tests/risk map before editing.
- Use a **custom agent** when the task spans a risky multi-file surface and is ready for an implementation-focused specialized workflow.
- Use an **instruction file** when the guidance should apply automatically for matching files.
- Use a **prompt** when you want a narrow, repeatable output without a dedicated agent persona.

For repo-specific runtime guardrails, rely on `.github/copilot-instructions.md` and `docs/architecture.md` rather than treating this file as the source of truth for implementation details.
