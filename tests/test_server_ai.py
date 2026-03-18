import importlib
import unittest
from unittest.mock import patch

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()


class ServerAISimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ai = importlib.import_module("better_together_server.ai")
        cls.room_manager = importlib.import_module("better_together_server.room_manager")

    def setUp(self):
        self.room_manager.reset_rooms()

    def tearDown(self):
        self.room_manager.reset_rooms()

    def test_advance_ready_rooms_ticks_due_rooms_by_elapsed_time(self):
        registry = self.room_manager.RoomRegistry()
        _, room_id, _ = registry.assign_player_slot()
        game = registry.games[room_id]
        now = 100.0
        game.last_simulation_tick_at = now - (3.25 * game.tick_interval_seconds)

        with patch.object(self.ai, "advance_game") as mock_advance_game:
            self.ai.advance_ready_rooms(room_registry=registry, now=now)

        self.assertEqual(mock_advance_game.call_count, 3)

    def test_advance_ready_rooms_skips_when_no_tick_is_due(self):
        registry = self.room_manager.RoomRegistry()
        _, room_id, _ = registry.assign_player_slot()
        game = registry.games[room_id]
        now = 200.0
        game.last_simulation_tick_at = now - (0.5 * game.tick_interval_seconds)

        with patch.object(self.ai, "advance_game") as mock_advance_game:
            self.ai.advance_ready_rooms(room_registry=registry, now=now)

        mock_advance_game.assert_not_called()

    def test_advance_resource_refills_restores_empty_inventory(self):
        registry = self.room_manager.RoomRegistry()
        _, room_id, _ = registry.assign_player_slot()
        game = registry.games[room_id]
        crew_member = game.crew_members[0]
        crew_member.inventoryCannon = 0
        crew_member.inventoryWood = 0
        game.inventory_cannon_refill_ticks[0] = game.resource_refill_interval_ticks - 1
        game.inventory_wood_refill_ticks[0] = game.resource_refill_interval_ticks - 1

        self.ai.advance_resource_refills(game)

        self.assertEqual(crew_member.inventoryCannon, 9)
        self.assertEqual(crew_member.inventoryWood, 9)

    def test_advance_enemy_attacks_spawns_authoritative_enemy_projectile(self):
        registry = self.room_manager.RoomRegistry()
        _, room_id, _ = registry.assign_player_slot()
        game = registry.games[room_id]
        game.enemy_attack_cooldown_ticks = game.enemy_attack_interval_ticks - 1

        with patch.object(self.ai.random, "choice", side_effect=lambda options: options[0]):
            with patch.object(self.ai.random, "randrange", return_value=0):
                self.ai.advance_enemy_attacks(game)

        self.assertEqual(len(game.enemy_projectiles), 1)
        self.assertEqual(game.damage_markers, [])
        projectile = game.enemy_projectiles[0]
        self.assertEqual(
            (projectile["origin_x"], projectile["origin_y"]),
            (
                game.pirate_ships[0].x + game.pirate_ships[0].width // 4,
                game.pirate_ships[0].y + game.pirate_ships[0].height // 4,
            ),
        )
        self.assertEqual(
            (projectile["impact_x"], projectile["impact_y"]),
            (
                game.crew_members[0].x + game.crew_members[0].width // 4,
                game.crew_members[0].y + game.crew_members[0].height // 4,
            ),
        )

    def test_advance_enemy_projectiles_land_as_damage_markers(self):
        registry = self.room_manager.RoomRegistry()
        _, room_id, _ = registry.assign_player_slot()
        game = registry.games[room_id]
        game.enemy_attack_cooldown_ticks = game.enemy_attack_interval_ticks - 1

        with patch.object(self.ai.random, "choice", side_effect=lambda options: options[0]):
            with patch.object(self.ai.random, "randrange", return_value=0):
                self.ai.advance_enemy_attacks(game)

        for _ in range(game.tick_rate_hz):
            self.ai.advance_enemy_projectiles(game)

        self.assertEqual(game.enemy_projectiles, [])
        self.assertEqual(
            game.damage_markers,
            [
                (
                    game.crew_members[0].x + game.crew_members[0].width // 4,
                    game.crew_members[0].y + game.crew_members[0].height // 4,
                )
            ],
        )

    def test_advance_player_repairs_removes_damage_marker_authoritatively(self):
        registry = self.room_manager.RoomRegistry()
        player_number, room_id, _ = registry.assign_player_slot()
        game = registry.games[room_id]
        crew_member = game.crew_members[player_number]
        repair_target = (crew_member.x, crew_member.y)
        game.damage_markers = [repair_target]
        game.update_action_state(
            player_number,
            {
                "action_pressed": True,
                "repair_target": repair_target,
            },
        )

        for _ in range(game.repair_duration_ticks):
            self.ai.advance_player_repairs(game)

        self.assertEqual(game.damage_markers, [])
        self.assertEqual(crew_member.inventoryWood, 8)
        self.assertEqual(game.repair_ticks_remaining[player_number], game.repair_duration_ticks)

    def test_advance_player_cannon_actions_uses_authoritative_reload_and_fire_request(self):
        registry = self.room_manager.RoomRegistry()
        player_number, room_id, _ = registry.assign_player_slot()
        game = registry.games[room_id]
        crew_member = game.crew_members[player_number]
        crew_member.x = 500
        crew_member.y = 500
        game.cannon_reload_ticks_remaining[player_number] = 1

        game.update_action_state(
            player_number,
            {
                "action_pressed": True,
                "aim_target": (350, 120),
            },
        )
        self.ai.advance_player_cannon_actions(game)

        self.assertEqual(game.cannon_reload_ticks_remaining[player_number], 0)

        game.update_action_state(
            player_number,
            {
                "action_pressed": False,
                "aim_target": (350, 120),
            },
        )
        self.ai.advance_player_cannon_actions(game)

        self.assertEqual(crew_member.inventoryCannon, 8)
        self.assertEqual(
            game.cannon_reload_ticks_remaining[player_number],
            game.cannon_reload_duration_ticks,
        )
        self.assertIsNotNone(game.active_shots[player_number])
        self.assertEqual(game.player_projectile_positions(), [(crew_member.x - 60, crew_member.y + 20)])
        self.assertEqual((crew_member.targetX, crew_member.targetY), (-1000, -1000))
        self.assertEqual((crew_member.cannonBallAnimationX, crew_member.cannonBallAnimationY), (-1000, -1000))

    def test_advance_player_projectiles_resolves_hits_against_pirate_ships(self):
        registry = self.room_manager.RoomRegistry()
        player_number, room_id, _ = registry.assign_player_slot()
        game = registry.games[room_id]
        pirate_ship = game.pirate_ships[0]
        game.active_shots[player_number] = {
            "origin_x": pirate_ship.x,
            "origin_y": pirate_ship.y,
            "x": pirate_ship.x,
            "y": pirate_ship.y,
            "target_x": pirate_ship.x,
            "target_y": pirate_ship.y,
            "ticks_elapsed": 0,
            "total_ticks": 1,
        }

        self.ai.advance_player_projectiles(game)

        self.assertIsNone(game.active_shots[player_number])
        self.assertEqual(game.player_projectile_positions(), [])
        self.assertEqual((pirate_ship.x, pirate_ship.y), (self.ai.WINDOW_WIDTH // 2, -600))

    def test_advance_game_over_state_marks_match_authoritatively(self):
        registry = self.room_manager.RoomRegistry()
        player_number, room_id, _ = registry.assign_player_slot()
        game = registry.games[room_id]
        game.damage_markers = [(index, index) for index in range(game.game_over_damage_threshold)]

        marked_over = self.ai.advance_game_over_state(game)

        self.assertTrue(marked_over)
        self.assertTrue(game.game_over)
        self.assertEqual(game.game_over_ticks_remaining, game.game_over_delay_ticks)
        self.assertTrue(game.gameplay_state_for(player_number)["game_over"])
