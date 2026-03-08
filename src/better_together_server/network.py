"""Server-side networking loop helpers."""

import socket
import threading

from better_together_shared.config import NETWORK_BUFFER_SIZE
from better_together_shared.protocol import (
    extract_player_update,
    extract_repaired_damage_markers,
)
from better_together_shared.transport import TransportError, receive_message, send_message

from .room_manager import default_room_registry


buffer = NETWORK_BUFFER_SIZE
DEFAULT_ACCEPT_TIMEOUT_SECONDS = 0.25


def close_connection(connection):
    try:
        connection.close()
    except OSError:
        pass


def _resolve_room_registry(room_registry):
    return default_room_registry if room_registry is None else room_registry


def prune_finished_session_threads(session_threads):
    if session_threads is None:
        return []

    alive_threads = [thread for thread in session_threads if thread.is_alive()]
    session_threads[:] = alive_threads
    return alive_threads


def start_client_session_thread(connection, player_number, game_id, address, room_registry=None, session_threads=None):
    room_registry = _resolve_room_registry(room_registry)
    session_thread = threading.Thread(
        target=client_thread,
        args=(connection, player_number, game_id, address, room_registry),
        daemon=True,
    )
    session_thread.start()
    if session_threads is not None:
        session_threads.append(session_thread)
    return session_thread


def join_session_threads(session_threads, timeout=1):
    if session_threads is None:
        return

    for session_thread in list(session_threads):
        session_thread.join(timeout=timeout)


def client_thread(connection, player_number, game_id, address, room_registry=None):
    room_registry = _resolve_room_registry(room_registry)

    while True:
        try:
            assignment_message = room_registry.build_assignment_message(game_id, player_number)

            send_message(connection, assignment_message)
            break
        except (OSError, TransportError, KeyError):
            print(f"Lost connection with {address[0]}:{address[1]}")
            room_closed = room_registry.release_player_slot(game_id, player_number)
            if room_closed:
                print("Closed room with ID:", game_id)

            close_connection(connection)
            return

    while True:
        try:
            player_update_message = receive_message(connection)
            player_update_snapshot = extract_player_update(player_update_message)
            if player_update_snapshot is None:
                break
            repaired_damage_markers = extract_repaired_damage_markers(player_update_message)

            if not room_registry.apply_player_update(
                game_id,
                player_number,
                player_update_snapshot,
                repaired_damage_markers=repaired_damage_markers,
            ):
                break
            room_state_message = room_registry.build_room_state_message(game_id, player_number)

            send_message(connection, room_state_message)
        except (OSError, TransportError, KeyError):
            break

    print(f"Lost connection with {address[0]}:{address[1]}")
    room_closed = room_registry.release_player_slot(game_id, player_number)
    if room_closed:
        print("Closed room with ID:", game_id)

    close_connection(connection)


def serve_forever(server_socket, room_registry=None, stop_event=None, session_threads=None, accept_timeout=DEFAULT_ACCEPT_TIMEOUT_SECONDS):
    room_registry = _resolve_room_registry(room_registry)
    server_socket.settimeout(accept_timeout)

    while stop_event is None or not stop_event.is_set():
        try:
            connection, address = server_socket.accept()
        except socket.timeout:
            prune_finished_session_threads(session_threads)
            continue
        except OSError:
            if stop_event is not None and stop_event.is_set():
                break
            raise

        print(f"Connected to {address[0]}:{address[1]}")

        player_number, game_id, room_created = room_registry.assign_player_slot()
        if room_created:
            print("Created room with ID:", game_id)
        else:
            print("Joined room with ID:", game_id)

        prune_finished_session_threads(session_threads)
        start_client_session_thread(
            connection,
            player_number,
            game_id,
            address,
            room_registry=room_registry,
            session_threads=session_threads,
        )

    return prune_finished_session_threads(session_threads)


__all__ = [
    "DEFAULT_ACCEPT_TIMEOUT_SECONDS",
    "buffer",
    "client_thread",
    "join_session_threads",
    "prune_finished_session_threads",
    "serve_forever",
    "start_client_session_thread",
]
