"""Explicit snapshot-based wire protocol for Better Together.

The snapshot field `char` now carries a logical asset reference. Runtime-managed
entities should use asset IDs from `better_together_shared.asset_catalog`
instead of raw package-relative image paths.
"""

import pickle
from numbers import Integral

from better_together_shared.asset_catalog import normalize_asset_reference


PROTOCOL_VERSION = 3

PLAYER_ASSIGNMENT_MESSAGE = "player_assignment"
PLAYER_UPDATE_MESSAGE = "player_update"
ROOM_STATE_MESSAGE = "room_state"

CREW_MEMBER_ENTITY_KIND = "crew_member"
PIRATE_SHIP_ENTITY_KIND = "pirate_ship"

ENTITY_KINDS = (
    CREW_MEMBER_ENTITY_KIND,
    PIRATE_SHIP_ENTITY_KIND,
)

PLAYER_SNAPSHOT_FIELDS = (
    "x",
    "y",
    "width",
    "height",
    "char",
    "animation",
    "frame",
    "velocity",
    "increment",
    "maxHeight",
    "maxWidth",
    "inventoryWood",
    "inventoryCannon",
    "cannonBallAnimationX",
    "cannonBallAnimationY",
    "targetX",
    "targetY",
)

OPTIONAL_PLAYER_SNAPSHOT_FIELDS = (
    "direction",
)

PLAYER_SNAPSHOT_INTEGER_FIELDS = (
    "x",
    "y",
    "width",
    "height",
    "frame",
    "velocity",
    "increment",
    "maxHeight",
    "maxWidth",
    "inventoryWood",
    "inventoryCannon",
    "cannonBallAnimationX",
    "cannonBallAnimationY",
    "targetX",
    "targetY",
)

DEFAULT_DAMAGE_MARKERS = ()
DEFAULT_PLAYER_PROJECTILES = ()
DEFAULT_ACTION_STATE = {
    "action_pressed": False,
    "repair_target": None,
    "aim_target": None,
}
DEFAULT_GAMEPLAY_STATE = {
    "tick_rate_hz": 1,
    "game_over": False,
    "game_over_ticks_remaining": 0,
    "repair_target": None,
    "repair_ticks_remaining": 0,
    "repair_duration_ticks": 0,
    "cannon_reload_ticks_remaining": 0,
    "cannon_reload_duration_ticks": 0,
}


class ProtocolValidationError(ValueError):
    """Raised when a message or snapshot does not match the expected protocol shape."""


class InvalidPlayerSnapshotError(ProtocolValidationError):
    """Raised when a player snapshot is missing required fields or contains invalid values."""


class InvalidProtocolMessageError(ProtocolValidationError):
    """Raised when a protocol message is malformed for its declared message type."""


def serialize_message(message):
    return pickle.dumps(message)


def deserialize_message(payload):
    return pickle.loads(payload)


def _is_integral_value(value):
    return isinstance(value, Integral) and not isinstance(value, bool)


def _validate_integral(value, field_name, error_cls):
    if not _is_integral_value(value):
        raise error_cls(f"Field `{field_name}` must be an integer, got {type(value).__name__}.")

    return value


def _validate_boolean(value, field_name, error_cls):
    if not isinstance(value, bool):
        raise error_cls(f"Field `{field_name}` must be a boolean, got {type(value).__name__}.")

    return value


def _validate_animation(animation):
    if animation is None:
        return None

    if not isinstance(animation, (list, tuple)) or len(animation) != 4:
        raise InvalidPlayerSnapshotError(
            "Field `animation` must be None or a 4-item list/tuple of integers."
        )

    for index, component in enumerate(animation):
        _validate_integral(component, f"animation[{index}]", InvalidPlayerSnapshotError)

    return animation


def _validate_coordinate_pairs(coordinate_pairs, field_name, error_cls):
    if coordinate_pairs in (None, DEFAULT_DAMAGE_MARKERS):
        return []

    if not isinstance(coordinate_pairs, list):
        raise error_cls(
            f"Field `{field_name}` must be a list of 2-item integer coordinate pairs."
        )

    normalized_coordinate_pairs = []
    for coordinate_index, coordinate_pair in enumerate(coordinate_pairs):
        if not isinstance(coordinate_pair, (list, tuple)) or len(coordinate_pair) != 2:
            raise error_cls(
                f"Field `{field_name}[{coordinate_index}]` must be a 2-item list/tuple of integers."
            )

        normalized_coordinate_pairs.append(
            (
                _validate_integral(coordinate_pair[0], f"{field_name}[{coordinate_index}][0]", error_cls),
                _validate_integral(coordinate_pair[1], f"{field_name}[{coordinate_index}][1]", error_cls),
            )
        )

    return normalized_coordinate_pairs


