import importlib
import unittest
from unittest.mock import Mock, patch

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()

from better_together_shared.asset_catalog import CREW_CAPTAIN_M_001_LIGHT_ASSET_ID
from better_together_shared.protocol import create_assignment_message, create_room_state_message


class ClientNetworkLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.network_module = importlib.import_module("better_together_client.network")

    def test_network_init_does_not_connect_immediately(self):
        fake_socket = Mock()

        with patch.object(self.network_module.socket, "socket", return_value=fake_socket):
            network = self.network_module.Network()

        self.assertIsNone(network.client)
        self.assertFalse(network.connected)
        fake_socket.connect.assert_not_called()

    def test_connect_and_send_update_authoritative_state(self):
        fake_socket = Mock()
        assignment_gameplay_state = {
            "tick_rate_hz": 20,
            "game_over": False,
            "game_over_ticks_remaining": 0,
            "repair_target": None,
            "repair_ticks_remaining": 60,
            "repair_duration_ticks": 60,
            "cannon_reload_ticks_remaining": 60,
            "cannon_reload_duration_ticks": 60,
        }
        room_state_gameplay_state = {
            "tick_rate_hz": 20,
            "game_over": True,
            "game_over_ticks_remaining": 199,
            "repair_target": (11, 22),
            "repair_ticks_remaining": 15,
            "repair_duration_ticks": 60,
            "cannon_reload_ticks_remaining": 9,
            "cannon_reload_duration_ticks": 60,
        }
        assignment_snapshot = {
            "x": 100,
            "y": 200,
            "width": 36,
            "height": 48,
            "char": CREW_CAPTAIN_M_001_LIGHT_ASSET_ID,
            "animation": (36, 96, 36, 48),
            "frame": 17,
            "velocity": 2,
            "increment": 3,
            "maxHeight": 960,
            "maxWidth": 1280,
            "inventoryWood": 8,
            "inventoryCannon": 7,
            "cannonBallAnimationX": -1000,
            "cannonBallAnimationY": -1000,
            "targetX": 500,
            "targetY": 600,
            "direction": 4,
            "entity_kind": "crew_member",
        }
        room_state_self_snapshot = dict(assignment_snapshot)
        room_state_self_snapshot["inventoryWood"] = 5
        room_state_self_snapshot["inventoryCannon"] = 4
        room_state_entity_snapshot = dict(assignment_snapshot)
        room_state_entity_snapshot["x"] = 300
        room_state_entity_snapshot["y"] = 400

        receive_messages = [
            create_assignment_message(0, 0, assignment_snapshot, gameplay_state=assignment_gameplay_state),
            create_room_state_message(
                0,
                [room_state_entity_snapshot],
                self_player=room_state_self_snapshot,
                damage_markers=[(11, 22)],
                enemy_projectiles=[(33, 44)],
                player_projectiles=[(55, 66)],
                gameplay_state=room_state_gameplay_state,
            ),
        ]

        with patch.object(self.network_module.socket, "socket", return_value=fake_socket):
            with patch.object(self.network_module, "receive_message", side_effect=receive_messages):
                with patch.object(self.network_module, "send_message"):
                    network = self.network_module.Network()
                    player_me = network.connect()
                    self.assertEqual(network.gameplay_state, assignment_gameplay_state)
                    player_others = network.send(
                        player_me,
                        repaired_damage_markers=[(11, 22)],
                        action_state={"action_pressed": True, "repair_target": (11, 22)},
                    )

        self.assertTrue(network.connected)
        self.assertEqual((player_me.inventoryWood, player_me.inventoryCannon), (5, 4))
        self.assertEqual(network.damage_markers, [(11, 22)])
        self.assertEqual(network.enemy_projectiles, [(33, 44)])
        self.assertEqual(network.player_projectiles, [(55, 66)])
        self.assertEqual(network.gameplay_state, room_state_gameplay_state)
        self.assertEqual(len(player_others), 1)

    def test_close_clears_cached_room_state(self):
        fake_socket = Mock()
        network = self.network_module.Network()
        network.client = fake_socket
        network.connected = True
        network.room_id = 7
        network.player_number = 2
        network.damage_markers = [(11, 22)]
        network.enemy_projectiles = [(33, 44)]
        network.player_projectiles = [(55, 66)]
        network.gameplay_state = {"game_over": True}

        network.close()

        fake_socket.close.assert_called_once_with()
        self.assertFalse(network.connected)
        self.assertEqual(network.room_id, None)
        self.assertEqual(network.player_number, None)
        self.assertEqual(network.damage_markers, [])
        self.assertEqual(network.enemy_projectiles, [])
        self.assertEqual(network.player_projectiles, [])
        self.assertEqual(network.gameplay_state, {})
