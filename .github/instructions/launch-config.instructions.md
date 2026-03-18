---
description: "Use when editing Better-Together setup flow, .env lookup, BETTER_TOGETHER_ENV_FILE overrides, cli.py, __main__.py, app.py, macOS launchers, shared config, README.md, or docs/quickstart.md."
name: "Launch and configuration guardrails"
applyTo: "src/better_together_shared/config.py, src/better_together_client/cli.py, src/better_together_client/app.py, src/better_together_client/__main__.py, src/better_together_server/cli.py, src/better_together_server/app.py, src/better_together_server/__main__.py, Launch Better Together Client.command, Launch Better Together Server.command, README.md, docs/quickstart.md"
---
# Launch and configuration guardrails

- Preserve `python -m better_together_client` and `python -m better_together_server` as the canonical runtime entrypoints unless the task explicitly changes them everywhere.
- Keep the macOS `.command` launchers behaviorally aligned with the package entrypoints; they are the raw-checkout convenience path, not a separate runtime.
- Runtime configuration prefers `src/better_together_client/.env` and `src/better_together_server/.env`. Treat `BETTER_TOGETHER_ENV_FILE` as an explicit override, not the default path.
- When setup flow changes, update both `README.md` and `docs/quickstart.md` in the same branch.
- If launch/config behavior changes, review `tests/test_config.py`, `tests/test_package_entrypoints.py`, and `tests/test_macos_launchers.py`.
- Do not reintroduce a display requirement for the server unless the task explicitly calls for it.
