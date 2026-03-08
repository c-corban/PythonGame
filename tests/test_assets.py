import importlib
import os
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from tests.test_support import ROOT_DIR, add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import ROOT_DIR, add_workspace_package_paths


add_workspace_package_paths()

from better_together_shared.asset_catalog import (
    CREW_CAPTAIN_M_001_LIGHT_ASSET_ID,
    get_asset_spec,
)


class FakeLoadedImage:
    def __init__(self, alpha_result, plain_result):
        self.alpha_result = alpha_result
        self.plain_result = plain_result
        self.convert_alpha_calls = 0
        self.convert_calls = 0

    def convert_alpha(self):
        self.convert_alpha_calls += 1
        return self.alpha_result

    def convert(self):
        self.convert_calls += 1
        return self.plain_result


class AssetHelperContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.modules = {
            "client_package": importlib.import_module("better_together_client.assets"),
            "server_package": importlib.import_module("better_together_server.assets"),
        }

    def setUp(self):
        self.clear_caches()

    def tearDown(self):
        self.clear_caches()

    def clear_caches(self):
        for module in self.modules.values():
            module.load_image.cache_clear()
            module.load_scaled_image.cache_clear()

    def test_asset_helpers_resolve_from_canonical_package_roots(self):
        expected_base_dirs = {
            "client_package": ROOT_DIR / "src" / "better_together_client",
            "server_package": ROOT_DIR / "src" / "better_together_server",
        }

        for module_name, module in self.modules.items():
            with self.subTest(module=module_name):
                self.assertEqual(Path(module.BASE_DIR), expected_base_dirs[module_name])

    def test_resolve_asset_path_preserves_absolute_paths(self):
        for module_name, module in self.modules.items():
            absolute_path = os.path.join(module.BASE_DIR, "Images", "players", "36x48", "captain-m-001-light.png")

            with self.subTest(module=module_name):
                self.assertEqual(module.resolve_asset_path(absolute_path), absolute_path)

    def test_resolve_asset_path_normalizes_relative_backslashes(self):
        for module_name, module in self.modules.items():
            relative_path = r"Images\players\36x48\captain-m-001-light.png"
            expected_path = os.path.join(module.BASE_DIR, "Images", "players", "36x48", "captain-m-001-light.png")

            with self.subTest(module=module_name):
                self.assertEqual(module.resolve_asset_path(relative_path), expected_path)

    def test_resolve_asset_path_supports_logical_asset_ids(self):
        expected_runtime_path = get_asset_spec(CREW_CAPTAIN_M_001_LIGHT_ASSET_ID).runtime_path

        for module_name, module in self.modules.items():
            with self.subTest(module=module_name):
                self.assertEqual(
                    module.resolve_asset_path(CREW_CAPTAIN_M_001_LIGHT_ASSET_ID),
                    os.path.join(module.BASE_DIR, *Path(expected_runtime_path).parts),
                )

    def test_load_image_uses_alpha_conversion_and_caches_results(self):
        for module_name, module in self.modules.items():
            fake_image = FakeLoadedImage(alpha_result=object(), plain_result=object())
            expected_path = os.path.join(module.BASE_DIR, "Images", "players", "36x48", "captain-m-001-light.png")

            with self.subTest(module=module_name):
                with patch.object(module.pygame.display, "get_init", return_value=True):
                    with patch.object(module.pygame.display, "get_surface", return_value=object()):
                        with patch.object(module.pygame.image, "load", return_value=fake_image) as mock_load:
                            first_result = module.load_image(CREW_CAPTAIN_M_001_LIGHT_ASSET_ID)
                            second_result = module.load_image(CREW_CAPTAIN_M_001_LIGHT_ASSET_ID)

                self.assertIs(first_result, second_result)
                self.assertEqual(first_result, fake_image.alpha_result)
                mock_load.assert_called_once_with(expected_path)
                self.assertEqual(fake_image.convert_alpha_calls, 1)
                self.assertEqual(fake_image.convert_calls, 0)

    def test_load_image_can_use_non_alpha_conversion(self):
        for module_name, module in self.modules.items():
            fake_image = FakeLoadedImage(alpha_result=object(), plain_result=object())

            with self.subTest(module=module_name):
                with patch.object(module.pygame.display, "get_init", return_value=True):
                    with patch.object(module.pygame.display, "get_surface", return_value=object()):
                        with patch.object(module.pygame.image, "load", return_value=fake_image):
                            converted_image = module.load_image(CREW_CAPTAIN_M_001_LIGHT_ASSET_ID, alpha=False)

                self.assertIs(converted_image, fake_image.plain_result)
                self.assertEqual(fake_image.convert_alpha_calls, 0)
                self.assertEqual(fake_image.convert_calls, 1)

    def test_load_image_skips_conversion_without_display_surface(self):
        for module_name, module in self.modules.items():
            fake_image = FakeLoadedImage(alpha_result=object(), plain_result=object())

            with self.subTest(module=module_name):
                with patch.object(module.pygame.display, "get_init", return_value=False):
                    with patch.object(module.pygame.display, "get_surface", return_value=None):
                        with patch.object(module.pygame.image, "load", return_value=fake_image):
                            loaded_image = module.load_image(CREW_CAPTAIN_M_001_LIGHT_ASSET_ID)

                self.assertIs(loaded_image, fake_image)
                self.assertEqual(fake_image.convert_alpha_calls, 0)
                self.assertEqual(fake_image.convert_calls, 0)

    def test_load_scaled_image_delegates_once_per_unique_request(self):
        for module_name, module in self.modules.items():
            source_image = object()
            scaled_image = object()

            with self.subTest(module=module_name):
                with patch.object(module, "load_image", return_value=source_image) as mock_load_image:
                    with patch.object(module.pygame.transform, "scale", return_value=scaled_image) as mock_scale:
                        first_result = module.load_scaled_image(CREW_CAPTAIN_M_001_LIGHT_ASSET_ID, (36, 48))
                        second_result = module.load_scaled_image(CREW_CAPTAIN_M_001_LIGHT_ASSET_ID, (36, 48))

                self.assertIs(first_result, second_result)
                self.assertIs(first_result, scaled_image)
                mock_load_image.assert_called_once_with(CREW_CAPTAIN_M_001_LIGHT_ASSET_ID, True)
                mock_scale.assert_called_once_with(source_image, (36, 48))

    def test_load_image_normalizes_equivalent_relative_paths_for_caching(self):
        for module_name, module in self.modules.items():
            fake_image = FakeLoadedImage(alpha_result=object(), plain_result=object())
            expected_path = os.path.join(module.BASE_DIR, "Images", "players", "36x48", "captain-m-001-light.png")

            with self.subTest(module=module_name):
                with patch.object(module.pygame.display, "get_init", return_value=True):
                    with patch.object(module.pygame.display, "get_surface", return_value=object()):
                        with patch.object(module.pygame.image, "load", return_value=fake_image) as mock_load:
                            first_result = module.load_image(r"Images\players\36x48\captain-m-001-light.png")
                            second_result = module.load_image("Images/players/36x48/captain-m-001-light.png")

                self.assertIs(first_result, second_result)
                mock_load.assert_called_once_with(expected_path)
