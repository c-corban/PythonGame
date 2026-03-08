import importlib
import unittest

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()


class PackageEntrypointImportTests(unittest.TestCase):
    def test_client_app_import_is_safe_and_exposes_main(self):
        client_app = importlib.import_module("better_together_client.app")

        self.assertTrue(callable(client_app.main))
        self.assertTrue(callable(client_app.refresh))
        self.assertTrue(callable(client_app.Network))
        self.assertIsNone(client_app.window)

    def test_client_split_modules_import_safely(self):
        client_assets = importlib.import_module("better_together_client.assets")
        client_cli = importlib.import_module("better_together_client.cli")
        client_main = importlib.import_module("better_together_client.__main__")
        client_network = importlib.import_module("better_together_client.network")
        client_player = importlib.import_module("better_together_client.player")
        client_render = importlib.import_module("better_together_client.render")
        client_session = importlib.import_module("better_together_client.session")
        client_game_loop = importlib.import_module("better_together_client.game_loop")

        self.assertTrue(callable(client_assets.load_image))
        self.assertTrue(callable(client_cli.main))
        self.assertTrue(callable(client_main.main))
        self.assertTrue(callable(client_network.Network))
        self.assertTrue(callable(client_network.get_client_player_class))
        self.assertTrue(callable(client_network.Network.connect))
        self.assertTrue(callable(client_player.Player))
        self.assertTrue(callable(client_render.RenderRuntime))
        self.assertTrue(callable(client_render.get_runtime))
        self.assertTrue(callable(client_render.initialize_runtime))
        self.assertTrue(callable(client_render.refresh))
        self.assertTrue(callable(client_session.GameplaySessionState))
        self.assertTrue(callable(client_game_loop.main))
        self.assertTrue(client_assets.BASE_DIR)
        self.assertIsNone(client_render.window)

    def test_shared_split_modules_import_safely(self):
        shared_package = importlib.import_module("better_together_shared")
        shared_assets_runtime = importlib.import_module("better_together_shared.assets_runtime")
        shared_config = importlib.import_module("better_together_shared.config")
        shared_protocol = importlib.import_module("better_together_shared.protocol")
        shared_transport = importlib.import_module("better_together_shared.transport")

        self.assertTrue(callable(shared_package.create_update_message))
        self.assertTrue(callable(shared_package.receive_message))
        self.assertTrue(callable(shared_assets_runtime.load_image))
        self.assertTrue(callable(shared_assets_runtime.load_scaled_image))
        self.assertEqual(shared_config.SERVER_BIND_PORT, 2911)
        self.assertTrue(callable(shared_protocol.create_update_message))
        self.assertTrue(callable(shared_protocol.validate_message))
        self.assertTrue(callable(shared_transport.receive_message))
        self.assertEqual(shared_transport.MAX_MESSAGE_SIZE, shared_config.NETWORK_BUFFER_SIZE)

    def test_server_app_import_is_safe_and_exposes_main(self):
        server_app = importlib.import_module("better_together_server.app")

        self.assertTrue(callable(server_app.main))
        self.assertTrue(callable(server_app.aiMove))
        self.assertTrue(callable(server_app.clientThread))
        self.assertIsInstance(server_app.games, dict)
        self.assertIsNone(server_app.s)
        self.assertIsNone(server_app.window)

    def test_server_split_modules_import_safely(self):
        server_assets = importlib.import_module("better_together_server.assets")
        server_ai = importlib.import_module("better_together_server.ai")
        server_cli = importlib.import_module("better_together_server.cli")
        server_game = importlib.import_module("better_together_server.game")
        server_main = importlib.import_module("better_together_server.__main__")
        server_network = importlib.import_module("better_together_server.network")
        server_player = importlib.import_module("better_together_server.player")
        server_room_manager = importlib.import_module("better_together_server.room_manager")

        self.assertTrue(callable(server_assets.load_image))
        self.assertTrue(callable(server_ai.ai_move))
        self.assertTrue(callable(server_ai.ship_ai))
        self.assertTrue(callable(server_cli.main))
        self.assertTrue(callable(server_game.Game))
        self.assertTrue(callable(server_main.main))
        self.assertTrue(callable(server_network.client_thread))
        self.assertTrue(callable(server_network.start_client_session_thread))
        self.assertTrue(callable(server_network.join_session_threads))
        self.assertTrue(callable(server_network.serve_forever))
        self.assertTrue(callable(server_player.Player))
        self.assertTrue(callable(server_room_manager.RoomRegistry))
        self.assertTrue(callable(server_room_manager.assign_player_slot))
        self.assertTrue(callable(server_room_manager.release_player_slot))
        self.assertTrue(server_assets.BASE_DIR)
        self.assertIsInstance(server_room_manager.games, dict)
