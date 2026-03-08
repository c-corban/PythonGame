import importlib
import unittest
from types import SimpleNamespace

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()

from better_together_client.session import GameplaySessionState


class ClientGameLoopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.game_loop = importlib.import_module("better_together_client.game_loop")

    def test_update_shoot_animation_rounds_cannon_positions_to_integers(self):
        player = SimpleNamespace(
            x=520,
            y=640,
            cannonBallAnimationX=-1000,
            cannonBallAnimationY=-1000,
            targetX=-1000,
            targetY=-1000,
        )
        session_state = GameplaySessionState(
            aim_x=333,
            aim_y=187,
            cannon_shoot=0,
            shoot_animation=True,
        )

        self.game_loop.update_shoot_animation(session_state, player)

        self.assertEqual(session_state.cannon_shoot, 1)
        self.assertEqual((player.cannonBallAnimationX, player.cannonBallAnimationY), (457, 652))
        self.assertIsInstance(player.cannonBallAnimationX, int)
        self.assertIsInstance(player.cannonBallAnimationY, int)
