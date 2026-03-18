# Knowledge base map

This file is the routing guide for Better-Together's live knowledge base.

Use it when you need to answer any of these quickly:

- Where should I look first for a fact about the project?
- Which doc should move with a change?
- Is a file live guidance, historical background, or raw provenance?
- Which `.github` customization matches a task?

This file does **not** replace the topic docs it points to. Its job is to keep navigation, ownership, and update routing easy to trust.

## Start here by question

| Question | Primary source | Why |
| --- | --- | --- |
| How do I install, launch, or smoke-test the prototype? | `README.md` for the shortest path, then `docs/quickstart.md` | `README.md` stays concise; `docs/quickstart.md` owns the full setup and launch flow. |
| How does the client/server/shared split work today? | `docs/architecture.md` | This is the implementation-facing explanation of runtime ownership, protocol flow, room lifecycle, and asset/runtime caveats. |
| What gameplay exists right now versus the original concept? | `docs/gameplay-status.md`, then `reference/game-concept.md` | `docs/gameplay-status.md` is the canonical “vision versus shipped prototype” snapshot, while `reference/game-concept.md` preserves the original design note it compares against. |
| What files, docs, tests, and risks will this change touch before I edit? | `.github/agents/repo-change-surface.agent.md`, then `docs/contributing.md` | The repo-change-surface agent gives a read-only impact map before editing, and `docs/contributing.md` owns the contributor-facing risk and validation guidance. |
| Where do asset licenses and provenance live? | `docs/assets-licenses.md` and `credits/` | The doc summarizes the asset inventory; `credits/` keeps the raw source notes. |
| How do runtime bundles, asset IDs, or asset regeneration work? | `docs/architecture.md`, then `docs/quickstart.md` and `scripts/build_runtime_assets.py` | `docs/architecture.md` explains the runtime behavior, while `docs/quickstart.md` and the build script own the validation and regeneration flow. |
| How do I decide which automated checks or smoke tests to run? | `docs/quickstart.md#canonical-automated-baseline`, then `docs/contributing.md` | `docs/quickstart.md` owns the canonical baseline commands, while `docs/contributing.md` owns the broader manual verification checklist and change-risk guidance. |
| I changed code; which summary docs should I sync? | `docs/knowledge-base.md`, then `.github/prompts/doc-sync.prompt.md` | Start here for document ownership; use the doc-sync prompt when you want a narrow drafted follow-up once the change surface is known. |
| What AI/customization workflow should I use? | `AGENTS.md`, then `.github/` | `AGENTS.md` is the quick human-readable map of the workspace-shared agents, instructions, prompts, and skills. |

## AI-assisted work at a glance

| Need | Start with | Why |
| --- | --- | --- |
| Documentation ownership or update routing | `docs/knowledge-base.md` | This file maps the live docs and tells you what should move together. |
| Always-on AI guardrails and canonical repo expectations | `.github/copilot-instructions.md` | This is the default rule set AI agents should keep in context. |
| File-targeted rules for risky surfaces | `.github/instructions/` | These are the scoped guardrails that apply when matching files are edited. |
| Planning, triage, validation, or reusable references/checklists | `.github/skills/`, then `.github/prompts/` | Skills are the broader front door for planning and validation; prompts are better for narrow one-shot triage, doc-sync, and regression-planning tasks. |
| An implementation-focused multi-file workflow or read-only impact map | `.github/agents/` | Most agents are implementation specialists once the task is ready for editing; `repo-change-surface` is the read-only planning exception. |

Rule of thumb: `docs/` own facts and update routing, `.github/instructions/` add file-scoped guardrails, `.github/prompts/` handle narrow one-shot outputs, `.github/skills/` handle planning/validation or reusable workflows, and `.github/agents/` handle implementation-focused or read-only impact-mapping work. When you are still planning, prefer prompts or skills before implementation-focused agents.

## Common exact entry points

Use this table when you already know the kind of help you want and need the fastest concrete starting point inside `.github/`.

