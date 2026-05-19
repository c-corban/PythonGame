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
| How do I install, launch, or smoke-test the prototype? | `README.md` for the shortest path, then `docs/quickstart.md` | `README.md` stays concise; `docs/quickstart.md` owns the full setup, launch, and smoke-test flow. |
| How does the client/server/shared split work today? | `docs/architecture.md` | This is the implementation-facing explanation of runtime ownership, protocol flow, room lifecycle, and asset/runtime caveats. |
| What gameplay exists right now versus the original concept? | `docs/gameplay-status.md`, then `reference/game-concept.md` | `docs/gameplay-status.md` is the live “vision versus shipped prototype” snapshot; `reference/game-concept.md` preserves the original design note it compares against. |
| What files, docs, tests, and risks will this change touch before I edit? | `.github/prompts/change-surface-triage.prompt.md`, then `.github/agents/repo-change-surface.agent.md` | The prompt is the fastest narrow triage entry point, the agent expands that into a broader files/docs/tests/risk map, and `docs/contributing.md` owns the repo-risk and validation guidance once the surface is clear. |
| Where do asset licenses and provenance live? | `docs/assets-licenses.md` and `credits/` | The doc summarizes the asset inventory; `credits/` keeps the raw source notes. |
| How do logical asset IDs, bundle targets, or asset regeneration work? | `src/better_together_shared/asset_catalog.py`, then `src/better_together_shared/asset_pipeline.py`, `scripts/build_runtime_assets.py`, and `docs/architecture.md` | `asset_catalog.py` is the code-owned truth for logical IDs and preferred build inputs, `asset_pipeline.py` owns the actual build/validation behavior, the script is the CLI entrypoint, and `docs/architecture.md` explains how the runtime uses them. |
| How do I decide which automated checks or smoke tests to run? | `docs/quickstart.md#canonical-automated-baseline`, then `docs/contributing.md` | `docs/quickstart.md` owns the baseline commands; `docs/contributing.md` owns the change-risk and manual verification flow around them. |
| I changed code; which summary docs should I sync? | `docs/knowledge-base.md`, then `.github/prompts/doc-sync.prompt.md` | Start here for doc ownership; use the prompt when you want a narrow drafted follow-up once the change surface is known. |
| Which Copilot customization should I reach for first? | `AGENTS.md`, then the most specific matching entry in `.github/prompts/`, `.github/skills/`, `.github/instructions/`, or `.github/agents/` | `AGENTS.md` is the quick inventory; from there, choose the most specific primitive instead of browsing `.github/` blindly. |

## AI-assisted work at a glance

| Need | Start with | Why |
| --- | --- | --- |
| Documentation ownership or update routing | `docs/knowledge-base.md` | This file maps the live docs and tells you what should move together. |
| Always-on AI guardrails and canonical repo expectations | `.github/copilot-instructions.md` | This is the default AI overlay for canonical commands, documentation expectations, and repo guardrails. |
| File-targeted guardrails for risky edits | `.github/instructions/` | These are scope-specific overlays for matching files; use the most specific one that fits. |
| Narrow one-shot outputs such as change triage, doc sync, attribution follow-up, or a regression matrix | `.github/prompts/` | Prompts are the fastest primary entry point when you already know the exact output you want. |
| Reusable workflows for planning, validation, test authoring, or area-specific review | `.github/skills/` | Skills package a repeatable workflow plus supporting references. |
| Implementation-focused multi-file work or a read-only impact map | `.github/agents/` | Most agents are implementation specialists; `repo-change-surface` is the read-only planning exception. |

Rule of thumb: `docs/` own repo facts, `.github/copilot-instructions.md` and `.github/instructions/` overlay AI guardrails, prompts are best for narrow outputs, skills are reusable workflows, and agents are for implementation or broader impact maps. Start with the most specific thing that fits the task.

## Common exact entry points

Use this table when you already know the kind of help you want and need the fastest concrete starting point inside `.github/`.

