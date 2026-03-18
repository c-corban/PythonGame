import importlib
import unittest
from collections import defaultdict
from types import SimpleNamespace
from unittest.mock import Mock, patch

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

    def test_should_start_local_shoot_animation_requires_ready_release(self):
        player = SimpleNamespace(x=500, y=500, width=36, height=48, inventoryCannon=2)
        session_state = GameplaySessionState()
        session_state.apply_authoritative_state(
            {
                "tick_rate_hz": 20,
                "repair_ticks_remaining": 0,
                "repair_duration_ticks": 60,
                "cannon_reload_ticks_remaining": 0,
                "cannon_reload_duration_ticks": 60,
            }
        )
        frame_state = session_state.begin_frame()
        previous_action_state = session_state.create_action_state(
            action_pressed=True,
            aim_target=(350, 120),
        )
        action_state = session_state.create_action_state(
            action_pressed=False,
            aim_target=(350, 120),
        )

        self.assertTrue(
            self.game_loop.should_start_local_shoot_animation(
                previous_action_state,
                action_state,
                session_state,
                player,
                frame_state,
            )
        )

        frame_state.repair_info_displayed = True
        self.assertFalse(
            self.game_loop.should_start_local_shoot_animation(
                previous_action_state,
                action_state,
                session_state,
                player,
                frame_state,
            )
        )

    def test_update_game_over_overlay_uses_authoritative_server_state(self):
        runtime = SimpleNamespace(window=Mock())
        session_state = GameplaySessionState()
        session_state.apply_authoritative_state(
            {
                "tick_rate_hz": 20,
                "game_over": True,
                "game_over_ticks_remaining": 5,
                "repair_ticks_remaining": 0,
                "repair_duration_ticks": 60,
                "cannon_reload_ticks_remaining": 0,
                "cannon_reload_duration_ticks": 60,
            }
        )
        fake_font = Mock()
        fake_font.render.return_value = object()

        with patch.object(self.game_loop.pygame.font, "SysFont", return_value=fake_font):
            keep_running = self.game_loop.update_game_over_overlay(runtime, session_state)

        self.assertTrue(keep_running)
        runtime.window.blit.assert_called_once()

    def test_main_refreshes_before_interaction_handlers_and_sends_pending_action_state(self):
        call_order = []
        runtime = SimpleNamespace(
            window=Mock(),
            font=Mock(),
            hit=[],
            enemy_projectiles=[],
        )
        server = SimpleNamespace(
            gameplay_state={
                "tick_rate_hz": 20,
                "game_over": False,
                "game_over_ticks_remaining": 0,
                "repair_target": None,
                "repair_ticks_remaining": 60,
                "repair_duration_ticks": 60,
                "cannon_reload_ticks_remaining": 60,
                "cannon_reload_duration_ticks": 60,
            },
            close=Mock(),
        )
        player = SimpleNamespace()
        key_state = defaultdict(bool)

        def fake_sync(server_arg, player_arg, runtime_arg, session_state_arg, action_state=None):
            call_order.append(("sync", action_state))
            return []

        def fake_refresh(runtime_arg, player_arg, player_others_arg):
            call_order.append("refresh")

        def fake_handle_repairs(runtime_arg, session_state_arg, player_arg, frame_state_arg, keys_arg, action_state_arg):
            call_order.append("repairs")
            return {
                "action_pressed": True,
                "repair_target": (10, 20),
                "aim_target": None,
            }

        def fake_handle_cannon_controls(runtime_arg, session_state_arg, player_arg, frame_state_arg, keys_arg, action_state_arg):
            call_order.append("cannon")
            return action_state_arg

        fake_clock = SimpleNamespace(tick=Mock())

        with patch.object(self.game_loop, "connect_to_server", return_value=(server, player)):
            with patch.object(self.game_loop, "sync_remote_players", side_effect=fake_sync):
                with patch.object(self.game_loop.render, "initialize_runtime", return_value=runtime):
                    with patch.object(self.game_loop.render, "refresh", side_effect=fake_refresh):
                        with patch.object(self.game_loop.render, "shutdown_runtime"):
                            with patch.object(self.game_loop, "handle_repairs", side_effect=fake_handle_repairs):
                                with patch.object(self.game_loop, "handle_cannon_controls", side_effect=fake_handle_cannon_controls):
                                    with patch.object(self.game_loop, "update_game_over_overlay", return_value=False):
                                        with patch.object(self.game_loop.pygame.time, "Clock", return_value=fake_clock):
                                            with patch.object(self.game_loop.pygame.event, "get", return_value=[]):
                                                with patch.object(self.game_loop.pygame.key, "get_pressed", return_value=key_state):
                                                    with patch.object(self.game_loop.pygame.display, "update"):
                                                        with patch.object(self.game_loop.pygame, "quit"):
                                                            self.game_loop.main()

        self.assertEqual(
            call_order,
            [
                ("sync", {"action_pressed": False, "repair_target": None, "aim_target": None}),
                "refresh",
                "repairs",
                "cannon",
            ],
        )
        server.close.assert_called_once()

    def test_draw_action_prompt_renders_icon_and_progress_bar(self):
        prompt_surface = Mock()
        prompt_surface.get_height.return_value = 18
        prompt_surface.get_width.return_value = 140
        bar_label_surface = Mock()
        bar_label_surface.get_height.return_value = 12
        bar_label_surface.get_width.return_value = 70
        icon = Mock()
        icon.get_width.return_value = 16
        icon.get_height.return_value = 16
        runtime = SimpleNamespace(
            window=Mock(),
            font=Mock(),
        )
        runtime.font.render.return_value = prompt_surface

        fake_bar_label_font = Mock()
        fake_bar_label_font.render.return_value = bar_label_surface

        with patch.object(self.game_loop.pygame.draw, "rect") as mock_draw_rect:
            with patch.object(self.game_loop.pygame.font, "SysFont", return_value=fake_bar_label_font) as mock_sys_font:
                self.game_loop.draw_action_prompt(
                    runtime,
                    "Hold SPACE to reload",
                    progress_ratio=0.5,
                    icon=icon,
                )

        runtime.font.render.assert_called_once_with("Hold SPACE to reload", True, (255, 255, 255))
        mock_sys_font.assert_called_once_with(None, self.game_loop.ACTION_PROMPT_BAR_LABEL_FONT_SIZE)
        fake_bar_label_font.render.assert_called_once_with(
            self.game_loop.ACTION_PROMPT_BAR_LABEL,
            True,
            self.game_loop.ACTION_PROMPT_BAR_LABEL_COLOR,
        )
        content_width = max(140, self.game_loop.ACTION_PROMPT_BAR_WIDTH + 16 + self.game_loop.ACTION_PROMPT_ICON_GAP)
        content_left = (self.game_loop.render.width - content_width) // 2
        row_y = self.game_loop.render.height - self.game_loop.ACTION_PROMPT_BOTTOM_MARGIN - self.game_loop.ACTION_PROMPT_BAR_HEIGHT
        runtime.window.blit.assert_any_call(
            prompt_surface,
            (
                content_left + (content_width - 140) // 2,
                row_y - self.game_loop.ACTION_PROMPT_STACK_GAP - 18,
            ),
        )
        runtime.window.blit.assert_any_call(icon, (content_left, row_y + (self.game_loop.ACTION_PROMPT_BAR_HEIGHT - 16) // 2))
        runtime.window.blit.assert_any_call(
            bar_label_surface,
            (
                content_left + 16 + self.game_loop.ACTION_PROMPT_ICON_GAP + (self.game_loop.ACTION_PROMPT_BAR_WIDTH - 70) // 2,
                row_y + (self.game_loop.ACTION_PROMPT_BAR_HEIGHT - 12) // 2,
            ),
        )
        self.assertEqual(mock_draw_rect.call_count, 3)

    def test_handle_repairs_uses_hold_prompt_with_progress_bar(self):
        runtime = SimpleNamespace(
            window=Mock(),
            font=Mock(),
            wood_icon=Mock(),
            hit=[(100, 200)],
        )
        player = SimpleNamespace(x=100, y=200, width=36, height=48, inventoryWood=3)
        session_state = GameplaySessionState()
        session_state.apply_authoritative_state(
            {
                "tick_rate_hz": 20,
                "repair_target": (100, 200),
                "repair_ticks_remaining": 30,
                "repair_duration_ticks": 60,
                "cannon_reload_ticks_remaining": 0,
                "cannon_reload_duration_ticks": 60,
            }
        )
        frame_state = session_state.begin_frame()
        keys = defaultdict(bool)

        with patch.object(self.game_loop, "draw_action_prompt") as mock_draw_action_prompt:
            action_state = self.game_loop.handle_repairs(
                runtime,
                session_state,
                player,
                frame_state,
                keys,
                session_state.create_action_state(),
            )

        mock_draw_action_prompt.assert_called_once_with(
            runtime,
            "Hold SPACE to repair",
            progress_ratio=0.5,
            icon=runtime.wood_icon,
            fill_color=self.game_loop.REPAIR_PROGRESS_COLOR,
        )
        self.assertTrue(frame_state.repair_info_displayed)
        self.assertEqual(action_state["repair_target"], None)

    def test_handle_cannon_controls_uses_hold_prompt_with_progress_bar(self):
        runtime = SimpleNamespace(
            window=Mock(),
            font=Mock(),
            cannonball_icon=Mock(),
        )
        player = SimpleNamespace(x=500, y=500, width=36, height=48, inventoryCannon=3, move=Mock())
        session_state = GameplaySessionState()
        session_state.apply_authoritative_state(
            {
                "tick_rate_hz": 20,
                "repair_ticks_remaining": 0,
                "repair_duration_ticks": 60,
                "cannon_reload_ticks_remaining": 30,
                "cannon_reload_duration_ticks": 60,
            }
        )
        frame_state = session_state.begin_frame()
        keys = defaultdict(bool)

        with patch.object(self.game_loop, "draw_action_prompt") as mock_draw_action_prompt:
            action_state = self.game_loop.handle_cannon_controls(
                runtime,
                session_state,
                player,
                frame_state,
                keys,
                session_state.create_action_state(),
            )

        mock_draw_action_prompt.assert_called_once_with(
            runtime,
            "Hold SPACE to reload",
            progress_ratio=0.5,
            icon=runtime.cannonball_icon,
            fill_color=self.game_loop.RELOAD_PROGRESS_COLOR,
        )
        player.move.assert_called_once()
        self.assertEqual(action_state["aim_target"], (session_state.aim_x, session_state.aim_y))

    def test_move_player_and_track_hint_marks_first_local_movement(self):
        player = SimpleNamespace(x=100, y=200)

        def fake_move():
            player.x += 4

        player.move = fake_move
        session_state = GameplaySessionState()

        self.game_loop.move_player_and_track_hint(session_state, player)

        self.assertTrue(session_state.movement_hint_has_seen_local_movement)
        self.assertEqual(session_state.movement_hint_ticks_remaining, 60 * 3)

    def test_handle_cannon_controls_keeps_movement_hint_visible_until_first_move_and_after(self):
        runtime = SimpleNamespace(window=Mock(), font=Mock())
        player = SimpleNamespace(x=100, y=100, width=36, height=48, inventoryCannon=3)

        def fake_move():
            player.x += 2

        player.move = Mock(side_effect=fake_move)
        session_state = GameplaySessionState()
        frame_state = session_state.begin_frame()
        keys = defaultdict(bool)
        runtime.font.render.return_value = object()

        self.game_loop.handle_cannon_controls(
            runtime,
            session_state,
            player,
            frame_state,
            keys,
            session_state.create_action_state(),
        )

        runtime.window.blit.assert_called()
        self.assertTrue(session_state.should_show_movement_hint())
        self.assertTrue(session_state.movement_hint_has_seen_local_movement)
