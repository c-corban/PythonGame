"""Server-side room model for Better Together."""
import random
import time
from collections.abc import MutableSequence

from better_together_shared.asset_catalog import (
    DEFAULT_CREW_SELECTION_ASSET_IDS,
    get_pirate_ship_frame_asset_id,
)
from better_together_shared.config import PLAYER_SPAWN_POSITIONS


DEFAULT_SERVER_TICK_RATE_HZ = 20
MAX_SIMULATION_STEPS_PER_ADVANCE = 5


class CombinedEntityView(MutableSequence):
    """Compatibility view that exposes crew members followed by pirate ships."""

    def __init__(self, crew_members, pirate_ships):
        self.crew_members = crew_members
        self.pirate_ships = pirate_ships

    def _combined(self):
        return [*self.crew_members, *self.pirate_ships]

    def __len__(self):
        return len(self.crew_members) + len(self.pirate_ships)

    def __getitem__(self, index):
        return self._combined()[index]

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            raise TypeError("CombinedEntityView does not support slice assignment.")

        if index < 0:
            index += len(self)

        if 0 <= index < len(self.crew_members):
            self.crew_members[index] = value
            return

        pirate_index = index - len(self.crew_members)
        if 0 <= pirate_index < len(self.pirate_ships):
            self.pirate_ships[pirate_index] = value
            return

        raise IndexError(index)

    def __delitem__(self, index):
        raise TypeError("CombinedEntityView does not support item deletion.")

    def insert(self, index, value):
        raise TypeError("CombinedEntityView does not support insertion.")

    def __eq__(self, other):
        return list(self) == list(other)


def get_server_player_class():
    from .player import Player

    return Player


class Game:
    def __init__(self, game_id, tick_rate_hz=DEFAULT_SERVER_TICK_RATE_HZ):
        Player = get_server_player_class()

        self.id = game_id
        (self.playerWidth, self.playerHeight) = (36, 48)
        self.tick_rate_hz = tick_rate_hz
        self.tick_interval_seconds = 1 / tick_rate_hz
        self.last_simulation_tick_at = time.monotonic()
        self.resource_refill_interval_ticks = self.tick_rate_hz * 10
        self.enemy_attack_interval_ticks = self.tick_rate_hz * 6
        self.enemy_attack_cooldown_ticks = 0

        characters = list(DEFAULT_CREW_SELECTION_ASSET_IDS)
        random.shuffle(characters)
        self.crew_members = [
            Player(spawn_x, spawn_y, self.playerWidth, self.playerHeight, characters[index])
            for index, (spawn_x, spawn_y) in enumerate(PLAYER_SPAWN_POSITIONS)
        ]
        self.ai = [True] * len(self.crew_members)
        self.inventory_cannon_refill_ticks = [0] * len(self.crew_members)
        self.inventory_wood_refill_ticks = [0] * len(self.crew_members)
        self.damage_markers = []
        self.enemy_projectiles = []

        self.pirate_ships = [
            Player(-300, -300, 549, 549, get_pirate_ship_frame_asset_id(0)),
            Player(1050, 750, 549, 549, get_pirate_ship_frame_asset_id(0)),
        ]
        self.pirateShips = self.pirate_ships
        self.players = CombinedEntityView(self.crew_members, self.pirate_ships)

        for ship in self.pirate_ships:
            ship.maxWidth = 1050
            ship.maxHeight = 750
            ship.animation = None

    def all_entities(self):
        return list(self.players)

    def other_entities_for(self, player_number):
        return [
            *self.crew_members[:player_number],
            *self.crew_members[player_number + 1 :],
            *self.pirate_ships,
        ]

    def active_enemy_attack_targets(self):
        active_targets = [
            crew_member
            for crew_index, crew_member in enumerate(self.crew_members)
            if not self.ai[crew_index]
        ]
        return active_targets or list(self.crew_members)

    def remove_damage_markers(self, repaired_damage_markers):
        if not repaired_damage_markers:
            return

        repaired_damage_markers = {tuple(marker) for marker in repaired_damage_markers}
        self.damage_markers = [
            damage_marker
            for damage_marker in self.damage_markers
            if tuple(damage_marker) not in repaired_damage_markers
        ]

    def enemy_projectile_positions(self):
        return [
            (projectile["x"], projectile["y"])
            for projectile in self.enemy_projectiles
        ]

    def consume_pending_simulation_steps(self, now=None, max_steps=MAX_SIMULATION_STEPS_PER_ADVANCE):
        if now is None:
            now = time.monotonic()

        if now <= self.last_simulation_tick_at:
            return 0

        due_steps = int((now - self.last_simulation_tick_at) / self.tick_interval_seconds)
        if due_steps <= 0:
            return 0

        if max_steps is not None:
            due_steps = min(due_steps, max_steps)

        self.last_simulation_tick_at += due_steps * self.tick_interval_seconds
        return due_steps

    def get_player(self, player_number):
        if self.ai[player_number] is True:
            self.ai[player_number] = False
            return self.crew_members[player_number]
        return None

    def play(self, player_number, move):
        self.crew_members[player_number] = move


__all__ = [
    "CombinedEntityView",
    "DEFAULT_SERVER_TICK_RATE_HZ",
    "Game",
    "MAX_SIMULATION_STEPS_PER_ADVANCE",
]
