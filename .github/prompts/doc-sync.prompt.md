---
description: "Draft Better-Together documentation updates after gameplay, networking, launch-flow, or asset changes."
name: "Doc Sync"
argument-hint: "Describe the code changes or the docs that may need updates."
agent: "agent"
tools: [read, search]
---
Review the described Better-Together change and draft the documentation delta.

- Decide which docs should change among `README.md`, `docs/knowledge-base.md`, `docs/quickstart.md`, `docs/architecture.md`, `docs/gameplay-status.md`, `docs/contributing.md`, `docs/assets-licenses.md`, and `credits/`.
- Use `docs/knowledge-base.md` when the change affects documentation ownership, navigation, or where contributors should look first.
- Use the repo architecture and contributor guidance to justify each recommendation.
- Prefer concise, merge-ready bullets or paragraphs instead of vague reminders.
- Call out when no documentation update is needed.

Output sections:

1. `Docs to update`
2. `Suggested edits`
3. `Why each doc matters`
4. `Docs that can stay unchanged`
