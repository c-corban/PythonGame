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
