import tempfile
import sys
import unittest
from pathlib import Path

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()

from better_together_shared.config import (
    CLIENT_ENV_FILE_NAME,
    CLIENT_SERVER_ADDRESS,
    CLIENT_SERVER_HOST,
    CLIENT_SERVER_HOST_ENV_VAR,
    CLIENT_SERVER_PORT,
    CLIENT_SERVER_PORT_ENV_VAR,
    CLIENT_RUNTIME_ROLE,
    ENV_FILE_PATH,
    SERVER_ENV_FILE_NAME,
    SERVER_ADDRESS,
    SERVER_BIND_ADDRESS,
    SERVER_BIND_HOST,
    SERVER_BIND_HOST_ENV_VAR,
    SERVER_BIND_PORT,
    SERVER_BIND_PORT_ENV_VAR,
    SERVER_RUNTIME_ROLE,
    find_env_file_path,
)


class SharedConfigTests(unittest.TestCase):
    def build_role_env_path(self, root_path, runtime_role):
        package_name = "better_together_client" if runtime_role == CLIENT_RUNTIME_ROLE else "better_together_server"
        env_file_name = CLIENT_ENV_FILE_NAME if runtime_role == CLIENT_RUNTIME_ROLE else SERVER_ENV_FILE_NAME
        return root_path / "src" / package_name / env_file_name

    def test_bind_and_connect_addresses_are_exposed_separately(self):
        self.assertEqual(SERVER_BIND_ADDRESS, (SERVER_BIND_HOST, SERVER_BIND_PORT))
        self.assertEqual(CLIENT_SERVER_ADDRESS, (CLIENT_SERVER_HOST, CLIENT_SERVER_PORT))

    def test_legacy_server_address_alias_matches_client_target(self):
        self.assertEqual(SERVER_ADDRESS, CLIENT_SERVER_ADDRESS)

    def test_expected_env_var_names_are_stable(self):
        self.assertEqual(SERVER_BIND_HOST_ENV_VAR, "BETTER_TOGETHER_SERVER_BIND_HOST")
        self.assertEqual(SERVER_BIND_PORT_ENV_VAR, "BETTER_TOGETHER_SERVER_BIND_PORT")
        self.assertEqual(CLIENT_SERVER_HOST_ENV_VAR, "BETTER_TOGETHER_CLIENT_SERVER_HOST")
        self.assertEqual(CLIENT_SERVER_PORT_ENV_VAR, "BETTER_TOGETHER_CLIENT_SERVER_PORT")

    def test_default_env_file_path_uses_dotenv_name(self):
        self.assertEqual(ENV_FILE_PATH.name, ".env")

    def test_client_role_prefers_role_specific_env_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            role_env_path = self.build_role_env_path(temp_path, CLIENT_RUNTIME_ROLE)
            fallback_env_path = temp_path / ".env"
            role_env_path.parent.mkdir(parents=True, exist_ok=True)
            role_env_path.write_text("client=1\n", encoding="utf-8")
            fallback_env_path.write_text("shared=1\n", encoding="utf-8")

            resolved_path = find_env_file_path(
                runtime_role=CLIENT_RUNTIME_ROLE,
                cwd=temp_path,
                package_root=temp_path,
            )

        self.assertEqual(resolved_path, role_env_path.resolve())

    def test_server_role_prefers_role_specific_env_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            role_env_path = self.build_role_env_path(temp_path, SERVER_RUNTIME_ROLE)
            fallback_env_path = temp_path / ".env"
            role_env_path.parent.mkdir(parents=True, exist_ok=True)
            role_env_path.write_text("server=1\n", encoding="utf-8")
            fallback_env_path.write_text("shared=1\n", encoding="utf-8")

            resolved_path = find_env_file_path(
                runtime_role=SERVER_RUNTIME_ROLE,
                cwd=temp_path,
                package_root=temp_path,
            )

        self.assertEqual(resolved_path, role_env_path.resolve())

    def test_env_override_path_takes_precedence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            override_path = temp_path / "custom.env"
            override_path.write_text("override=1\n", encoding="utf-8")
            role_env_path = self.build_role_env_path(temp_path, CLIENT_RUNTIME_ROLE)
            role_env_path.parent.mkdir(parents=True, exist_ok=True)
            role_env_path.write_text("client=1\n", encoding="utf-8")
            (temp_path / ".env").write_text("shared=1\n", encoding="utf-8")

            resolved_path = find_env_file_path(
                runtime_role=CLIENT_RUNTIME_ROLE,
                cwd=temp_path,
                package_root=temp_path,
                override=override_path,
            )

        self.assertEqual(resolved_path, override_path.resolve())

    def test_role_specific_fallback_path_is_reported_when_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            resolved_path = find_env_file_path(
                runtime_role=CLIENT_RUNTIME_ROLE,
                cwd=temp_path,
                package_root=temp_path,
            )

        self.assertEqual(resolved_path, self.build_role_env_path(temp_path, CLIENT_RUNTIME_ROLE).resolve())
