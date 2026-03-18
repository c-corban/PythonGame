# Better-Together startup verification checklist

## Automated checks

- `tests/test_config.py` for env-path precedence and stable env variable names.
- `tests/test_package_entrypoints.py` for safe imports and package entrypoint exposure.
- `tests/test_macos_launchers.py` for executable launchers, dry-run output, and env-file targeting.

## What to look for

- `find_env_file_path()` still prefers the role-specific `.env` when it exists.
- Overrides passed through `BETTER_TOGETHER_ENV_FILE` still win.
- Client and server CLI modules still set their runtime-role defaults before calling app startup.
- Launcher dry runs still print the expected entry module and env file.

## Manual follow-up when startup behavior changed

- Start the server with `python -m better_together_server` and confirm it reaches `Waiting for connections`.
- Start the client with `python -m better_together_client` and confirm it connects or fails with the expected guidance.
- On macOS, dry-run or launch the `.command` files if the change touched launcher behavior.

## Reporting

- Say whether the change affected installed entrypoints, raw-checkout launchers, config resolution, or role defaults.
- Note any environment-dependent verification you could not complete locally.
