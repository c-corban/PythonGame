import os
import queue
import socket
import subprocess
import sys
import threading
import time
import unittest

try:
    from tests.test_support import ROOT_DIR, add_workspace_package_paths, build_workspace_pythonpath
except ModuleNotFoundError:
    from test_support import ROOT_DIR, add_workspace_package_paths, build_workspace_pythonpath

add_workspace_package_paths()

from better_together_shared.config import CLIENT_SERVER_HOST, CLIENT_SERVER_PORT, NETWORK_BUFFER_SIZE
from better_together_shared.protocol import (
    PIRATE_SHIP_ENTITY_KIND,
    PLAYER_ASSIGNMENT_MESSAGE,
    PLAYER_UPDATE_MESSAGE,
    PROTOCOL_VERSION,
    ROOM_STATE_MESSAGE,
    create_update_message,
    extract_assigned_player,
    extract_room_state_damage_markers,
    extract_room_state_self_player,
    is_message_type,
)
from better_together_shared.transport import ConnectionClosedError, receive_message, send_message


HOST = CLIENT_SERVER_HOST
PORT = CLIENT_SERVER_PORT
BUFFER = NETWORK_BUFFER_SIZE


class OutputCollector:
    def __init__(self, stream):
        self.lines = []
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self._read_stream, args=(stream,), daemon=True)
        self.thread.start()

    def _read_stream(self, stream):
        for line in stream:
            stripped_line = line.rstrip()
            self.lines.append(stripped_line)
            self.queue.put(stripped_line)

    def wait_for(self, predicate, timeout):
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            for line in self.lines:
                if predicate(line):
                    return line

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break

            try:
                line = self.queue.get(timeout=min(0.25, remaining))
            except queue.Empty:
                continue

            if predicate(line):
                return line

        return None


class ServerProtocolIntegrationTests(unittest.TestCase):
    def test_server_handshake_reply_and_room_cleanup(self):
        if not self.port_is_available():
            self.skipTest("Port 2911 is already in use; skipping live server integration test.")

        server_process, output_collector = self.start_server_process()

        try:
            waiting_line = output_collector.wait_for(lambda line: "Waiting for connections" in line, timeout=10)
            self.assertIsNotNone(waiting_line, self.format_output("Server never reported it was ready", output_collector))

            with socket.create_connection((HOST, PORT), timeout=5) as client_socket:
                client_socket.settimeout(5)

                assignment_message = receive_message(client_socket)
                self.assertTrue(is_message_type(assignment_message, PLAYER_ASSIGNMENT_MESSAGE))
                self.assertEqual(assignment_message.get("room_id"), 0)
                self.assertEqual(assignment_message.get("player_number"), 0)

                assigned_player = extract_assigned_player(assignment_message)
                self.assertIsNotNone(assigned_player)
                self.assertEqual((assigned_player["x"], assigned_player["y"]), (480, 780))

                send_message(client_socket, create_update_message(assigned_player))
                reply_message = receive_message(client_socket)
                self.assertTrue(is_message_type(reply_message, ROOM_STATE_MESSAGE))
                self.assertEqual(reply_message.get("room_id"), 0)
                self.assertEqual(extract_room_state_self_player(reply_message)["x"], assigned_player["x"])
                self.assertEqual(extract_room_state_damage_markers(reply_message), [])

                reply = reply_message.get("entities", [])

                self.assertEqual(len(reply), 5)
                self.assertEqual(sum(1 for entity in reply if entity.get("entity_kind") == PIRATE_SHIP_ENTITY_KIND), 2)
                self.assertEqual(sum(1 for entity in reply if entity.get("animation") is None), 2)

            lost_connection_line = output_collector.wait_for(lambda line: "Lost connection with" in line, timeout=10)
            self.assertIsNotNone(lost_connection_line, self.format_output("Server never logged the disconnect", output_collector))

            closed_room_line = output_collector.wait_for(lambda line: "Closed room with ID: 0" in line, timeout=10)
            self.assertIsNotNone(closed_room_line, self.format_output("Server never cleaned up the empty room", output_collector))
        finally:
            self.stop_server_process(server_process, output_collector)

    def test_server_rejects_malformed_player_update_and_cleans_room(self):
        if not self.port_is_available():
            self.skipTest("Port 2911 is already in use; skipping live server integration test.")

        server_process, output_collector = self.start_server_process()

        try:
            waiting_line = output_collector.wait_for(lambda line: "Waiting for connections" in line, timeout=10)
            self.assertIsNotNone(waiting_line, self.format_output("Server never reported it was ready", output_collector))

            with socket.create_connection((HOST, PORT), timeout=5) as client_socket:
                client_socket.settimeout(5)

                assignment_message = receive_message(client_socket)
                assigned_player = extract_assigned_player(assignment_message)
                self.assertIsNotNone(assigned_player)

                malformed_player = dict(assigned_player)
                malformed_player.pop("targetY")

                send_message(
                    client_socket,
                    {
                        "protocol_version": PROTOCOL_VERSION,
                        "message_type": PLAYER_UPDATE_MESSAGE,
                        "player": malformed_player,
                    },
                )

                with self.assertRaises(ConnectionClosedError):
                    receive_message(client_socket)

            lost_connection_line = output_collector.wait_for(lambda line: "Lost connection with" in line, timeout=10)
            self.assertIsNotNone(lost_connection_line, self.format_output("Server never logged the malformed disconnect", output_collector))

            closed_room_line = output_collector.wait_for(lambda line: "Closed room with ID: 0" in line, timeout=10)
            self.assertIsNotNone(closed_room_line, self.format_output("Server never cleaned up the malformed session room", output_collector))
        finally:
            self.stop_server_process(server_process, output_collector)

    def start_server_process(self):
        environment = os.environ.copy()
        environment.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
        environment.setdefault("SDL_AUDIODRIVER", "dummy")
        environment["SDL_VIDEODRIVER"] = "better_together_headless_test"
        environment["PYTHONPATH"] = build_workspace_pythonpath()

        server_process = subprocess.Popen(
            [sys.executable, "-u", "-m", "better_together_server"],
            cwd=ROOT_DIR,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        self.assertIsNotNone(server_process.stdout)
        return server_process, OutputCollector(server_process.stdout)

    def stop_server_process(self, server_process, output_collector):
        if server_process.poll() is not None:
            if server_process.stdout is not None and not server_process.stdout.closed:
                server_process.stdout.close()
            output_collector.thread.join(timeout=1)
            return

        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
            server_process.wait(timeout=5)

        if server_process.stdout is not None and not server_process.stdout.closed:
            server_process.stdout.close()
        output_collector.thread.join(timeout=1)

    def port_is_available(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe_socket:
            try:
                probe_socket.bind((HOST, PORT))
            except OSError:
                return False

        return True

    def format_output(self, message, output_collector):
        joined_output = "\n".join(output_collector.lines) or "<no output captured>"
        return f"{message}. Captured server output:\n{joined_output}"
