"""Shared runtime constants used by the Better Together packages and launchers."""

import os
from pathlib import Path


SHARED_PACKAGE_DIR = Path(__file__).resolve().parent
PACKAGE_SOURCE_ROOT = SHARED_PACKAGE_DIR.parent
PACKAGE_ROOT = PACKAGE_SOURCE_ROOT.parent if PACKAGE_SOURCE_ROOT.name == "src" else PACKAGE_SOURCE_ROOT
ENV_FILE_OVERRIDE_ENV_VAR = "BETTER_TOGETHER_ENV_FILE"
RUNTIME_ROLE_ENV_VAR = "BETTER_TOGETHER_RUNTIME_ROLE"

CLIENT_RUNTIME_ROLE = "client"
SERVER_RUNTIME_ROLE = "server"

CLIENT_PACKAGE_DIR_NAME = "better_together_client"
SERVER_PACKAGE_DIR_NAME = "better_together_server"

CLIENT_ENV_FILE_NAME = ".env"
SERVER_ENV_FILE_NAME = ".env"

ROLE_ENV_FILE_NAMES = {
    CLIENT_RUNTIME_ROLE: CLIENT_ENV_FILE_NAME,
    SERVER_RUNTIME_ROLE: SERVER_ENV_FILE_NAME,
}

ROLE_PACKAGE_DIR_NAMES = {
    CLIENT_RUNTIME_ROLE: CLIENT_PACKAGE_DIR_NAME,
    SERVER_RUNTIME_ROLE: SERVER_PACKAGE_DIR_NAME,
}

SERVER_BIND_HOST_ENV_VAR = "BETTER_TOGETHER_SERVER_BIND_HOST"
SERVER_BIND_PORT_ENV_VAR = "BETTER_TOGETHER_SERVER_BIND_PORT"
CLIENT_SERVER_HOST_ENV_VAR = "BETTER_TOGETHER_CLIENT_SERVER_HOST"
CLIENT_SERVER_PORT_ENV_VAR = "BETTER_TOGETHER_CLIENT_SERVER_PORT"


def normalize_runtime_role(runtime_role):
    if runtime_role is None:
        return None

    normalized_role = runtime_role.strip().lower()
    if normalized_role in ROLE_ENV_FILE_NAMES:
        return normalized_role

    return None


def _resolve_cwd(cwd=None):
    return Path.cwd().resolve() if cwd is None else Path(cwd).resolve()


def _resolve_package_root(package_root=None):
    return PACKAGE_ROOT.resolve() if package_root is None else Path(package_root).resolve()


def _resolve_package_source_root(package_root=None):
    if package_root is None:
        return PACKAGE_SOURCE_ROOT.resolve()

    candidate_root = Path(package_root).resolve()
    if candidate_root.name == "src":
        return candidate_root

    if any((candidate_root / package_dir_name).exists() for package_dir_name in ROLE_PACKAGE_DIR_NAMES.values()):
        return candidate_root

    src_root = candidate_root / "src"
    return src_root.resolve(strict=False)


def _iter_search_roots(cwd=None, package_root=None):
    cwd_path = _resolve_cwd(cwd)
    package_root_path = _resolve_package_root(package_root)

    yield from (cwd_path, *cwd_path.parents, package_root_path, package_root_path.parent)


def _role_env_package_path(runtime_role, package_root=None):
    normalized_role = normalize_runtime_role(runtime_role)
    if normalized_role is None:
        return None

    package_source_root = _resolve_package_source_root(package_root)
    return package_source_root / ROLE_PACKAGE_DIR_NAMES[normalized_role] / ROLE_ENV_FILE_NAMES[normalized_role]


def candidate_env_paths(runtime_role=None, cwd=None, package_root=None, override=None):
    if override is None:
        override = os.environ.get(ENV_FILE_OVERRIDE_ENV_VAR)

    if override:
        yield Path(override).expanduser()

    normalized_role = normalize_runtime_role(
        runtime_role if runtime_role is not None else os.environ.get(RUNTIME_ROLE_ENV_VAR)
    )
    search_roots = tuple(_iter_search_roots(cwd=cwd, package_root=package_root))

    if normalized_role is not None:
        role_package_env_path = _role_env_package_path(normalized_role, package_root=package_root)
        if role_package_env_path is not None:
            yield role_package_env_path

        role_env_file_name = ROLE_ENV_FILE_NAMES[normalized_role]
        for candidate_dir in search_roots:
            yield candidate_dir / role_env_file_name

    for candidate_dir in search_roots:
        yield candidate_dir / ".env"


def _candidate_env_paths():
    yield from candidate_env_paths()


def find_env_file_path(runtime_role=None, cwd=None, package_root=None, override=None):
    normalized_role = normalize_runtime_role(
        runtime_role if runtime_role is not None else os.environ.get(RUNTIME_ROLE_ENV_VAR)
    )
    seen_paths = set()
    for candidate_path in candidate_env_paths(
        runtime_role=runtime_role,
        cwd=cwd,
        package_root=package_root,
        override=override,
    ):
        normalized_candidate = candidate_path.resolve(strict=False)
        if normalized_candidate in seen_paths:
            continue

        seen_paths.add(normalized_candidate)
        if normalized_candidate.exists():
            return normalized_candidate

    role_package_env_path = _role_env_package_path(normalized_role, package_root=package_root)
    if role_package_env_path is not None:
        return role_package_env_path.resolve(strict=False)

    fallback_dir = _resolve_cwd(cwd)
    return (fallback_dir / ".env").resolve(strict=False)


def _find_env_file_path():
    return find_env_file_path()


ENV_FILE_PATH = find_env_file_path()


def _load_dotenv_defaults():
    if not ENV_FILE_PATH.exists():
        return

    for line in ENV_FILE_PATH.read_text(encoding="utf-8").splitlines():
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#") or "=" not in stripped_line:
            continue

        key, value = stripped_line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _read_int_env(name, default):
    value = os.environ.get(name)
    if value in (None, ""):
        return default

    return int(value)


_load_dotenv_defaults()


SERVER_BIND_HOST = os.environ.get(SERVER_BIND_HOST_ENV_VAR, "localhost")
SERVER_BIND_PORT = _read_int_env(SERVER_BIND_PORT_ENV_VAR, 2911)
SERVER_BIND_ADDRESS = (SERVER_BIND_HOST, SERVER_BIND_PORT)

CLIENT_SERVER_HOST = os.environ.get(CLIENT_SERVER_HOST_ENV_VAR, "localhost")
CLIENT_SERVER_PORT = _read_int_env(CLIENT_SERVER_PORT_ENV_VAR, SERVER_BIND_PORT)
CLIENT_SERVER_ADDRESS = (CLIENT_SERVER_HOST, CLIENT_SERVER_PORT)

SERVER_HOST = CLIENT_SERVER_HOST
SERVER_PORT = CLIENT_SERVER_PORT
SERVER_ADDRESS = CLIENT_SERVER_ADDRESS

SERVER_SOCKET_BACKLOG = 1

NETWORK_BUFFER_SIZE = 65535

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 960
WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)
GAME_TITLE = "Better Together"

PLAYER_SPAWN_POSITIONS = (
    (480, 780),
    (576, 780),
    (722, 780),
    (818, 780),
)
