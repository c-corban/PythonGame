---
description: "Suggest Better-Together automated tests and manual smoke checks for a described change set or selected files."
name: "Regression Matrix"
argument-hint: "Describe the changed files, subsystem, or diff summary."
agent: "agent"
tools: [read, search]
---
Create a Better-Together regression matrix for the described change.

- Classify the change surface using `docs/knowledge-base.md`, `docs/contributing.md`, `docs/architecture.md`, and `.github/copilot-instructions.md`.
- Recommend the smallest credible automated checks first.
- Include `python scripts/build_runtime_assets.py --check` and `python -m unittest discover -s tests -v` when the change is not docs-only.
- Call out manual smoke steps only when rendering, input, networking, multiplayer room behavior, or launch/setup flow changed.
- If a change is docs-only, explicitly say which automated/runtime checks can be skipped.

Output sections:

1. `Automated checks`
2. `Manual smoke checks`
3. `Why these checks`
4. `What can be skipped`
