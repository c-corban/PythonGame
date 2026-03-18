import importlib
import unittest
from unittest.mock import Mock, patch

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()


class ClientPlayerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player_module = importlib.import_module("better_together_client.player")

    def test_draw_resets_local_cannonball_preview_after_blit(self):
        player = self.player_module.Player(100, 200, 36, 48, "crew-preview")
        player.cannonBallAnimationX = 321
        player.cannonBallAnimationY = 654
        window = Mock()

        with patch.object(self.player_module, "load_image", side_effect=[object(), object()]):
            player.draw(window)

        self.assertEqual(window.blit.call_count, 2)
        self.assertEqual((player.cannonBallAnimationX, player.cannonBallAnimationY), (-1000, -1000))