| Task | Start with | Escalate when needed |
| --- | --- | --- |
| Read-only change triage before editing | `.github/prompts/change-surface-triage.prompt.md` | `.github/agents/repo-change-surface.agent.md` for a broader files/docs/tests/risk map |
| Validation planning and smoke-test selection | `.github/skills/better-together-change-validation/` | `.github/prompts/regression-matrix.prompt.md` for a narrow regression plan |
| Docs-only follow-up after code changes | `.github/prompts/doc-sync.prompt.md` | `docs/knowledge-base.md` if the owning summary doc is still unclear |
| Launch/config/startup work | `.github/skills/better-together-launcher-config-entrypoints/` | `.github/agents/delivery-launch-config.agent.md` once the task is ready for implementation |
| Networking, room lifecycle, or snapshot compatibility work | `.github/skills/better-together-network-room-change-playbook/` | `.github/agents/runtime-network-protocol.agent.md` or `.github/agents/runtime-room-lifecycle.agent.md` when you are ready to edit |
| Gameplay/HUD or state-ownership work | `.github/skills/better-together-gameplay-feature-workflow/` | `.github/agents/client-gameplay-hud.agent.md` or `.github/agents/runtime-state-ownership.agent.md` |
| Assets, runtime bundles, headless-safe loading, or attribution work | `.github/skills/better-together-asset-pipeline-maintainer/` or `.github/prompts/asset-attribution-update.prompt.md` | `.github/agents/assets-bundle-pipeline.agent.md` or `.github/agents/client-headless-safe-runtime.agent.md` when implementation work begins |
| Add or refine regression tests | `.github/skills/better-together-unittest-regression-authoring/` | `tests/` plus the relevant surface doc once the bug or change surface is clear |

## Repository knowledge layers

| Surface | Primary audience | Owns | Notes |
| --- | --- | --- | --- |
| `README.md` | Everyone | Project overview, shortest safe startup path, top-level doc index | Keep this high-signal and lightweight. |
| `docs/knowledge-base.md` | Contributors and AI-assisted workflows | KB navigation, doc ownership, update routing | Update this when the documentation/customization map changes. |
| `docs/quickstart.md` | Contributors running the prototype | Detailed install, canonical automated baseline, launch order, smoke-test steps, current setup caveats | This is the operational setup guide. |
| `docs/architecture.md` | Contributors touching runtime behavior | Current runtime boundaries, room lifecycle, protocol contract, state ownership, asset/runtime caveats | Prefer this over summaries when architecture details matter. |
| `docs/gameplay-status.md` | Contributors changing player-visible behavior | Current playable loop versus original design vision | Keep this synchronized with meaningful gameplay changes. |
| `docs/contributing.md` | Contributors planning changes | Repo map, risk guidance, safe change surfaces, and change-specific verification flow after the shared baseline | This is the “what should I touch, and how carefully?” guide. |
| `docs/assets-licenses.md` | Contributors changing assets | Asset inventory, attribution record, bundle/source-of-truth notes, and open follow-up items | Pair with `credits/` for raw source notes. |
| `tests/` | Contributors validating changes | Automated coverage for startup/config, protocol/transport, client runtime helpers, server room/simulation invariants, and mirrored asset helpers | Review the surface-specific tests before and after risky changes. |
| `scripts/build_runtime_assets.py` | Contributors changing assets or runtime bundle layout | Validation and regeneration of the package-local runtime bundles | Use `--check` as the default baseline; run the full build after asset-catalog or source-asset changes. |
| `AGENTS.md` | Contributors using Copilot | Quick map of agents, instructions, prompts, skills, and customization guardrails | Treat this as the human-friendly entry point to `.github/`. |
| `.github/copilot-instructions.md` | AI agents | Always-on repo guidance, guardrails, canonical commands, documentation expectations | This repeats some repo facts intentionally so the AI has a stable default context. |
| `.github/instructions/` | AI agents editing matched files | File-targeted guardrails for risky surfaces | Use these for always-on, scope-specific rules. |
| `.github/agents/` | AI agents doing risky multi-file work | Specialized workflows by change surface | Most are implementation-focused; `repo-change-surface` is the read-only planning exception. |
| `.github/skills/` | AI agents on demand | Reusable workflows plus reference material | Good for planning, triage, validation, testing, or area-specific implementation workflows, and often the better front door before editing. |
| `.github/prompts/` | AI agents on demand | Narrow repeatable tasks such as change triage, doc sync, and regression planning | Use when you want a focused output instead of a broader workflow. |
| `reference/game-concept.md` | Contributors comparing the prototype to the original vision | Original high-level design note for the game concept | Use it alongside `docs/gameplay-status.md`, not instead of the live docs. |
| `reference/` | Contributors researching history | Historical design notes, raw license texts, research material | Do not treat this as the current implementation source of truth. |
| `credits/` | Contributors validating provenance | Raw attribution and source notes per asset | This is supporting material, not the curated runtime/behavior docs. |

## Canonical update map

