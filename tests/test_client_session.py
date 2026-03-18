import unittest

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()

from better_together_client.session import FramePromptState, GameplaySessionState


class ClientSessionStateTests(unittest.TestCase):
    def test_begin_frame_returns_clean_prompt_state(self):
        session_state = GameplaySessionState()

        frame_state = session_state.begin_frame()

        self.assertIsInstance(frame_state, FramePromptState)
        self.assertFalse(frame_state.shoot_info_displayed)
        self.assertFalse(frame_state.repair_info_displayed)

    def test_queue_and_consume_repaired_damage_markers(self):
        session_state = GameplaySessionState()
        session_state.queue_repaired_damage_marker((10, 20))
        session_state.queue_repaired_damage_marker((30, 40))

        repaired_damage_markers = session_state.consume_repaired_damage_markers()

        self.assertEqual(repaired_damage_markers, [(10, 20), (30, 40)])
        self.assertEqual(session_state.pending_repaired_damage_markers, [])

    def test_apply_authoritative_state_updates_session_view(self):
        session_state = GameplaySessionState()

        session_state.apply_authoritative_state(
            {
                "tick_rate_hz": 20,
                "game_over": True,
                "game_over_ticks_remaining": 199,
                "repair_target": (10, 20),
                "repair_ticks_remaining": 15,
                "repair_duration_ticks": 60,
                "cannon_reload_ticks_remaining": 9,
                "cannon_reload_duration_ticks": 60,
            }
        )

        self.assertTrue(session_state.game_over)
        self.assertTrue(session_state.authoritative_state.game_over)
        self.assertEqual(session_state.authoritative_state.repair_target, (10, 20))
        self.assertEqual(session_state.authoritative_state.cannon_reload_ticks_remaining, 9)
        self.assertAlmostEqual(session_state.authoritative_state.seconds_remaining(15), 0.75)

    def test_create_action_state_normalizes_targets(self):
        session_state = GameplaySessionState()

        action_state = session_state.create_action_state(
            action_pressed=True,
            repair_target=[10, 20],
            aim_target=[30, 40],
        )

        self.assertEqual(
            action_state,
            {
                "action_pressed": True,
                "repair_target": (10, 20),
                "aim_target": (30, 40),
            },
        )

    def test_movement_hint_persists_until_movement_then_counts_down(self):
        session_state = GameplaySessionState()

        self.assertTrue(session_state.should_show_movement_hint())

        session_state.register_local_movement(post_move_ticks=2)
        self.assertTrue(session_state.should_show_movement_hint())

        session_state.begin_frame()
        self.assertTrue(session_state.should_show_movement_hint())

        session_state.begin_frame()
        self.assertFalse(session_state.should_show_movement_hint())
