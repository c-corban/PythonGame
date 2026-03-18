# Better-Together startup surface map

## Entrypoints and bootstrap layers

- `pyproject.toml` defines installed console scripts: `better-together-client` and `better-together-server`.
- `src/better_together_client/cli.py` and `src/better_together_server/cli.py` set the runtime role and call the package app entrypoint.
- `src/better_together_client/__main__.py` and `src/better_together_server/__main__.py` expose `python -m better_together_client` and `python -m better_together_server`.
- The macOS `Launch Better Together Client.command` and `Launch Better Together Server.command` files are the supported raw-checkout launcher path.

## Shared config behavior

- `src/better_together_shared/config.py` owns runtime-role normalization, candidate env discovery, and fallback selection.
- `BETTER_TOGETHER_ENV_FILE` is the explicit override.
- Package-local env files under `src/better_together_client/.env` and `src/better_together_server/.env` are preferred when the runtime role is known.
- `BETTER_TOGETHER_RUNTIME_ROLE` selects the role-specific env search path and defaults are applied after dotenv loading.

## Launcher behavior to preserve unless intentionally changed

- Launchers prefer the repository `.venv` when present, then fall back to `python3` or `python`.
- Launchers prepend `src/` to `PYTHONPATH` for raw-checkout execution.
- Launchers export `BETTER_TOGETHER_RUNTIME_ROLE` and set `BETTER_TOGETHER_ENV_FILE` when the role-specific `.env` exists.
- Launchers support dry-run verification through `BETTER_TOGETHER_LAUNCHER_DRY_RUN=1` and interpreter override through `BETTER_TOGETHER_LAUNCHER_PYTHON`.

## Docs to keep in sync

- `README.md` and `docs/quickstart.md` for setup/run flow.
- `docs/architecture.md` when startup architecture or config precedence meaningfully changes.
