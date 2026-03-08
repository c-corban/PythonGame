import os
import subprocess
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class MacOSLauncherTests(unittest.TestCase):
    def run_launcher_dry_run(self, launcher_name):
        launcher_path = PROJECT_ROOT / launcher_name
        self.assertTrue(launcher_path.exists(), f"Missing launcher: {launcher_name}")
        self.assertTrue(os.access(launcher_path, os.X_OK), f"Launcher should be executable: {launcher_name}")

        env = os.environ.copy()
        env["BETTER_TOGETHER_LAUNCHER_DRY_RUN"] = "1"
        env["BETTER_TOGETHER_LAUNCHER_PYTHON"] = sys.executable

        return subprocess.run(
            ["/bin/sh", os.fspath(launcher_path)],
            cwd=PROJECT_ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_client_launcher_dry_run_targets_client_module(self):
        result = self.run_launcher_dry_run("Launch Better Together Client.command")

        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        self.assertIn("Launching Better Together Client...", result.stdout)
        self.assertIn("Entry module: better_together_client", result.stdout)
        self.assertIn(
            f"Using env file: {PROJECT_ROOT / 'src/better_together_client/.env'}",
            result.stdout,
        )

    def test_server_launcher_dry_run_targets_server_module(self):
        result = self.run_launcher_dry_run("Launch Better Together Server.command")

        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)
        self.assertIn("Launching Better Together Server...", result.stdout)
        self.assertIn("Entry module: better_together_server", result.stdout)
        self.assertIn(
            f"Using env file: {PROJECT_ROOT / 'src/better_together_server/.env'}",
            result.stdout,
        )
