"""Client-side networking helpers for Better Together."""

import socket

from better_together_shared.config import CLIENT_SERVER_HOST, CLIENT_SERVER_PORT, NETWORK_BUFFER_SIZE
from better_together_shared.protocol import (
    apply_player_snapshot,
    create_player_from_snapshot,
    create_players_from_room_state,
    create_update_message,
    extract_assigned_player,
    extract_room_state_damage_markers,
    extract_room_state_enemy_projectiles,
    extract_room_state_self_player,
)
from better_together_shared.transport import TransportError, receive_message, send_message


buffer = NETWORK_BUFFER_SIZE
client_player_class = None


def get_client_player_class():
    global client_player_class

    if client_player_class is None:
        from .player import Player as client_player

        client_player_class = client_player

    return client_player_class


class Network:
    def __init__(self):
        self.server = (self.ip, self.port) = (CLIENT_SERVER_HOST, CLIENT_SERVER_PORT)
        self.client = None
        self.room_id = None
        self.player_number = None
        self.player = None
        self.damage_markers = []
        self.enemy_projectiles = []
        self.connected = False

    def getPlayer(self):
        return self.player

    def connect(self):
        if self.connected and self.player is not None:
            return self.player

        if self.client is None:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.client.connect(self.server)
            assignment_message = receive_message(self.client)
            assigned_player_snapshot = extract_assigned_player(assignment_message)
            if assigned_player_snapshot is None:
                return None

            self.room_id = assignment_message.get("room_id")
            self.player_number = assignment_message.get("player_number")
            self.player = create_player_from_snapshot(get_client_player_class(), assigned_player_snapshot)
            self.damage_markers = []
            self.enemy_projectiles = []
            self.connected = True
            return self.player
        except (OSError, TransportError) as errMsg:
            print(errMsg)
            self.close()
            return None

    def send(self, data, repaired_damage_markers=None):
        if self.client is None or self.player is None or not self.connected:
            return []

        try:
            send_message(
                self.client,
                create_update_message(data, repaired_damage_markers=repaired_damage_markers),
            )
            room_state_message = receive_message(self.client)
            self.room_id = room_state_message.get("room_id", self.room_id)
            authoritative_player_snapshot = extract_room_state_self_player(room_state_message)
            if authoritative_player_snapshot is not None:
                apply_player_snapshot(self.player, authoritative_player_snapshot)
            self.damage_markers = extract_room_state_damage_markers(room_state_message)
            self.enemy_projectiles = extract_room_state_enemy_projectiles(room_state_message)
            return create_players_from_room_state(get_client_player_class(), room_state_message)
        except (socket.error, TransportError) as errMsg:
            print(errMsg)
            self.close()
            return []

    def close(self):
        try:
            if self.client is not None:
                self.client.close()
        except OSError:
            pass
        finally:
            self.client = None
            self.connected = False


__all__ = ["Network", "buffer", "client_player_class", "get_client_player_class"]
