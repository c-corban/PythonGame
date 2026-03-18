---
name: better-together-launcher-config-entrypoints
description: 'Use when reviewing or planning Better-Together launchers, cli.py or __main__.py entrypoints, package scripts, BETTER_TOGETHER_ENV_FILE resolution, runtime-role env behavior, or startup flow on macOS/raw checkouts.'
argument-hint: 'Describe the launcher, config, or entrypoint change you want to make.'
---

# Better-Together Launcher, Config, and Entrypoint Workflow

## When to Use

- Editing `Launch Better Together *.command` launchers.
- Editing `cli.py`, `__main__.py`, startup flow, or package entrypoints.
- Debugging `.env` resolution, `BETTER_TOGETHER_ENV_FILE`, runtime-role behavior, or raw-checkout launch issues.

## Procedure

1. Start with the [startup surface map](./references/startup-surface-map.md). Keep launchers, package entrypoints, runtime-role setup, and shared config resolution aligned.
2. If config discovery changes, inspect `candidate_env_paths()` and `find_env_file_path()` behavior before editing. Preserve the preference for package-local role env files unless the task explicitly changes it.
3. If startup flow changes, update both the code path and the user-facing launch docs in the same branch.
4. Validate with the [startup verification checklist](./references/startup-verification-checklist.md), especially `tests/test_config.py`, `tests/test_package_entrypoints.py`, and `tests/test_macos_launchers.py`.
5. Summarize which launch path changed: installed package entrypoints, raw-checkout `.command` launchers, config resolution, or all of the above.

## References

- [Startup surface map](./references/startup-surface-map.md)
- [Startup verification checklist](./references/startup-verification-checklist.md)
