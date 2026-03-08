#!/bin/sh

set -u

APP_NAME="Better Together Client"
ENTRY_MODULE="better_together_client"
PYTHON_OVERRIDE_ENV_VAR="BETTER_TOGETHER_LAUNCHER_PYTHON"
DRY_RUN_ENV_VAR="BETTER_TOGETHER_LAUNCHER_DRY_RUN"

keep_window_open() {
    printf "\nPress Return to close this window..."
    IFS= read -r _unused
}

resolve_project_root() {
    CDPATH= cd -- "$(dirname -- "$0")" && pwd
}

resolve_package_dir() {
    printf '%s\n' "src/$ENTRY_MODULE"
}

resolve_runtime_role() {
    printf '%s\n' "${ENTRY_MODULE##*_}"
}

resolve_python_command() {
    override_python="${BETTER_TOGETHER_LAUNCHER_PYTHON:-}"
    if [ -n "$override_python" ]; then
        if [ -x "$override_python" ]; then
            printf '%s\n' "$override_python"
            return 0
        fi

        if command -v "$override_python" >/dev/null 2>&1; then
            command -v "$override_python"
            return 0
        fi

        return 1
    fi

    if [ -x "$PROJECT_ROOT/.venv/bin/python" ]; then
        printf '%s\n' "$PROJECT_ROOT/.venv/bin/python"
        return 0
    fi

    if command -v python3 >/dev/null 2>&1; then
        command -v python3
        return 0
    fi

    if command -v python >/dev/null 2>&1; then
        command -v python
        return 0
    fi

    return 1
}

PROJECT_ROOT=$(resolve_project_root)
PACKAGE_DIR=$(resolve_package_dir)
TARGET_PATH="$PROJECT_ROOT/$PACKAGE_DIR/__main__.py"
ROLE_ENV_PATH="$PROJECT_ROOT/$PACKAGE_DIR/.env"
RUNTIME_ROLE=$(resolve_runtime_role)

if [ ! -f "$TARGET_PATH" ]; then
    printf '%s\n' "Could not find the client module runner at: $TARGET_PATH"
    keep_window_open
    exit 1
fi

if ! PYTHON_BIN=$(resolve_python_command); then
    printf '%s\n' "Could not find a Python interpreter."
    printf '%s\n' "Create the repo .venv first, or set $PYTHON_OVERRIDE_ENV_VAR to a working Python command/path."
    keep_window_open
    exit 1
fi

if [ -f "$ROLE_ENV_PATH" ]; then
    export BETTER_TOGETHER_ENV_FILE="$ROLE_ENV_PATH"
fi

export BETTER_TOGETHER_RUNTIME_ROLE="$RUNTIME_ROLE"
export PYTHONUNBUFFERED=1
export PYTHONPATH="$PROJECT_ROOT/src${PYTHONPATH:+:$PYTHONPATH}"

if ! cd "$PROJECT_ROOT"; then
    printf '%s\n' "Could not switch to the project root: $PROJECT_ROOT"
    keep_window_open
    exit 1
fi

printf '%s\n' "Launching $APP_NAME..."
printf '%s\n' "Using Python: $PYTHON_BIN"
printf '%s\n' "Using env file: ${BETTER_TOGETHER_ENV_FILE:-<none>}"

if [ "${BETTER_TOGETHER_LAUNCHER_DRY_RUN:-0}" = "1" ]; then
    printf '%s\n' "Entry module: $ENTRY_MODULE"
    exit 0
fi

"$PYTHON_BIN" -m "$ENTRY_MODULE"
status=$?

if [ "$status" -ne 0 ]; then
    printf '\n%s\n' "$APP_NAME exited with status $status."
    keep_window_open
fi

exit "$status"
