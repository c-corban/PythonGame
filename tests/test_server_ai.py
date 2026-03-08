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