| If you change... | Update these first | Also review |
| --- | --- | --- |
| Setup, launch flow, entrypoints, or `.env` behavior | `README.md`, `docs/quickstart.md` | `.github/instructions/launch-config.instructions.md` and the launch/config customization files if discovery wording changes |
| Protocol flow, room lifecycle, networking semantics, or runtime ownership | `docs/architecture.md` | `docs/gameplay-status.md` if the player-visible loop changes, plus the relevant `.github/instructions/`, `.github/agents/`, and `.github/skills/` entries |
| Gameplay loop, prompts, HUD flow, or current shipped feature set | `docs/gameplay-status.md` | `docs/architecture.md` if ownership or network-visible behavior changed |
| Contributor workflow, risk guidance, or validation expectations | `docs/contributing.md` | `docs/knowledge-base.md` if the guidance changes where contributors should look first |
| Automated baseline commands, test coverage expectations, or manual verification flow | `docs/quickstart.md#canonical-automated-baseline`, `docs/contributing.md` | `tests/`, `.github/skills/better-together-change-validation/`, and `scripts/build_runtime_assets.py` when asset/runtime bundle behavior is involved |
| Asset inventory, attribution, runtime bundle sources, or provenance | `docs/assets-licenses.md`, `credits/` | `README.md` or `docs/quickstart.md` if the source-of-truth or asset-generation workflow changes |
| AI customization discovery, naming, or routing | `AGENTS.md`, `.github/copilot-instructions.md`, and the specific `.github` file you changed | `docs/knowledge-base.md` if the overall map changed |

## High-risk change surfaces at a glance

Use this table when a change crosses a risky runtime seam and you want the shortest path to the right docs, validations, and AI customization.

| Surface | Start with | Also review |
| --- | --- | --- |
| Launch/config/startup behavior | `README.md`, then `docs/quickstart.md` | `.github/instructions/launch-config.instructions.md` plus the startup/config tests in `tests/` |
| Networking, room lifecycle, and transport framing | `docs/architecture.md` | `.github/instructions/networking.instructions.md`, `.github/skills/better-together-network-room-change-playbook/`, and the protocol/transport/room tests in `tests/` |
| Player snapshot compatibility | `docs/architecture.md` | `.github/instructions/player-snapshot-compatibility.instructions.md` and the protocol/snapshot coverage in `tests/` |
| Gameplay ownership, prompts, and HUD flow | `docs/gameplay-status.md`, then `docs/architecture.md` | `.github/instructions/gameplay-runtime.instructions.md` and `.github/skills/better-together-gameplay-feature-workflow/` |
| Server simulation, AI, and other server-owned gameplay state | `docs/architecture.md`, then `docs/gameplay-status.md` | `.github/skills/better-together-server-simulation-ai-playbook/` and the room/simulation tests in `tests/` |
| Assets, runtime bundles, and headless-safe loading | `docs/assets-licenses.md`, `docs/architecture.md`, then `docs/quickstart.md` | `.github/instructions/assets-runtime.instructions.md`, `.github/agents/client-headless-safe-runtime.agent.md`, `.github/skills/better-together-asset-pipeline-maintainer/`, and `scripts/build_runtime_assets.py` |

## Overlap that is intentional

Some repetition is useful; the goal is to keep it scoped.

- `README.md` and `docs/quickstart.md` both mention the canonical entrypoints. `README.md` is the short path; `docs/quickstart.md` owns the operational detail.
- `docs/contributing.md` and `AGENTS.md` both mention the `.github` layer. `docs/contributing.md` explains when contributor workflows or docs should move; `AGENTS.md` enumerates the available customization primitives.
- `.github/copilot-instructions.md` repeats a subset of repo facts from `docs/`. That duplication is intentional because AI agents need stable standalone guidance even when they have not opened every doc yet.

## When documents disagree

Use this priority order:

1. the focused topic doc in `docs/`,
2. then the high-level summary (`README.md`, `AGENTS.md`, or this map),
3. then `reference/` only for historical background.

If a focused doc and a summary disagree, update the summary to match the focused doc and the current code behavior.

## Maintenance habit

If you add a new top-level doc that contributors should discover, update this file and the `README.md` documentation index in the same branch.

If you add, rename, or remove a repository customization that contributors should discover, update this file, `AGENTS.md`, and any affected summary guidance such as `.github/copilot-instructions.md` in the same branch.

If you add a new contributor-facing validation surface such as a new baseline command, a new high-value test area, or a new asset-build workflow, update this file together with `docs/quickstart.md` or `docs/contributing.md` so the routing stays accurate.
