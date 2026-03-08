import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import time

try:
    from tests.test_support import ROOT_DIR, add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import ROOT_DIR, add_workspace_package_paths


add_workspace_package_paths()

from better_together_shared.asset_catalog import (
    AIM_ASSET_ID,
    CANNONBALL_ASSET_ID,
    CLIENT_ASSET_BUNDLE,
    CREW_CAPTAIN_M_001_LIGHT_ASSET_ID,
    OBSTACLE_ASSET_ID,
    SERVER_ASSET_BUNDLE,
    get_asset_spec,
)
from better_together_shared.asset_pipeline import (
    COPY_BUILD_STRATEGY,
    SCALE_TO_SIZE_BUILD_STRATEGY,
    SCALE_BY_CELLS_BUILD_STRATEGY,
    BuildTask,
    build_asset_tasks,
    check_build_task,
    compute_scaled_dimensions,
    create_collision_mask_surface,
    create_build_task,
    perform_build_task,
    promote_surface_transparency,
)


class AssetPipelineTests(unittest.TestCase):
    def test_build_asset_tasks_filters_to_requested_bundle(self):
        server_asset_ids = {task.asset_id for task in build_asset_tasks(bundle_target=SERVER_ASSET_BUNDLE)}

        self.assertIn(OBSTACLE_ASSET_ID, server_asset_ids)
        self.assertIn(CREW_CAPTAIN_M_001_LIGHT_ASSET_ID, server_asset_ids)
        self.assertNotIn(AIM_ASSET_ID, server_asset_ids)

    def test_create_build_task_uses_high_quality_crew_source_and_runtime_destination(self):
        asset_spec = get_asset_spec(CREW_CAPTAIN_M_001_LIGHT_ASSET_ID)

        task = create_build_task(asset_spec, CLIENT_ASSET_BUNDLE)

        self.assertEqual(task.build_strategy, SCALE_BY_CELLS_BUILD_STRATEGY)
        self.assertEqual(task.source_size, (48, 64))
        self.assertEqual(task.runtime_size, (36, 48))
        self.assertTrue(str(task.source_path).endswith("assets/source/players/48x64/captain-m-001-light.png"))
        self.assertTrue(str(task.destination_path).endswith("src/better_together_client/Images/players/36x48/captain-m-001-light.png"))

    def test_create_build_task_uses_high_quality_icon_source_and_fixed_runtime_size(self):
        asset_spec = get_asset_spec(CANNONBALL_ASSET_ID)

        task = create_build_task(asset_spec, CLIENT_ASSET_BUNDLE)

        self.assertEqual(task.build_strategy, SCALE_TO_SIZE_BUILD_STRATEGY)
        self.assertEqual(task.runtime_size, (40, 40))
        self.assertTrue(str(task.source_path).endswith("assets/source/projectiles/cannonball.png"))
        self.assertTrue(str(task.destination_path).endswith("src/better_together_client/Images/cannonball.png"))

    def test_compute_scaled_dimensions_scales_full_sprite_sheet_from_cell_sizes(self):
        self.assertEqual(
            compute_scaled_dimensions((144, 256), (48, 64), (36, 48)),
            (108, 192),
        )

    def test_perform_build_task_copies_assets_into_destination(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_path = temp_path / "source.txt"
            destination_path = temp_path / "nested" / "destination.txt"
            source_path.write_text("ahoy", encoding="utf-8")
            task = BuildTask(
                asset_id="test.copy",
                bundle_target=CLIENT_ASSET_BUNDLE,
                source_path=source_path,
                destination_path=destination_path,
                build_strategy=COPY_BUILD_STRATEGY,
            )

            built_path = perform_build_task(task)
            self.assertEqual(built_path, destination_path)
            self.assertEqual(destination_path.read_text(encoding="utf-8"), "ahoy")

    def test_perform_build_task_scales_surfaces_for_generated_runtime_assets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_path = temp_path / "captain.png"
            destination_path = temp_path / "generated" / "captain.png"
            source_path.write_bytes(b"not-a-real-png-but-mocked")
            task = BuildTask(
                asset_id="test.scale",
                bundle_target=CLIENT_ASSET_BUNDLE,
                source_path=source_path,
                destination_path=destination_path,
                build_strategy=SCALE_BY_CELLS_BUILD_STRATEGY,
                source_size=(48, 64),
                runtime_size=(36, 48),
            )
            fake_loaded_surface = SimpleNamespace()
            fake_processed_surface = SimpleNamespace(get_size=lambda: (144, 256))
            fake_scaled_surface = object()

            with patch("better_together_shared.asset_pipeline.pygame.image.load", return_value=fake_loaded_surface) as mock_load:
                with patch("better_together_shared.asset_pipeline.promote_surface_transparency", return_value=fake_processed_surface) as mock_promote:
                    with patch("better_together_shared.asset_pipeline.pygame.transform.scale", return_value=fake_scaled_surface) as mock_scale:
                        with patch("better_together_shared.asset_pipeline.pygame.image.save") as mock_save:
                            built_path = perform_build_task(task)

        self.assertEqual(built_path, destination_path)
        mock_load.assert_called_once_with(source_path)
        mock_promote.assert_called_once_with(fake_loaded_surface, use_top_left_transparency=False)
        mock_scale.assert_called_once_with(fake_processed_surface, (108, 192))
        mock_save.assert_called_once_with(fake_scaled_surface, destination_path)

    def test_promote_surface_transparency_preserves_existing_colorkey_as_alpha(self):
        surface = __import__("pygame").Surface((2, 2))
        surface.fill((71, 112, 76))
        surface.set_at((1, 1), (255, 0, 0))
        surface.set_colorkey((71, 112, 76))

        promoted_surface = promote_surface_transparency(surface)

        self.assertEqual(tuple(promoted_surface.get_at((0, 0))), (0, 0, 0, 0))
        self.assertEqual(tuple(promoted_surface.get_at((1, 1))), (255, 0, 0, 255))

    def test_promote_surface_transparency_can_key_from_top_left_pixel(self):
        surface = __import__("pygame").Surface((2, 2))
        surface.fill((0, 0, 0))
        surface.set_at((1, 1), (255, 255, 255))

        promoted_surface = promote_surface_transparency(surface, use_top_left_transparency=True)

        self.assertEqual(tuple(promoted_surface.get_at((0, 0))), (0, 0, 0, 0))
        self.assertEqual(tuple(promoted_surface.get_at((1, 1))), (255, 255, 255, 255))

    def test_create_collision_mask_surface_returns_monochrome_alpha_mask(self):
        import pygame

        surface = pygame.Surface((3, 3), pygame.SRCALPHA, 32)
        surface.fill((0, 0, 0, 0))
        surface.set_at((1, 1), (10, 20, 30, 255))

        mask_surface = create_collision_mask_surface(surface)

        self.assertEqual(tuple(mask_surface.get_at((0, 0))), (0, 0, 0, 0))
        self.assertEqual(tuple(mask_surface.get_at((1, 1))), (255, 255, 255, 255))

    def test_check_build_task_reports_missing_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_path = temp_path / "source.txt"
            destination_path = temp_path / "missing" / "destination.txt"
            source_path.write_text("ahoy", encoding="utf-8")
            task = BuildTask(
                asset_id="test.check",
                bundle_target=CLIENT_ASSET_BUNDLE,
                source_path=source_path,
                destination_path=destination_path,
                build_strategy=COPY_BUILD_STRATEGY,
            )

            issue = check_build_task(task)

        self.assertIsNotNone(issue)
        self.assertIn("missing output", issue.message)

    def test_check_build_task_ignores_staleness_by_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_path = temp_path / "source.txt"
            destination_path = temp_path / "destination.txt"
            destination_path.write_text("old", encoding="utf-8")
            time.sleep(0.01)
            source_path.write_text("new", encoding="utf-8")
            task = BuildTask(
                asset_id="test.non-strict-check",
                bundle_target=CLIENT_ASSET_BUNDLE,
                source_path=source_path,
                destination_path=destination_path,
                build_strategy=COPY_BUILD_STRATEGY,
            )

            issue = check_build_task(task)

        self.assertIsNone(issue)

    def test_check_build_task_can_fail_on_stale_outputs_when_requested(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_path = temp_path / "source.txt"
            destination_path = temp_path / "destination.txt"
            destination_path.write_text("old", encoding="utf-8")
            time.sleep(0.01)
            source_path.write_text("new", encoding="utf-8")
            task = BuildTask(
                asset_id="test.strict-check",
                bundle_target=CLIENT_ASSET_BUNDLE,
                source_path=source_path,
                destination_path=destination_path,
                build_strategy=COPY_BUILD_STRATEGY,
            )

            issue = check_build_task(task, check_staleness=True)

        self.assertIsNotNone(issue)
        self.assertIn("stale output", issue.message)

    def test_generated_runtime_player_sheets_have_transparent_backgrounds(self):
        import pygame

        runtime_paths = (
            ROOT_DIR / "src" / "better_together_client" / "Images" / "players" / "36x48" / "captain-m-001-light.png",
            ROOT_DIR / "src" / "better_together_server" / "Images" / "players" / "36x48" / "captain-m-001-light.png",
        )

        for runtime_path in runtime_paths:
            with self.subTest(path=runtime_path):
                surface = pygame.image.load(runtime_path)
                self.assertEqual(surface.get_at((0, 0)).a, 0)
                self.assertEqual(surface.get_at((surface.get_width() // 2, surface.get_height() // 2)).a, 0)

    def test_server_runtime_collision_assets_are_monochrome_masks(self):
        import pygame

        runtime_paths = (
            ROOT_DIR / "src" / "better_together_server" / "Images" / "players" / "36x48" / "captain-m-001-light.png",
            ROOT_DIR / "src" / "better_together_server" / "Images" / "obstacle.png",
        )

        for runtime_path in runtime_paths:
            surface = pygame.image.load(runtime_path)
            visible_pixels = [
                tuple(surface.get_at((x, y)))
                for x in range(surface.get_width())
                for y in range(surface.get_height())
                if surface.get_at((x, y)).a > 0
            ]

            with self.subTest(path=runtime_path):
                self.assertTrue(visible_pixels)
                self.assertTrue(all(pixel[:3] == (255, 255, 255) for pixel in visible_pixels[:200]))

    def test_client_runtime_images_folder_no_longer_keeps_before_variants(self):
        obsolete_paths = (
            ROOT_DIR / "src" / "better_together_client" / "Images" / "cannonball before resize.png",
            ROOT_DIR / "src" / "better_together_client" / "Images" / "wood plank before resize.png",
            ROOT_DIR / "src" / "better_together_client" / "Images" / "obstacle before transparency.png",
        )

        for obsolete_path in obsolete_paths:
            with self.subTest(path=obsolete_path):
                self.assertFalse(obsolete_path.exists())


if __name__ == "__main__":
    unittest.main()
