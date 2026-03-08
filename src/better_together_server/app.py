"""Server application entrypoint for Better Together."""

import socket
import threading

from better_together_shared.config import (
    NETWORK_BUFFER_SIZE,
    SERVER_BIND_ADDRESS,
    SERVER_SOCKET_BACKLOG,
    WINDOW_SIZE,
)

from . import ai as ai_module
from . import network as network_module
from . import room_manager as room_manager_module


server = (ip, port) = SERVER_BIND_ADDRESS
buffer = NETWORK_BUFFER_SIZE
size = (width, height) = WINDOW_SIZE

games = room_manager_module.games
aiMove = ai_module.ai_move
shipAi = ai_module.ship_ai
clientThread = network_module.client_thread

s = None
window = None


def main():
    global s, window

    room_registry = room_manager_module.default_room_registry
    room_registry.reset_rooms()
    simulation_stop_event = None
    simulation_thread = None
    server_stop_event = None
    session_threads = []

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind(server)
    except socket.error as errMsg:
        s.close()
        s = None
        raise SystemExit(f"Could not bind server socket on {ip}:{port}: {errMsg}") from errMsg

    s.listen(SERVER_SOCKET_BACKLOG)
    print("Waiting for connections")
    window = None
    simulation_stop_event = threading.Event()
    server_stop_event = threading.Event()
    simulation_thread = threading.Thread(
        target=ai_module.run_simulation_loop,
        kwargs={
            "stop_event": simulation_stop_event,
            "room_registry": room_registry,
        },
        daemon=True,
    )
    simulation_thread.start()

    try:
        network_module.serve_forever(
            s,
            room_registry=room_registry,
            stop_event=server_stop_event,
            session_threads=session_threads,
        )
    finally:
        if server_stop_event is not None:
            server_stop_event.set()
        if simulation_stop_event is not None:
            simulation_stop_event.set()
        if simulation_thread is not None:
            simulation_thread.join(timeout=1)
        network_module.join_session_threads(session_threads, timeout=1)

        if s is not None:
            try:
                s.close()
            except OSError:
                pass
            s = None

        window = None


__all__ = ["aiMove", "buffer", "clientThread", "games", "height", "main", "server", "shipAi", "size", "width"]