def _validate_optional_coordinate_pair(coordinate_pair, field_name, error_cls):
    if coordinate_pair is None:
        return None

    if not isinstance(coordinate_pair, (list, tuple)) or len(coordinate_pair) != 2:
        raise error_cls(
            f"Field `{field_name}` must be None or a 2-item list/tuple of integers."
        )

    return (
        _validate_integral(coordinate_pair[0], f"{field_name}[0]", error_cls),
        _validate_integral(coordinate_pair[1], f"{field_name}[1]", error_cls),
    )


def _validate_damage_markers(damage_markers, field_name, error_cls):
    return _validate_coordinate_pairs(damage_markers, field_name, error_cls)


def validate_action_state(action_state):
    if action_state is None:
        return dict(DEFAULT_ACTION_STATE)

    if not isinstance(action_state, dict):
        raise InvalidProtocolMessageError(
            f"Field `action_state` must be a dictionary, got {type(action_state).__name__}."
        )

    normalized_action_state = dict(DEFAULT_ACTION_STATE)
    normalized_action_state.update(action_state)
    normalized_action_state["action_pressed"] = _validate_boolean(
        normalized_action_state["action_pressed"],
        "action_state.action_pressed",
        InvalidProtocolMessageError,
    )
    normalized_action_state["repair_target"] = _validate_optional_coordinate_pair(
        normalized_action_state.get("repair_target"),
        "action_state.repair_target",
        InvalidProtocolMessageError,
    )
    normalized_action_state["aim_target"] = _validate_optional_coordinate_pair(
        normalized_action_state.get("aim_target"),
        "action_state.aim_target",
        InvalidProtocolMessageError,
    )
    return normalized_action_state


def validate_gameplay_state(gameplay_state):
    if gameplay_state is None:
        return dict(DEFAULT_GAMEPLAY_STATE)

    if not isinstance(gameplay_state, dict):
        raise InvalidProtocolMessageError(
            f"Field `gameplay_state` must be a dictionary, got {type(gameplay_state).__name__}."
        )

    normalized_gameplay_state = dict(DEFAULT_GAMEPLAY_STATE)
    normalized_gameplay_state.update(gameplay_state)

    normalized_gameplay_state["tick_rate_hz"] = _validate_integral(
        normalized_gameplay_state["tick_rate_hz"],
        "gameplay_state.tick_rate_hz",
        InvalidProtocolMessageError,
    )
    if normalized_gameplay_state["tick_rate_hz"] <= 0:
        raise InvalidProtocolMessageError("Field `gameplay_state.tick_rate_hz` must be greater than 0.")
    normalized_gameplay_state["game_over"] = _validate_boolean(
        normalized_gameplay_state["game_over"],
        "gameplay_state.game_over",
        InvalidProtocolMessageError,
    )

    for field_name in (
        "game_over_ticks_remaining",
        "repair_ticks_remaining",
        "repair_duration_ticks",
        "cannon_reload_ticks_remaining",
        "cannon_reload_duration_ticks",
    ):
        normalized_gameplay_state[field_name] = _validate_integral(
            normalized_gameplay_state[field_name],
            f"gameplay_state.{field_name}",
            InvalidProtocolMessageError,
        )
        if normalized_gameplay_state[field_name] < 0:
            raise InvalidProtocolMessageError(
                f"Field `gameplay_state.{field_name}` must be greater than or equal to 0."
            )

    normalized_gameplay_state["repair_target"] = _validate_optional_coordinate_pair(
        normalized_gameplay_state.get("repair_target"),
        "gameplay_state.repair_target",
        InvalidProtocolMessageError,
    )
    return normalized_gameplay_state


def infer_entity_kind(snapshot):
    if snapshot.get("animation") is None:
        return PIRATE_SHIP_ENTITY_KIND

    return CREW_MEMBER_ENTITY_KIND