| Task | Start with | Escalate when needed |
| --- | --- | --- |
| Read-only change triage before editing | `.github/prompts/change-surface-triage.prompt.md` | `.github/agents/repo-change-surface.agent.md` for a broader files/docs/tests/risk map |
| Validation planning and smoke-test selection | `.github/skills/better-together-change-validation/` | `.github/prompts/regression-matrix.prompt.md` for a narrow regression checklist |
| Docs-only follow-up after code changes | `.github/prompts/doc-sync.prompt.md` | `docs/knowledge-base.md` if the owning summary doc is still unclear |
| Launch/config/startup work | `.github/instructions/launch-config.instructions.md` | `.github/skills/better-together-launcher-config-entrypoints/` for workflow guidance, then `.github/agents/delivery-launch-config.agent.md` for implementation |
| Networking, room lifecycle, or transport framing | `.github/skills/better-together-network-room-change-playbook/` | `.github/agents/runtime-network-protocol.agent.md` or `.github/agents/runtime-room-lifecycle.agent.md` when you are ready to edit |
| Player snapshot compatibility | `.github/instructions/player-snapshot-compatibility.instructions.md` | `.github/skills/better-together-network-room-change-playbook/` for change-surface guidance, then `.github/agents/runtime-network-protocol.agent.md` if the live wire shape changes |
| Gameplay/HUD or client-vs-server ownership work | `.github/skills/better-together-gameplay-feature-workflow/` | `.github/agents/client-gameplay-hud.agent.md` or `.github/agents/runtime-state-ownership.agent.md` |
| Server simulation, AI ticks, or other server-owned gameplay state | `.github/skills/better-together-server-simulation-ai-playbook/` | `.github/agents/runtime-room-lifecycle.agent.md` or `.github/agents/runtime-state-ownership.agent.md` when the change spills into room lifecycle or ownership boundaries |
| Asset catalog, bundle generation, or logical asset IDs | `.github/skills/better-together-asset-pipeline-maintainer/` | `.github/agents/assets-bundle-pipeline.agent.md` |
| Headless-safe image loading or display-surface-sensitive runtime work | `.github/instructions/assets-runtime.instructions.md` | `.github/agents/client-headless-safe-runtime.agent.md` |
| Attribution-only asset follow-up | `.github/prompts/asset-attribution-update.prompt.md` | `docs/assets-licenses.md` and `credits/` once the code-owned asset surface is settled |
| Add or refine regression tests | `.github/skills/better-together-unittest-regression-authoring/` | `tests/` plus the relevant surface doc once the bug or change surface is clear |

## Repository knowledge layers

| Surface | Primary audience | Owns | Notes |
| --- | --- | --- | --- |
| `README.md` | Everyone | Project overview, shortest safe startup path, top-level doc index | Keep this high-signal and lightweight. |
| `docs/knowledge-base.md` | Contributors and AI-assisted workflows | KB navigation, doc ownership, update routing | Update this when the documentation/customization map changes. |
| `docs/quickstart.md` | Contributors running the prototype | Detailed install, canonical automated baseline, launch order, smoke-test steps, setup caveats | This is the operational setup guide. |
| `docs/architecture.md` | Contributors touching runtime behavior | Current runtime boundaries, room lifecycle, protocol contract, state ownership, asset/runtime caveats | Prefer this over summaries when architecture details matter. |
| `docs/gameplay-status.md` | Contributors changing player-visible behavior | Current playable loop versus original design vision | Keep this synchronized with meaningful gameplay changes. |
| `docs/contributing.md` | Contributors planning changes | Repo map, risk guidance, safe change surfaces, change-specific verification flow | This is the “what should I touch, and how carefully?” guide. |
| `docs/assets-licenses.md` | Contributors changing assets | Asset inventory, attribution record, provenance notes, open follow-up items | Pair with `credits/` for raw source notes. |
| `tests/` | Contributors validating changes | Executable coverage for startup/config, protocol/transport, client runtime helpers, server room/simulation invariants, mirrored asset helpers | Review the surface-specific tests before and after risky changes. |
| `src/better_together_shared/asset_catalog.py` | Contributors changing runtime packaging | Logical asset IDs, preferred build inputs, runtime bundle targets | This is a code-owned exception: trust it for runtime packaging facts, then sync the docs to match. |
| `src/better_together_shared/asset_pipeline.py` | Contributors changing runtime packaging | Build strategies, output-path resolution, and validation/regeneration semantics for the package-local runtime bundles | Treat this as the implementation-owned bundle builder that turns catalog metadata into concrete runtime outputs. |
| `scripts/build_runtime_assets.py` | Contributors changing assets or runtime bundle layout | CLI entrypoint for validation and regeneration of the package-local runtime bundles | This script is the operational front door into `asset_pipeline.py`; use `--check` as the default baseline. |
| `AGENTS.md` | Contributors using Copilot | Quick map of agents, instructions, prompts, skills, and customization guardrails | Treat this as the human-friendly inventory of `.github/`, not the canonical source of repo facts. |
| `.github/copilot-instructions.md` | AI agents | Always-on repo guidance, guardrails, canonical commands, documentation expectations | Guardrail overlay for AI work; keep it aligned with the docs and code-owned truth sources above. |
| `.github/instructions/` | AI agents editing matched files | File-targeted guardrails for risky surfaces | Scope-specific guardrail overlays, not competing fact stores. |
| `.github/agents/` | AI agents doing risky multi-file work | Specialized workflows by change surface | Most are implementation-focused; `repo-change-surface` is the read-only planning exception. |
| `.github/skills/` | AI agents on demand | Reusable workflows plus supporting references | Use when you want a guided workflow; prompts may still be the better front door for narrow tasks. |
| `.github/prompts/` | AI agents on demand | Narrow repeatable outputs such as change triage, doc sync, regression planning, attribution follow-up | Use when you want a focused output instead of a broader workflow. |
| `reference/game-concept.md` | Contributors comparing the prototype to the original vision | Original high-level design note for the game concept | Use it alongside `docs/gameplay-status.md`, not instead of the live docs. |
| `reference/` | Contributors researching history | Historical design notes, raw license texts, research material | Do not treat this as the current implementation source of truth. |
| `credits/` | Contributors validating provenance | Raw attribution and source notes per asset | Supporting material, not the curated runtime/behavior docs. |

