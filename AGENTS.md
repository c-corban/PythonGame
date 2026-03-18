# Better-Together agent map

This repository ships workspace-shared Copilot customizations so contributors can use the most specific workflow for high-risk change surfaces.

Use this file when you want the shortest path to the right agent, instruction, prompt, or skill.

For the broader documentation and update-ownership map, start with `docs/knowledge-base.md`.

## Start here

- Documentation ownership and update routing → `docs/knowledge-base.md`
- Quick customization routing → `AGENTS.md`
- Always-on AI guardrails → `.github/copilot-instructions.md`

## Custom agents

- **Runtime Network & Protocol** — use for `player_assignment`, `player_update`, `room_state`, snapshot compatibility, socket framing, protocol versioning, and room-lifecycle-adjacent networking changes.
- **Runtime Room Lifecycle** — use for room creation, AI slot reuse, matchmaking, disconnect cleanup, and empty-room deletion behavior.
- **Runtime State Ownership** — use when deciding whether gameplay behavior belongs in the client, server, or shared protocol layer.
- **Client Gameplay & HUD** — use for prompts, aiming, reload flow, repair interaction text, shoot animation, and game-over presentation.
- **Client Headless-Safe Runtime** — use for Pygame display setup, image conversion, render initialization, and protecting headless server support.
- **Runtime Asset Bundle & Pipeline** — use for asset IDs, bundle generation, `build_runtime_assets.py`, mirrored client/server asset helpers, collision-mask assets, and attribution updates.
- **Delivery & Launch Config** — use for `.env` lookup, `BETTER_TOGETHER_ENV_FILE`, CLI/app entrypoints, macOS launchers, and setup-flow docs.
- **Repo Change Surface Map** — use as a read-only planning agent to map files, docs, tests, and risks before editing.

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