def validate_player_snapshot(snapshot):
    if not isinstance(snapshot, dict):
        raise InvalidPlayerSnapshotError(
            f"Player snapshots must be dictionaries, got {type(snapshot).__name__}."
        )

    normalized_snapshot = dict(snapshot)

    missing_fields = [field for field in PLAYER_SNAPSHOT_FIELDS if field not in normalized_snapshot]
    if missing_fields:
        raise InvalidPlayerSnapshotError(
            f"Player snapshot is missing required fields: {', '.join(missing_fields)}."
        )

    for field in PLAYER_SNAPSHOT_INTEGER_FIELDS:
        _validate_integral(normalized_snapshot[field], field, InvalidPlayerSnapshotError)

    if not isinstance(normalized_snapshot["char"], str):
        raise InvalidPlayerSnapshotError(
            f"Field `char` must be a string, got {type(normalized_snapshot['char']).__name__}."
        )

    normalized_snapshot["char"] = normalize_asset_reference(normalized_snapshot["char"])

    normalized_snapshot["animation"] = _validate_animation(normalized_snapshot["animation"])

    for field in OPTIONAL_PLAYER_SNAPSHOT_FIELDS:
        if field in normalized_snapshot:
            _validate_integral(normalized_snapshot[field], field, InvalidPlayerSnapshotError)

    inferred_entity_kind = infer_entity_kind(normalized_snapshot)
    entity_kind = normalized_snapshot.get("entity_kind", inferred_entity_kind)
    if entity_kind not in ENTITY_KINDS:
        raise InvalidPlayerSnapshotError(
            f"Field `entity_kind` must be one of {ENTITY_KINDS}, got {entity_kind!r}."
        )
    if entity_kind != inferred_entity_kind:
        raise InvalidPlayerSnapshotError(
            f"Field `entity_kind` ({entity_kind!r}) does not match inferred kind {inferred_entity_kind!r}."
        )

    normalized_snapshot["entity_kind"] = entity_kind
    return normalized_snapshot


def validate_message(message, expected_message_type=None):
    if not isinstance(message, dict):
        raise InvalidProtocolMessageError(
            f"Protocol messages must be dictionaries, got {type(message).__name__}."
        )

    normalized_message = dict(message)
    if normalized_message.get("protocol_version") != PROTOCOL_VERSION:
        raise InvalidProtocolMessageError(
            f"Unsupported protocol version {normalized_message.get('protocol_version')!r}."
        )

    message_type = normalized_message.get("message_type")
    if expected_message_type is not None and message_type != expected_message_type:
        raise InvalidProtocolMessageError(
            f"Expected message type {expected_message_type!r}, got {message_type!r}."
        )

    if message_type == PLAYER_ASSIGNMENT_MESSAGE:
        _validate_integral(normalized_message.get("room_id"), "room_id", InvalidProtocolMessageError)
        _validate_integral(normalized_message.get("player_number"), "player_number", InvalidProtocolMessageError)
        normalized_message["player"] = validate_player_snapshot(normalized_message.get("player"))
        normalized_message["gameplay_state"] = validate_gameplay_state(
            normalized_message.get("gameplay_state")
        )
        return normalized_message

    if message_type == PLAYER_UPDATE_MESSAGE:
        normalized_message["player"] = validate_player_snapshot(normalized_message.get("player"))
        normalized_message["repaired_damage_markers"] = _validate_damage_markers(
            normalized_message.get("repaired_damage_markers", []),
            "repaired_damage_markers",
            InvalidProtocolMessageError,
        )
        if "action_state" not in normalized_message:
            raise InvalidProtocolMessageError(
                "Field `action_state` is required for player_update messages."
            )
        normalized_message["action_state"] = validate_action_state(
            normalized_message.get("action_state")
        )
        return normalized_message

    if message_type == ROOM_STATE_MESSAGE:
        _validate_integral(normalized_message.get("room_id"), "room_id", InvalidProtocolMessageError)
        entities = normalized_message.get("entities")
        if not isinstance(entities, list):
            raise InvalidProtocolMessageError(
                f"Field `entities` must be a list, got {type(entities).__name__}."
            )
        normalized_message["entities"] = [validate_player_snapshot(entity) for entity in entities]
        self_player_snapshot = normalized_message.get("self_player")
        normalized_message["self_player"] = (
            None if self_player_snapshot is None else validate_player_snapshot(self_player_snapshot)
        )
        normalized_message["damage_markers"] = _validate_damage_markers(
            normalized_message.get("damage_markers", []),
            "damage_markers",
            InvalidProtocolMessageError,
        )
        normalized_message["enemy_projectiles"] = _validate_coordinate_pairs(
            normalized_message.get("enemy_projectiles", []),
            "enemy_projectiles",
            InvalidProtocolMessageError,
        )
        normalized_message["player_projectiles"] = _validate_coordinate_pairs(
            normalized_message.get("player_projectiles", []),
            "player_projectiles",
            InvalidProtocolMessageError,
        )
        normalized_message["gameplay_state"] = validate_gameplay_state(
            normalized_message.get("gameplay_state")
        )
        return normalized_message

    raise InvalidProtocolMessageError(f"Unsupported message type {message_type!r}.")


