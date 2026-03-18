"""Client gameplay session state helpers."""

from dataclasses import dataclass, field


DEFAULT_MOVEMENT_HINT_POST_MOVE_TICKS = 60 * 3


@dataclass
class FramePromptState:
    shoot_info_displayed: bool = False
    repair_info_displayed: bool = False


@dataclass
class AuthoritativeGameplayState:
    tick_rate_hz: int = 1
    game_over: bool = False
    game_over_ticks_remaining: int = 0
    repair_target: tuple[int, int] | None = None
    repair_ticks_remaining: int = 0
    repair_duration_ticks: int = 0
    cannon_reload_ticks_remaining: int = 0
    cannon_reload_duration_ticks: int = 0

    def apply(self, gameplay_state):
        gameplay_state = gameplay_state or {}
        self.tick_rate_hz = int(gameplay_state.get("tick_rate_hz", self.tick_rate_hz or 1)) or 1
        self.game_over = bool(gameplay_state.get("game_over", self.game_over))
        self.game_over_ticks_remaining = int(
            gameplay_state.get("game_over_ticks_remaining", self.game_over_ticks_remaining)
        )
        repair_target = gameplay_state.get("repair_target", self.repair_target)
        self.repair_target = None if repair_target is None else tuple(repair_target)
        self.repair_ticks_remaining = int(
            gameplay_state.get("repair_ticks_remaining", self.repair_ticks_remaining)
        )
        self.repair_duration_ticks = int(
            gameplay_state.get("repair_duration_ticks", self.repair_duration_ticks)
        )
        self.cannon_reload_ticks_remaining = int(
            gameplay_state.get(
                "cannon_reload_ticks_remaining",
                self.cannon_reload_ticks_remaining,
            )
        )
        self.cannon_reload_duration_ticks = int(
            gameplay_state.get(
                "cannon_reload_duration_ticks",
                self.cannon_reload_duration_ticks,
            )
        )

    def seconds_remaining(self, ticks_remaining):
        return ticks_remaining / max(1, self.tick_rate_hz)


@dataclass
class GameplaySessionState:
    info_count: int = 0
    game_over_count: int = 0
    aim_x: int = 300
    aim_y: int = 320
    aim_velocity: int = 4
    cannon_shoot: int = 60 * 2 + 1
    cannon_cooldown: int = 60 * 3
    repair_cooldown: int = 60 * 3
    shoot_animation: bool = False
    game_over: bool = False
    pending_repaired_damage_markers: list[tuple[int, int]] = field(default_factory=list)
    authoritative_state: AuthoritativeGameplayState = field(default_factory=AuthoritativeGameplayState)
    movement_hint_has_seen_local_movement: bool = False
    movement_hint_ticks_remaining: int = 0

    def begin_frame(self):
        if self.movement_hint_has_seen_local_movement and self.movement_hint_ticks_remaining > 0:
            self.movement_hint_ticks_remaining -= 1
        return FramePromptState()

    def apply_authoritative_state(self, gameplay_state):
        self.authoritative_state.apply(gameplay_state)
        self.game_over = self.authoritative_state.game_over

    def create_action_state(self, action_pressed=False, repair_target=None, aim_target=None):
        return {
            "action_pressed": bool(action_pressed),
            "repair_target": None if repair_target is None else tuple(repair_target),
            "aim_target": None if aim_target is None else tuple(aim_target),
        }

    def register_local_movement(self, post_move_ticks=DEFAULT_MOVEMENT_HINT_POST_MOVE_TICKS):
        if self.movement_hint_has_seen_local_movement:
            return

        self.movement_hint_has_seen_local_movement = True
        self.movement_hint_ticks_remaining = post_move_ticks

    def should_show_movement_hint(self):
        return (
            not self.movement_hint_has_seen_local_movement
            or self.movement_hint_ticks_remaining > 0
        )

    def queue_repaired_damage_marker(self, damage_marker):
        self.pending_repaired_damage_markers.append(tuple(damage_marker))

    def consume_repaired_damage_markers(self):
        repaired_damage_markers = list(self.pending_repaired_damage_markers)
        self.pending_repaired_damage_markers.clear()
        return repaired_damage_markers


__all__ = [
    "AuthoritativeGameplayState",
    "DEFAULT_MOVEMENT_HINT_POST_MOVE_TICKS",
    "FramePromptState",
    "GameplaySessionState",
]
