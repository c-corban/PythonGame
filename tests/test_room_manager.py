import importlib
import sys
import unittest

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()

from better_together_shared.protocol import (
    PLAYER_ASSIGNMENT_MESSAGE,
    ROOM_STATE_MESSAGE,
    create_player_snapshot,
    extract_assignment_gameplay_state,
    extract_room_state_damage_markers,
    extract_room_state_enemy_projectiles,
    extract_room_state_gameplay_state,
    extract_room_state_player_projectiles,
    extract_room_state_self_player,
    is_message_type,
)


class RoomManagerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.room_manager = importlib.import_module("better_together_server.room_manager")

    def setUp(self):
        self.room_manager.reset_rooms()

    def tearDown(self):
        self.room_manager.reset_rooms()

    def test_assign_player_slot_creates_then_reuses_room(self):
        first_player_number, first_room_id, first_created = self.room_manager.assign_player_slot()
        second_player_number, second_room_id, second_created = self.room_manager.assign_player_slot()

        self.assertEqual((first_player_number, first_room_id, first_created), (0, 0, True))
        self.assertEqual((second_player_number, second_room_id, second_created), (1, 0, False))
        self.assertEqual(self.room_manager.games[0].ai[:2], [False, False])

    def test_next_room_id_fills_numeric_gap(self):
        self.room_manager.games[0] = object()
        self.room_manager.games[2] = object()

        self.assertEqual(self.room_manager.next_room_id(), 1)

    def test_release_player_slot_closes_room_when_all_slots_return_to_ai(self):
        player_number, room_id, _ = self.room_manager.assign_player_slot()

        room_closed = self.room_manager.release_player_slot(room_id, player_number)

        self.assertTrue(room_closed)
        self.assertNotIn(room_id, self.room_manager.games)

    def test_room_registry_instances_manage_state_independently(self):
        registry = self.room_manager.RoomRegistry()

        first_player_number, first_room_id, first_created = registry.assign_player_slot()
        second_player_number, second_room_id, second_created = registry.assign_player_slot()

        self.assertEqual((first_player_number, first_room_id, first_created), (0, 0, True))
        self.assertEqual((second_player_number, second_room_id, second_created), (1, 0, False))
        self.assertEqual(registry.games[0].ai[:2], [False, False])
        self.assertEqual(self.room_manager.games, {})

    def test_room_registry_builds_assignment_and_room_state_messages(self):
        registry = self.room_manager.RoomRegistry()
        player_number, room_id, _ = registry.assign_player_slot()

        assignment_message = registry.build_assignment_message(room_id, player_number)
        room_state_message = registry.build_room_state_message(room_id, player_number)

        self.assertTrue(is_message_type(assignment_message, PLAYER_ASSIGNMENT_MESSAGE))
        self.assertEqual(assignment_message["player_number"], player_number)
        self.assertEqual(assignment_message["room_id"], room_id)
        self.assertEqual(
            extract_assignment_gameplay_state(assignment_message)["cannon_reload_ticks_remaining"],
            registry.games[room_id].cannon_reload_duration_ticks,
        )
        self.assertTrue(is_message_type(room_state_message, ROOM_STATE_MESSAGE))
        self.assertEqual(len(room_state_message["entities"]), 5)
        self.assertIsNotNone(extract_room_state_self_player(room_state_message))
        self.assertEqual(extract_room_state_damage_markers(room_state_message), [])
        self.assertEqual(extract_room_state_enemy_projectiles(room_state_message), [])
        self.assertEqual(extract_room_state_player_projectiles(room_state_message), [])
        self.assertEqual(
            extract_room_state_gameplay_state(room_state_message)["tick_rate_hz"],
            registry.games[room_id].tick_rate_hz,
        )

    def test_room_registry_applies_player_updates_without_direct_game_access(self):
        registry = self.room_manager.RoomRegistry()
        player_number, room_id, _ = registry.assign_player_slot()
        snapshot = create_player_snapshot(registry.games[room_id].crew_members[player_number])
        snapshot["x"] += 25
        snapshot["y"] += 10

        applied = registry.apply_player_update(room_id, player_number, snapshot)

        self.assertTrue(applied)
        self.assertEqual(
            (registry.games[room_id].crew_members[player_number].x, registry.games[room_id].crew_members[player_number].y),
            (snapshot["x"], snapshot["y"]),
        )

    def test_room_registry_does_not_trust_client_reported_repairs(self):
        registry = self.room_manager.RoomRegistry()
        player_number, room_id, _ = registry.assign_player_slot()
        registry.games[room_id].damage_markers = [(10, 20), (30, 40)]
        snapshot = create_player_snapshot(registry.games[room_id].crew_members[player_number])

        applied = registry.apply_player_update(
            room_id,
            player_number,
            snapshot,
            repaired_damage_markers=[(10, 20)],
        )

        self.assertTrue(applied)
        self.assertEqual(registry.games[room_id].damage_markers, [(10, 20), (30, 40)])

    def test_room_registry_preserves_server_authoritative_inventory_and_shot_state(self):
        registry = self.room_manager.RoomRegistry()
        player_number, room_id, _ = registry.assign_player_slot()
        game = registry.games[room_id]
        snapshot = create_player_snapshot(game.crew_members[player_number])
        snapshot["x"] += 25
        snapshot["inventoryWood"] = 0
        snapshot["inventoryCannon"] = 0
        snapshot["cannonBallAnimationX"] = 123
        snapshot["cannonBallAnimationY"] = 456
        snapshot["targetX"] = 789
        snapshot["targetY"] = 321

        applied = registry.apply_player_update(
            room_id,
            player_number,
            snapshot,
            action_state={
                "action_pressed": True,
                "repair_target": (10, 20),
                "aim_target": (300, 400),
            },
        )

        crew_member = game.crew_members[player_number]
        self.assertTrue(applied)
        self.assertEqual(crew_member.x, snapshot["x"])
        self.assertEqual((crew_member.inventoryWood, crew_member.inventoryCannon), (9, 9))
        self.assertEqual(
            (crew_member.cannonBallAnimationX, crew_member.cannonBallAnimationY),
            (-1000, -1000),
        )
        self.assertEqual((crew_member.targetX, crew_member.targetY), (-1000, -1000))
        self.assertTrue(game.action_pressed[player_number])
        self.assertEqual(game.requested_repair_targets[player_number], (10, 20))
        self.assertEqual(game.aim_targets[player_number], (300, 400))
