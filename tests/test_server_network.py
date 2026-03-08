import importlib
import threading
import unittest
from unittest.mock import Mock, patch

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()

from better_together_shared.protocol import create_player_snapshot, create_update_message


class ServerNetworkLifecycleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.network = importlib.import_module("better_together_server.network")
        cls.room_manager = importlib.import_module("better_together_server.room_manager")

    def setUp(self):
        self.room_manager.reset_rooms()

    def tearDown(self):
        self.room_manager.reset_rooms()

    def test_client_thread_releases_room_when_assignment_send_fails(self):
        player_number, room_id, _ = self.room_manager.assign_player_slot()
        connection = Mock()

        with patch.object(self.network, "send_message", side_effect=OSError("boom")):
            self.network.client_thread(connection, player_number, room_id, ("127.0.0.1", 2911))

        self.assertNotIn(room_id, self.room_manager.games)
        connection.close.assert_called_once()

    def test_client_thread_uses_injected_room_registry(self):
        registry = self.room_manager.RoomRegistry()
        player_number, room_id, _ = registry.assign_player_slot()
        connection = Mock()

        with patch.object(self.network, "send_message", side_effect=OSError("boom")):
            self.network.client_thread(connection, player_number, room_id, ("127.0.0.1", 2911), registry)

        self.assertNotIn(room_id, registry.games)
        self.assertEqual(self.room_manager.games, {})
        connection.close.assert_called_once()

    def test_client_thread_does_not_advance_ai_from_player_updates(self):
        registry = self.room_manager.RoomRegistry()
        player_number, room_id, _ = registry.assign_player_slot()
        connection = Mock()
        player_snapshot = create_player_snapshot(registry.games[room_id].crew_members[player_number])

        with patch.object(self.network, "receive_message", side_effect=[create_update_message(player_snapshot), OSError("disconnect")]):
            with patch.object(self.network, "send_message"):
                with patch.object(registry, "apply_player_update", wraps=registry.apply_player_update) as mock_apply_player_update:
                    with patch.object(registry, "build_room_state_message", wraps=registry.build_room_state_message) as mock_build_room_state_message:
                        self.network.client_thread(connection, player_number, room_id, ("127.0.0.1", 2911), registry)

        mock_apply_player_update.assert_called_once()
        mock_build_room_state_message.assert_called_once_with(room_id, player_number)
        self.assertFalse(hasattr(self.network, "ai_move"))
        self.assertFalse(hasattr(self.network, "ship_ai"))

    def test_start_client_session_thread_uses_managed_threading(self):
        registry = self.room_manager.RoomRegistry()
        player_number, room_id, _ = registry.assign_player_slot()
        session_threads = []

        with patch.object(self.network, "client_thread") as mock_client_thread:
            session_thread = self.network.start_client_session_thread(
                Mock(),
                player_number,
                room_id,
                ("127.0.0.1", 2911),
                room_registry=registry,
                session_threads=session_threads,
            )
            session_thread.join(timeout=1)

        self.assertIsInstance(session_thread, threading.Thread)
        self.assertEqual(session_threads, [session_thread])
        mock_client_thread.assert_called_once()

    def test_prune_finished_session_threads_removes_dead_threads(self):
        finished_thread = threading.Thread(target=lambda: None)
        finished_thread.start()
        finished_thread.join(timeout=1)
        session_threads = [finished_thread]

        alive_threads = self.network.prune_finished_session_threads(session_threads)

        self.assertEqual(alive_threads, [])
        self.assertEqual(session_threads, [])