## Canonical update map

| If you change... | Update these first | Also review |
| --- | --- | --- |
| Setup, launch flow, entrypoints, or `.env` behavior | `README.md`, `docs/quickstart.md` | `.github/copilot-instructions.md`, `.github/instructions/launch-config.instructions.md`, `tests/test_config.py`, `tests/test_package_entrypoints.py`, and `tests/test_macos_launchers.py` |
| Protocol flow, room lifecycle, transport framing, or runtime ownership | `docs/architecture.md` | `.github/copilot-instructions.md`, the matching `.github/instructions/`, and the protocol/transport/room tests in `tests/` |
| Gameplay loop, prompts/HUD flow, or the current shipped feature set | `docs/gameplay-status.md` | `docs/architecture.md` if the client/server ownership split or wire-visible behavior changed, plus the matching gameplay/AI `.github` workflow |
| Contributor workflow, risk guidance, or validation expectations | `docs/contributing.md` | `docs/knowledge-base.md` if routing changed, plus `.github/copilot-instructions.md` when AI-facing expectations changed |
| Canonical automated baseline, asset-build check expectations, or smoke-test flow | `docs/quickstart.md`, `docs/contributing.md` | `.github/copilot-instructions.md`, `.github/skills/better-together-change-validation/`, `scripts/build_runtime_assets.py`, and the affected `tests/` coverage |
| Runtime packaging facts: logical asset IDs, bundle targets, headless-safe asset loading, or regeneration flow | `docs/architecture.md`, then `docs/quickstart.md` when contributor workflow changes, plus `docs/assets-licenses.md` and `credits/` when preferred asset sources or provenance changed | `src/better_together_shared/asset_catalog.py`, `src/better_together_shared/asset_pipeline.py`, `scripts/build_runtime_assets.py`, `.github/instructions/assets-runtime.instructions.md`, mirrored asset loaders, and asset/runtime tests in `tests/` |
| Asset provenance or attribution | `docs/assets-licenses.md`, `credits/` | `src/better_together_shared/asset_catalog.py` if IDs or build inputs changed, plus `.github/prompts/asset-attribution-update.prompt.md` for follow-up drafting |
| AI customization discovery, naming, or routing | `AGENTS.md`, `.github/copilot-instructions.md`, and the specific `.github` file you changed | `docs/knowledge-base.md` if contributor-facing routing changed |

## High-risk change surfaces at a glance

Use this table when a change crosses a risky runtime seam and you want the shortest path to the right docs, validations, and AI customization.

