import sys
import unittest

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()


from better_together_shared.asset_catalog import (
    DEFAULT_CREW_SELECTION_ASSET_IDS,
    get_pirate_ship_frame_asset_id,
)
from better_together_server.game import Game


class GameRoomInvariantTests(unittest.TestCase):
    def setUp(self):
        self.game = Game(42)

    def test_initial_state_creates_ai_slots_and_pirate_ships(self):
        self.assertEqual(self.game.ai, [True, True, True, True])
        self.assertEqual(len(self.game.crew_members), 4)
        self.assertEqual(len(self.game.pirate_ships), 2)
        self.assertEqual(len(self.game.players), 6)
        self.assertEqual(self.game.pirateShips, self.game.pirate_ships)
        self.assertEqual(self.game.players[:4], self.game.crew_members)
        self.assertEqual(self.game.players[4:], self.game.pirate_ships)

        crew_members = self.game.crew_members
        expected_crew_asset_ids = set(DEFAULT_CREW_SELECTION_ASSET_IDS)

        self.assertEqual(len({crew_member.char for crew_member in crew_members}), 4)
        self.assertEqual({crew_member.char for crew_member in crew_members}, expected_crew_asset_ids)

        for crew_member in crew_members:
            with self.subTest(character=crew_member.char):
                self.assertEqual((crew_member.width, crew_member.height), (self.game.playerWidth, self.game.playerHeight))
                self.assertIn(crew_member.char, expected_crew_asset_ids)

        for pirate_ship in self.game.pirate_ships:
            with self.subTest(ship=pirate_ship.char):
                self.assertIsNone(pirate_ship.animation)
                self.assertEqual((pirate_ship.maxWidth, pirate_ship.maxHeight), (1050, 750))
                self.assertEqual(pirate_ship.char, get_pirate_ship_frame_asset_id(0))

    def test_get_player_claims_an_ai_slot_only_once(self):
        assigned_player = self.game.get_player(1)

        self.assertIs(assigned_player, self.game.crew_members[1])
        self.assertFalse(self.game.ai[1])
        self.assertIsNone(self.game.get_player(1))

    def test_play_replaces_the_stored_slot_state(self):
        replacement_state = object()

        self.game.play(3, replacement_state)

        self.assertIs(self.game.crew_members[3], replacement_state)
        self.assertIs(self.game.players[3], replacement_state)

    def test_consume_pending_simulation_steps_uses_elapsed_time(self):
        base_time = 100.0
        self.game.last_simulation_tick_at = base_time

        due_steps = self.game.consume_pending_simulation_steps(
            now=base_time + (3.5 * self.game.tick_interval_seconds)
        )

        self.assertEqual(due_steps, 3)
        self.assertAlmostEqual(
            self.game.last_simulation_tick_at,
            base_time + (3 * self.game.tick_interval_seconds),
        )

    def test_consume_pending_simulation_steps_caps_large_backlogs(self):
        base_time = 50.0
        self.game.last_simulation_tick_at = base_time

        due_steps = self.game.consume_pending_simulation_steps(
            now=base_time + (20 * self.game.tick_interval_seconds),
            max_steps=2,
        )

        self.assertEqual(due_steps, 2)
        self.assertAlmostEqual(
            self.game.last_simulation_tick_at,
            base_time + (2 * self.game.tick_interval_seconds),
        )
