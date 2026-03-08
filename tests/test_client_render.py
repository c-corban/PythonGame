import importlib
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, call, patch

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()

from better_together_shared.asset_catalog import (
    AIM_ASSET_ID,
    CANNONBALL_ASSET_ID,
    SHIP_DECK_ASSET_ID,
    WATER_ASSET_ID,
    WOOD_PLANK_ASSET_ID,
)


class ClientRenderRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.render = importlib.import_module("better_together_client.render")

    def tearDown(self):
        self.render.shutdown_runtime()

    def test_initialize_runtime_returns_runtime_and_updates_compatibility_globals(self):
        fake_window = object()
        fake_ship = object()
        fake_water = object()
        fake_aim = object()
        fake_wood_icon = object()
        fake_cannonball_icon = object()
        fake_font = object()

        with patch.object(self.render.pygame, "init"):
            with patch.object(self.render.pygame.display, "set_mode", return_value=fake_window):
                with patch.object(self.render.pygame.display, "set_caption"):
                    with patch.object(self.render, "load_scaled_image", side_effect=[fake_ship, fake_water, fake_aim]) as mock_load_scaled_image:
                        with patch.object(self.render, "load_image", side_effect=[fake_wood_icon, fake_cannonball_icon]) as mock_load_image:
                            with patch.object(self.render.pygame.font, "SysFont", return_value=fake_font):
                                runtime = self.render.initialize_runtime()

        self.assertIsInstance(runtime, self.render.RenderRuntime)
        self.assertEqual(
            mock_load_scaled_image.call_args_list,
            [
                call(SHIP_DECK_ASSET_ID, (self.render.width // 2, self.render.height), alpha=False),
                call(WATER_ASSET_ID, (self.render.width // 4, self.render.height), alpha=False),
                call(AIM_ASSET_ID, (80, 80)),
            ],
        )
        self.assertEqual(
            mock_load_image.call_args_list,
            [
                call(WOOD_PLANK_ASSET_ID),
                call(CANNONBALL_ASSET_ID),
            ],
        )
        self.assertIs(runtime, self.render.get_runtime())
        self.assertIs(self.render.window, fake_window)
        self.assertIs(self.render.ship, fake_ship)
        self.assertIs(self.render.water, fake_water)
        self.assertIs(self.render.aim, fake_aim)
        self.assertIs(self.render.wood_icon, fake_wood_icon)
        self.assertIs(self.render.cannonball_icon, fake_cannonball_icon)
        self.assertIs(self.render.font, fake_font)
        self.assertIs(self.render.hit, runtime.hit)

    def test_refresh_draws_enemy_projectiles_in_flight(self):
        fake_surface = Mock()
        fake_font = Mock()
        fake_font.render.side_effect = [object(), object()]
        player_me = SimpleNamespace(inventoryWood=3, inventoryCannon=4, draw=Mock())
        player_other = SimpleNamespace(draw=Mock())
        runtime = self.render.RenderRuntime(
            window=fake_surface,
            ship=object(),
            water=object(),
            aim=object(),
            wood_icon=object(),
            cannonball_icon=object(),
            font=fake_font,
            hit=[(11, 22)],
            enemy_projectiles=[(44, 55)],
        )

        self.render.refresh(runtime, player_me, [player_other])

        self.assertIn(call(runtime.water, (11, 22), (0, 0, 15, 15)), fake_surface.blit.call_args_list)
        self.assertIn(call(runtime.cannonball_icon, (44, 55)), fake_surface.blit.call_args_list)
        self.assertNotIn(call(runtime.cannonball_icon, (11, 22)), fake_surface.blit.call_args_list)
        player_other.draw.assert_called_once_with(fake_surface)
        player_me.draw.assert_called_once_with(fake_surface)
