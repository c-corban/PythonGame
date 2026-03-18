---
description: "Route a Better-Together bug, feature, or refactor to the right files, tests, docs, and repo customizations before editing."
name: "Change Surface Triage"
argument-hint: "Describe the bug, feature, or refactor you want to map."
agent: "agent"
tools: [read, search]
---
Map the Better-Together change surface before implementation.

- Classify whether the request is primarily gameplay, networking/protocol, server simulation, assets, launch/config, docs, or mixed. Use `docs/knowledge-base.md` to route contributor docs versus the `.github` customization layer.
- Recommend the most relevant files, coupled dependencies, tests, and docs.
- Point to the most relevant repo customizations under `.github/instructions/`, `.github/skills/`, `.github/prompts/`, and `.github/agents/`.
- Call out the top risks or invariants before editing.

Output sections:

1. `Primary change surface`
2. `Files and dependencies`
3. `Tests and docs`
4. `Recommended repo customizations`
5. `Top risks`
