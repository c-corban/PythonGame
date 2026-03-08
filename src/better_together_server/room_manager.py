"""Server-side room allocation and lifecycle helpers."""

import threading
import time

from better_together_shared.protocol import (
    apply_player_snapshot,
    create_assignment_message,
    create_room_state_message,
)

from .game import Game, MAX_SIMULATION_STEPS_PER_ADVANCE


class RoomRegistry:
    """Owns room creation, slot assignment, and cleanup state for the server runtime."""

    def __init__(self):
        self.games = {}
        self.lock = threading.RLock()

    def reset_rooms(self):
        with self.lock:
            self.games.clear()

    def next_room_id(self):
        with self.lock:
            if not self.games:
                return 0

            max_game_id = max(self.games.keys())
            for candidate_room_id in range(max_game_id + 1):
                if candidate_room_id not in self.games:
                    return candidate_room_id

            return max_game_id + 1

    def get_game(self, game_id):
        with self.lock:
            return self.games.get(game_id)

    def build_assignment_message(self, game_id, player_number):
        with self.lock:
            game = self.games.get(game_id)
            if game is None:
                raise KeyError(game_id)

            return create_assignment_message(player_number, game_id, game.crew_members[player_number])

    def apply_player_update(self, game_id, player_number, player_update_snapshot, repaired_damage_markers=None):
        with self.lock:
            game = self.games.get(game_id)
            if game is None:
                return False

            game.remove_damage_markers(repaired_damage_markers)
            apply_player_snapshot(game.crew_members[player_number], player_update_snapshot)
            return True

    def build_room_state_message(self, game_id, player_number):
        with self.lock:
            game = self.games.get(game_id)
            if game is None:
                raise KeyError(game_id)

            return create_room_state_message(
                game_id,
                game.other_entities_for(player_number),
                self_player=game.crew_members[player_number],
                damage_markers=game.damage_markers,
                enemy_projectiles=game.enemy_projectile_positions(),
            )

    def advance_ready_games(self, advance_game_callback, now=None, max_steps_per_room=MAX_SIMULATION_STEPS_PER_ADVANCE):
        if now is None:
            now = time.monotonic()

        with self.lock:
            for game in list(self.games.values()):
                due_steps = game.consume_pending_simulation_steps(now=now, max_steps=max_steps_per_room)
                for _ in range(due_steps):
                    advance_game_callback(game)

    def assign_player_slot(self):
        with self.lock:
            for game_id, game in self.games.items():
                for player_number, ai_controlled in enumerate(game.ai):
                    if ai_controlled:
                        game.ai[player_number] = False
                        return player_number, game_id, False

            game_id = 0
            if self.games:
                max_game_id = max(self.games.keys())
                for candidate_room_id in range(max_game_id + 1):
                    if candidate_room_id not in self.games:
                        game_id = candidate_room_id
                        break
                else:
                    game_id = max_game_id + 1

            self.games[game_id] = Game(game_id)
            self.games[game_id].ai[0] = False
            return 0, game_id, True

    def get_other_entities(self, game_id, player_number):
        with self.lock:
            game = self.games.get(game_id)
            if game is None:
                return []

            return game.other_entities_for(player_number)

    def release_player_slot(self, game_id, player_number):
        with self.lock:
            game = self.games.get(game_id)
            if game is None:
                return False

            game.ai[player_number] = True
            if False not in game.ai:
                del self.games[game_id]
                return True

            return False


default_room_registry = RoomRegistry()
games = default_room_registry.games


def reset_rooms():
    default_room_registry.reset_rooms()


def next_room_id():
    return default_room_registry.next_room_id()


def assign_player_slot():
    return default_room_registry.assign_player_slot()


def get_other_entities(game_id, player_number):
    return default_room_registry.get_other_entities(game_id, player_number)


def release_player_slot(game_id, player_number):
    return default_room_registry.release_player_slot(game_id, player_number)


__all__ = [
    "RoomRegistry",
    "assign_player_slot",
    "default_room_registry",
    "games",
    "get_other_entities",
    "next_room_id",
    "release_player_slot",
    "reset_rooms",
]
