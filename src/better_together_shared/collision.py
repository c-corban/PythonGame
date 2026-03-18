"""Shared collision and interaction geometry helpers for Better Together."""

from __future__ import annotations

from collections.abc import Iterable


CoordinatePair = tuple[int, int]


DAMAGE_MARKER_SIZE = 15
REPAIR_RANGE_PADDING_DIVISOR = 3
CANNON_ZONE_Y_MIN = 420
CANNON_ZONE_Y_MAX = 740
LEFT_CANNON_ZONE_X_MIN = 470
LEFT_CANNON_ZONE_X_MAX = 550
RIGHT_CANNON_ZONE_X_MIN = 760
RIGHT_CANNON_ZONE_X_MAX = 840


def _normalize_coordinate_pair(coordinate_pair: CoordinatePair | Iterable[int]) -> CoordinatePair:
    x, y = coordinate_pair
    return int(x), int(y)


def damage_marker_center(
    damage_marker: CoordinatePair | Iterable[int],
    *,
    marker_size: int = DAMAGE_MARKER_SIZE,
) -> CoordinatePair:
    damage_x, damage_y = _normalize_coordinate_pair(damage_marker)
    offset = marker_size // 2
    return damage_x + offset, damage_y + offset


def is_damage_marker_in_repair_range(
    *,
    player_x: int,
    player_y: int,
    player_width: int,
    player_height: int,
    damage_marker: CoordinatePair | Iterable[int],
    marker_size: int = DAMAGE_MARKER_SIZE,
) -> bool:
    """Return whether a damage marker is inside the current repair interaction range.

    The range math intentionally matches the current prototype behavior, including
    using ``player_width`` as the padding basis for both axes.
    """

    center_x, center_y = damage_marker_center(damage_marker, marker_size=marker_size)
    repair_padding = player_width // REPAIR_RANGE_PADDING_DIVISOR
    x_start = player_x - repair_padding
    x_stop = player_x + player_width + repair_padding
    y_start = player_y - repair_padding
    y_stop = player_y + player_height + repair_padding
    return x_start <= center_x < x_stop and y_start <= center_y < y_stop


def resolve_repair_target_for_player(
    damage_markers: Iterable[CoordinatePair | Iterable[int]],
    *,
    player_x: int,
    player_y: int,
    player_width: int,
    player_height: int,
    requested_target: CoordinatePair | Iterable[int] | None = None,
    marker_size: int = DAMAGE_MARKER_SIZE,
) -> CoordinatePair | None:
    """Resolve the best active repair target for a player.

    If the requested target is still present and in range, it wins. Otherwise the
    first in-range marker wins, which matches the existing client/server behavior.
    """

    normalized_damage_markers = [
        _normalize_coordinate_pair(damage_marker)
        for damage_marker in damage_markers
    ]
    normalized_requested_target = (
        None
        if requested_target is None
        else _normalize_coordinate_pair(requested_target)
    )

    if (
        normalized_requested_target is not None
        and normalized_requested_target in normalized_damage_markers
        and is_damage_marker_in_repair_range(
            player_x=player_x,
            player_y=player_y,
            player_width=player_width,
            player_height=player_height,
            damage_marker=normalized_requested_target,
            marker_size=marker_size,
        )
    ):
        return normalized_requested_target

    for damage_marker in normalized_damage_markers:
        if is_damage_marker_in_repair_range(
            player_x=player_x,
            player_y=player_y,
            player_width=player_width,
            player_height=player_height,
            damage_marker=damage_marker,
            marker_size=marker_size,
        ):
            return damage_marker

    return None


def is_player_in_cannon_zone(*, player_x: int, player_y: int) -> bool:
    """Return whether the player is within either cannon interaction zone."""

    if not CANNON_ZONE_Y_MIN <= player_y <= CANNON_ZONE_Y_MAX:
        return False

    return (
        LEFT_CANNON_ZONE_X_MIN <= player_x <= LEFT_CANNON_ZONE_X_MAX
        or RIGHT_CANNON_ZONE_X_MIN <= player_x <= RIGHT_CANNON_ZONE_X_MAX
    )


__all__ = [
    "CANNON_ZONE_Y_MAX",
    "CANNON_ZONE_Y_MIN",
    "CoordinatePair",
    "DAMAGE_MARKER_SIZE",
    "LEFT_CANNON_ZONE_X_MAX",
    "LEFT_CANNON_ZONE_X_MIN",
    "REPAIR_RANGE_PADDING_DIVISOR",
    "RIGHT_CANNON_ZONE_X_MAX",
    "RIGHT_CANNON_ZONE_X_MIN",
    "damage_marker_center",
    "is_damage_marker_in_repair_range",
    "is_player_in_cannon_zone",
    "resolve_repair_target_for_player",
]
