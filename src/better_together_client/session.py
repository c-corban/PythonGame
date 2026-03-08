"""Client gameplay session state helpers."""

from dataclasses import dataclass, field


@dataclass
class FramePromptState:
    shoot_info_displayed: bool = False
    repair_info_displayed: bool = False


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

    def begin_frame(self):
        return FramePromptState()

    def queue_repaired_damage_marker(self, damage_marker):
        self.pending_repaired_damage_markers.append(tuple(damage_marker))

    def consume_repaired_damage_markers(self):
        repaired_damage_markers = list(self.pending_repaired_damage_markers)
        self.pending_repaired_damage_markers.clear()
        return repaired_damage_markers


__all__ = ["FramePromptState", "GameplaySessionState"]