| Surface | Start with | Also review |
| --- | --- | --- |
| Launch/config/startup behavior | `docs/quickstart.md`, then `README.md` | `.github/instructions/launch-config.instructions.md`, `.github/skills/better-together-launcher-config-entrypoints/`, `.github/agents/delivery-launch-config.agent.md`, and the startup/config tests in `tests/` |
| Networking, room lifecycle, and transport framing | `docs/architecture.md` | `.github/instructions/networking.instructions.md`, `.github/skills/better-together-network-room-change-playbook/`, `.github/agents/runtime-network-protocol.agent.md`, `.github/agents/runtime-room-lifecycle.agent.md`, and the protocol/transport/room tests in `tests/` |
| Player snapshot compatibility | `docs/architecture.md` | `.github/instructions/player-snapshot-compatibility.instructions.md`, `.github/skills/better-together-network-room-change-playbook/`, `.github/agents/runtime-network-protocol.agent.md`, and `tests/test_protocol.py` plus `tests/test_server_protocol.py` |
| Gameplay ownership, prompts, HUD flow, and the current client/server split | `docs/gameplay-status.md`, then `docs/architecture.md` | `.github/instructions/gameplay-runtime.instructions.md`, `.github/skills/better-together-gameplay-feature-workflow/`, `.github/agents/client-gameplay-hud.agent.md`, and `.github/agents/runtime-state-ownership.agent.md` |
| Server simulation, AI movement, projectiles, damage markers, and other server-owned state | `docs/architecture.md`, then `docs/gameplay-status.md` | `.github/skills/better-together-server-simulation-ai-playbook/`, `.github/agents/runtime-room-lifecycle.agent.md`, `.github/agents/runtime-state-ownership.agent.md` when ownership boundaries move, and the room/simulation tests in `tests/` |
| Asset catalog, runtime bundles, and logical asset IDs | `src/better_together_shared/asset_catalog.py`, `src/better_together_shared/asset_pipeline.py`, `scripts/build_runtime_assets.py`, then `docs/architecture.md` | `.github/instructions/assets-runtime.instructions.md`, `.github/skills/better-together-asset-pipeline-maintainer/`, `.github/agents/assets-bundle-pipeline.agent.md`, and the asset/runtime tests in `tests/` |
| Headless-safe image loading and display-surface behavior | `docs/architecture.md`, then the mirrored `src/better_together_client/assets.py` / `src/better_together_server/assets.py` loaders | `.github/instructions/assets-runtime.instructions.md`, `.github/agents/client-headless-safe-runtime.agent.md`, and the asset/runtime tests in `tests/` |

## Overlap that is intentional

Some repetition is useful; the goal is to keep it scoped.

- `README.md` and `docs/quickstart.md` both mention the canonical entrypoints. `README.md` is the short path; `docs/quickstart.md` owns the operational detail.
- `docs/contributing.md` and `AGENTS.md` both name the same risky surfaces on purpose. `docs/contributing.md` explains repo risk, coupled files, and verification expectations; `AGENTS.md` tells you which Copilot instructions, prompts, skills, or agents map to those surfaces.
- `.github/copilot-instructions.md` repeats a subset of repo facts from `docs/`. That duplication is intentional because AI agents need stable standalone guidance even when they have not opened every topic doc yet.

## When documents disagree

Use this precedence ladder:

1. code-owned truth sources when the repo intentionally makes them authoritative — especially `src/better_together_shared/asset_catalog.py` for logical asset IDs and preferred build inputs, `src/better_together_shared/asset_pipeline.py` for runtime bundle build/validation semantics, and `scripts/build_runtime_assets.py` for the operational CLI entrypoint into that pipeline,
2. focused topic docs in `docs/` for contributor-facing facts and update ownership,
3. summary docs such as `README.md`, `docs/knowledge-base.md`, and `AGENTS.md`,
4. `.github/copilot-instructions.md` and `.github/instructions/*` as AI guardrail overlays that should agree with the sources above, not compete with them,
5. `reference/` and other historical/raw provenance material.

If a focused doc and a summary disagree, fix the summary. If an AI guardrail disagrees with the docs or a code-owned truth source, fix the `.github` file. If docs drift from a code-owned packaging fact, update the docs instead of papering over the mismatch.

## Maintenance habit

If you add a new top-level doc that contributors should discover, update this file and the `README.md` documentation index in the same branch.

If you change contributor-facing commands, launch flow, validation expectations, or AI routing, update the owning `docs/` page, the matching `.github` guidance, and any affected summary docs in the same branch.

If you rename or remove docs, commands, tests, prompts, skills, agents, or key files called out here, clean up stale references repo-wide (`README.md`, `docs/`, `AGENTS.md`, `.github/`, and related tests/scripts) before finishing.

Validate doc-sync changes against the current repo state: run the affected checks when behavior changed, or at minimum cross-check the owning code/script/test surface so the guidance stays evidence-based.