def ensure_player_snapshot(player_or_snapshot):
    if isinstance(player_or_snapshot, dict):
        return validate_player_snapshot(player_or_snapshot)

    return create_player_snapshot(player_or_snapshot)


def create_player_snapshot(player):
    snapshot = {field: getattr(player, field) for field in PLAYER_SNAPSHOT_FIELDS}

    for field in OPTIONAL_PLAYER_SNAPSHOT_FIELDS:
        if hasattr(player, field):
            snapshot[field] = getattr(player, field)

    snapshot["entity_kind"] = infer_entity_kind(snapshot)
    return validate_player_snapshot(snapshot)


def apply_player_snapshot(player, snapshot):
    normalized_snapshot = ensure_player_snapshot(snapshot)

    for field in PLAYER_SNAPSHOT_FIELDS:
        setattr(player, field, normalized_snapshot[field])

    for field in OPTIONAL_PLAYER_SNAPSHOT_FIELDS:
        if field in normalized_snapshot:
            setattr(player, field, normalized_snapshot[field])

    if hasattr(player, "update") and callable(player.update):
        player.update()

    return player


def create_player_from_snapshot(player_factory, snapshot):
    normalized_snapshot = ensure_player_snapshot(snapshot)
    player = player_factory(
        normalized_snapshot["x"],
        normalized_snapshot["y"],
        normalized_snapshot["width"],
        normalized_snapshot["height"],
        normalized_snapshot["char"],
    )
    return apply_player_snapshot(player, normalized_snapshot)


def create_message(message_type, **payload):
    return {
        "protocol_version": PROTOCOL_VERSION,
        "message_type": message_type,
        **payload,
    }


def is_message_type(message, expected_message_type):
    return (
        isinstance(message, dict)
        and message.get("protocol_version") == PROTOCOL_VERSION
        and message.get("message_type") == expected_message_type
    )


def create_assignment_message(player_number, room_id, player_or_snapshot, gameplay_state=None):
    return validate_message(
        create_message(
            PLAYER_ASSIGNMENT_MESSAGE,
            room_id=room_id,
            player_number=player_number,
            player=ensure_player_snapshot(player_or_snapshot),
            gameplay_state=validate_gameplay_state(gameplay_state),
        ),
        PLAYER_ASSIGNMENT_MESSAGE,
    )


def create_update_message(player_or_snapshot, repaired_damage_markers=None, action_state=None):
    return validate_message(
        create_message(
            PLAYER_UPDATE_MESSAGE,
            player=ensure_player_snapshot(player_or_snapshot),
            repaired_damage_markers=_validate_damage_markers(
                repaired_damage_markers,
                "repaired_damage_markers",
                InvalidProtocolMessageError,
            ),
            action_state=validate_action_state(action_state),
        ),
        PLAYER_UPDATE_MESSAGE,
    )


def create_room_state_message(room_id, entities, self_player=None, damage_markers=None, enemy_projectiles=None, player_projectiles=None, gameplay_state=None):
    return validate_message(
        create_message(
            ROOM_STATE_MESSAGE,
            room_id=room_id,
            entities=[ensure_player_snapshot(entity) for entity in entities],
            self_player=None if self_player is None else ensure_player_snapshot(self_player),
            damage_markers=_validate_damage_markers(
                damage_markers,
                "damage_markers",
                InvalidProtocolMessageError,
            ),
            enemy_projectiles=_validate_coordinate_pairs(
                enemy_projectiles,
                "enemy_projectiles",
                InvalidProtocolMessageError,
            ),
            player_projectiles=_validate_coordinate_pairs(
                player_projectiles,
                "player_projectiles",
                InvalidProtocolMessageError,
            ),
            gameplay_state=validate_gameplay_state(gameplay_state),
        ),
        ROOM_STATE_MESSAGE,
    )


