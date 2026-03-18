"""Server-side room model for Better Together."""
import random
import time
from collections.abc import MutableSequence

from better_together_shared.asset_catalog import (
    DEFAULT_CREW_SELECTION_ASSET_IDS,
    get_pirate_ship_frame_asset_id,
)
from better_together_shared.collision import (
    is_damage_marker_in_repair_range as is_damage_marker_in_shared_repair_range,
    is_player_in_cannon_zone as is_player_in_shared_cannon_zone,
    resolve_repair_target_for_player,
)
from better_together_shared.config import PLAYER_SPAWN_POSITIONS
from better_together_shared.protocol import ensure_player_snapshot, validate_action_state


DEFAULT_SERVER_TICK_RATE_HZ = 20
MAX_SIMULATION_STEPS_PER_ADVANCE = 5
DEFAULT_REPAIR_DURATION_SECONDS = 3
DEFAULT_CANNON_RELOAD_SECONDS = 3
DEFAULT_CANNON_SHOT_DURATION_SECONDS = 1
DEFAULT_GAME_OVER_DELAY_SECONDS = 10
GAME_OVER_DAMAGE_MARKER_THRESHOLD = 30
DEFAULT_ACTION_TARGET = (-1000, -1000)
CLIENT_CONTROLLED_SNAPSHOT_FIELDS = (
    "x",
    "y",
    "animation",
    "frame",
    "increment",
)
OPTIONAL_CLIENT_CONTROLLED_SNAPSHOT_FIELDS = (
    "direction",
)


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
        self.repair_duration_ticks = self.tick_rate_hz * DEFAULT_REPAIR_DURATION_SECONDS
        self.cannon_reload_duration_ticks = self.tick_rate_hz * DEFAULT_CANNON_RELOAD_SECONDS
        self.cannon_shot_duration_ticks = self.tick_rate_hz * DEFAULT_CANNON_SHOT_DURATION_SECONDS
        self.game_over_delay_ticks = self.tick_rate_hz * DEFAULT_GAME_OVER_DELAY_SECONDS
        self.game_over_damage_threshold = GAME_OVER_DAMAGE_MARKER_THRESHOLD
        self.game_over = False
        self.game_over_ticks_remaining = 0

        characters = list(DEFAULT_CREW_SELECTION_ASSET_IDS)
        random.shuffle(characters)
        self.crew_members = [
            Player(spawn_x, spawn_y, self.playerWidth, self.playerHeight, characters[index])
            for index, (spawn_x, spawn_y) in enumerate(PLAYER_SPAWN_POSITIONS)
        ]
        self.ai = [True] * len(self.crew_members)
        self.inventory_cannon_refill_ticks = [0] * len(self.crew_members)
        self.inventory_wood_refill_ticks = [0] * len(self.crew_members)
        self.repair_ticks_remaining = [self.repair_duration_ticks] * len(self.crew_members)
        self.requested_repair_targets = [None] * len(self.crew_members)
        self.active_repair_targets = [None] * len(self.crew_members)
        self.cannon_reload_ticks_remaining = [self.cannon_reload_duration_ticks] * len(self.crew_members)
        self.action_pressed = [False] * len(self.crew_members)
        self.pending_fire_requests = [False] * len(self.crew_members)
        self.aim_targets = [DEFAULT_ACTION_TARGET] * len(self.crew_members)
        self.active_shots = [None] * len(self.crew_members)
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

    def player_projectile_positions(self):
        return [
            (active_shot["x"], active_shot["y"])
            for active_shot in self.active_shots
            if active_shot is not None
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
            self.clear_action_state(player_number)
            return self.crew_members[player_number]
        return None

    def play(self, player_number, move):
        self.crew_members[player_number] = move

    def clear_action_state(self, player_number):
        self.action_pressed[player_number] = False
        self.pending_fire_requests[player_number] = False
        self.requested_repair_targets[player_number] = None
        self.active_repair_targets[player_number] = None
        self.aim_targets[player_number] = DEFAULT_ACTION_TARGET
        crew_member = self.crew_members[player_number]
        crew_member.cannonBallAnimationX, crew_member.cannonBallAnimationY = DEFAULT_ACTION_TARGET
        crew_member.targetX, crew_member.targetY = DEFAULT_ACTION_TARGET

    def apply_client_player_snapshot(self, player_number, player_snapshot):
        normalized_snapshot = ensure_player_snapshot(player_snapshot)
        crew_member = self.crew_members[player_number]

        for field_name in CLIENT_CONTROLLED_SNAPSHOT_FIELDS:
            setattr(crew_member, field_name, normalized_snapshot[field_name])

        for field_name in OPTIONAL_CLIENT_CONTROLLED_SNAPSHOT_FIELDS:
            if field_name in normalized_snapshot:
                setattr(crew_member, field_name, normalized_snapshot[field_name])

        if hasattr(crew_member, "update") and callable(crew_member.update):
            crew_member.update()

        return crew_member

    def update_action_state(self, player_number, action_state):
        normalized_action_state = validate_action_state(action_state)
        was_action_pressed = self.action_pressed[player_number]
        is_action_pressed = normalized_action_state["action_pressed"]

        if was_action_pressed and not is_action_pressed:
            self.pending_fire_requests[player_number] = True

        self.action_pressed[player_number] = is_action_pressed
        self.requested_repair_targets[player_number] = normalized_action_state["repair_target"]

        aim_target = normalized_action_state["aim_target"]
        if aim_target is not None:
            self.aim_targets[player_number] = self.clamp_aim_target(player_number, aim_target)

    def clamp_aim_target(self, player_number, aim_target):
        crew_member = self.crew_members[player_number]
        aim_x, aim_y = aim_target
        return (
            max(0, min(crew_member.maxWidth, aim_x)),
            max(0, min(crew_member.maxHeight, aim_y)),
        )

    def default_cannon_aim_target(self, player_number):
        crew_member = self.crew_members[player_number]
        aim_y = crew_member.y - crew_member.height
        if 760 <= crew_member.x <= 840:
            aim_x = crew_member.x + 6 * crew_member.width
        else:
            aim_x = crew_member.x - 6 * crew_member.width
        return self.clamp_aim_target(player_number, (aim_x, aim_y))

    def is_damage_marker_in_repair_range(self, player_number, damage_marker):
        crew_member = self.crew_members[player_number]
        return is_damage_marker_in_shared_repair_range(
            player_x=crew_member.x,
            player_y=crew_member.y,
            player_width=crew_member.width,
            player_height=crew_member.height,
            damage_marker=damage_marker,
        )

    def resolve_repair_target(self, player_number):
        crew_member = self.crew_members[player_number]
        return resolve_repair_target_for_player(
            self.damage_markers,
            player_x=crew_member.x,
            player_y=crew_member.y,
            player_width=crew_member.width,
            player_height=crew_member.height,
            requested_target=self.requested_repair_targets[player_number],
        )

    def is_player_in_cannon_zone(self, player_number):
        crew_member = self.crew_members[player_number]
        return is_player_in_shared_cannon_zone(
            player_x=crew_member.x,
            player_y=crew_member.y,
        )

    def create_cannon_shot(self, player_number):
        crew_member = self.crew_members[player_number]
        aim_target = self.aim_targets[player_number]
        if aim_target == DEFAULT_ACTION_TARGET:
            aim_target = self.default_cannon_aim_target(player_number)
            self.aim_targets[player_number] = aim_target

        self.active_shots[player_number] = {
            "origin_x": crew_member.x - 60,
            "origin_y": crew_member.y + 20,
            "x": crew_member.x - 60,
            "y": crew_member.y + 20,
            "target_x": aim_target[0],
            "target_y": aim_target[1],
            "ticks_elapsed": 0,
            "total_ticks": max(1, self.cannon_shot_duration_ticks),
        }

    def gameplay_state_for(self, player_number):
        return {
            "tick_rate_hz": self.tick_rate_hz,
            "game_over": self.game_over,
            "game_over_ticks_remaining": self.game_over_ticks_remaining,
            "repair_target": self.active_repair_targets[player_number],
            "repair_ticks_remaining": self.repair_ticks_remaining[player_number],
            "repair_duration_ticks": self.repair_duration_ticks,
            "cannon_reload_ticks_remaining": self.cannon_reload_ticks_remaining[player_number],
            "cannon_reload_duration_ticks": self.cannon_reload_duration_ticks,
        }


__all__ = [
    "CombinedEntityView",
    "CLIENT_CONTROLLED_SNAPSHOT_FIELDS",
    "DEFAULT_ACTION_TARGET",
    "DEFAULT_CANNON_RELOAD_SECONDS",
    "DEFAULT_CANNON_SHOT_DURATION_SECONDS",
    "DEFAULT_GAME_OVER_DELAY_SECONDS",
    "DEFAULT_REPAIR_DURATION_SECONDS",
    "DEFAULT_SERVER_TICK_RATE_HZ",
    "GAME_OVER_DAMAGE_MARKER_THRESHOLD",
    "Game",
    "MAX_SIMULATION_STEPS_PER_ADVANCE",
    "OPTIONAL_CLIENT_CONTROLLED_SNAPSHOT_FIELDS",
]
