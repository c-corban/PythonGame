---
name: better-together-change-validation
description: 'Use when validating Better-Together changes, choosing unittest coverage, running baseline checks, deciding whether manual smoke tests are needed, or checking headless, launcher, or networking impacts.'
argument-hint: 'Describe the changed files, subsystem, or regression you want to validate.'
---

# Better-Together Change Validation

## When to Use

- After implementing a change and before calling the work done.
- When you are unsure which `unittest` modules match a change.
- When you need to decide whether a manual smoke test, headless integration check, or launcher/config verification is required.

## Procedure

1. Classify the change surface with `docs/contributing.md` and the workspace instructions. Distinguish docs-only, client gameplay/rendering, networking/room lifecycle, assets, and launcher/config work.
2. Start from the repo baseline from the repository root:
   - `python scripts/build_runtime_assets.py --check`
   - `python -m unittest discover -s tests -v`
   Narrow or skip only when the user explicitly wants partial validation or the change is docs-only.
3. Use the [test matrix](./references/test-matrix.md) to add targeted automated checks for the touched area.
4. If the change touches runtime behavior, rendering, input, networking, or launch/setup flow, follow the [runtime smoke checklist](./references/runtime-smoke-checklist.md) and be explicit about what still needs a human desktop session.
5. Summarize validation clearly: what ran, what passed, what was not run, and why.

## References

- [Test matrix](./references/test-matrix.md)
- [Runtime smoke checklist](./references/runtime-smoke-checklist.md)