def extract_assigned_player(message):
    try:
        return validate_message(message, PLAYER_ASSIGNMENT_MESSAGE)["player"]
    except ProtocolValidationError:
        return None


def extract_assignment_gameplay_state(message):
    try:
        return validate_message(message, PLAYER_ASSIGNMENT_MESSAGE)["gameplay_state"]
    except ProtocolValidationError:
        return dict(DEFAULT_GAMEPLAY_STATE)


def extract_player_update(message):
    try:
        return validate_message(message, PLAYER_UPDATE_MESSAGE)["player"]
    except ProtocolValidationError:
        return None


def extract_repaired_damage_markers(message):
    try:
        return validate_message(message, PLAYER_UPDATE_MESSAGE)["repaired_damage_markers"]
    except ProtocolValidationError:
        return []


def extract_action_state(message):
    try:
        return validate_message(message, PLAYER_UPDATE_MESSAGE)["action_state"]
    except ProtocolValidationError:
        return dict(DEFAULT_ACTION_STATE)


def extract_room_state_self_player(message):
    try:
        return validate_message(message, ROOM_STATE_MESSAGE)["self_player"]
    except ProtocolValidationError:
        return None


def extract_room_state_damage_markers(message):
    try:
        return validate_message(message, ROOM_STATE_MESSAGE)["damage_markers"]
    except ProtocolValidationError:
        return []


def extract_room_state_enemy_projectiles(message):
    try:
        return validate_message(message, ROOM_STATE_MESSAGE)["enemy_projectiles"]
    except ProtocolValidationError:
        return []


def extract_room_state_player_projectiles(message):
    try:
        return validate_message(message, ROOM_STATE_MESSAGE)["player_projectiles"]
    except ProtocolValidationError:
        return list(DEFAULT_PLAYER_PROJECTILES)


def extract_room_state_gameplay_state(message):
    try:
        return validate_message(message, ROOM_STATE_MESSAGE)["gameplay_state"]
    except ProtocolValidationError:
        return dict(DEFAULT_GAMEPLAY_STATE)


def create_players_from_room_state(player_factory, message):
    try:
        validated_message = validate_message(message, ROOM_STATE_MESSAGE)
    except ProtocolValidationError:
        return []

    return [
        create_player_from_snapshot(player_factory, entity_snapshot)
        for entity_snapshot in validated_message["entities"]
    ]


__all__ = [
    "CREW_MEMBER_ENTITY_KIND",
    "DEFAULT_ACTION_STATE",
    "DEFAULT_GAMEPLAY_STATE",
    "DEFAULT_PLAYER_PROJECTILES",
    "ENTITY_KINDS",
    "InvalidPlayerSnapshotError",
    "InvalidProtocolMessageError",
    "OPTIONAL_PLAYER_SNAPSHOT_FIELDS",
    "PLAYER_ASSIGNMENT_MESSAGE",
    "PLAYER_SNAPSHOT_FIELDS",
    "PLAYER_SNAPSHOT_INTEGER_FIELDS",
    "PLAYER_UPDATE_MESSAGE",
    "PIRATE_SHIP_ENTITY_KIND",
    "PROTOCOL_VERSION",
    "ProtocolValidationError",
    "ROOM_STATE_MESSAGE",
    "apply_player_snapshot",
    "create_assignment_message",
    "create_message",
    "create_player_from_snapshot",
    "create_player_snapshot",
    "create_players_from_room_state",
    "create_room_state_message",
    "create_update_message",
    "deserialize_message",
    "ensure_player_snapshot",
    "extract_action_state",
    "extract_assigned_player",
    "extract_assignment_gameplay_state",
    "extract_player_update",
    "extract_repaired_damage_markers",
    "extract_room_state_damage_markers",
    "extract_room_state_enemy_projectiles",
    "extract_room_state_gameplay_state",
    "extract_room_state_player_projectiles",
    "extract_room_state_self_player",
    "infer_entity_kind",
    "is_message_type",
    "serialize_message",
    "validate_action_state",
    "validate_gameplay_state",
    "validate_message",
    "validate_player_snapshot",
]
