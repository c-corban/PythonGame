"""Explicit snapshot-based wire protocol for Better Together.

The snapshot field `char` now carries a logical asset reference. Runtime-managed
entities should use asset IDs from `better_together_shared.asset_catalog`
instead of raw package-relative image paths.
"""

import pickle
from numbers import Integral

from better_together_shared.asset_catalog import normalize_asset_reference


PROTOCOL_VERSION = 2

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


def _validate_damage_markers(damage_markers, field_name, error_cls):
    return _validate_coordinate_pairs(damage_markers, field_name, error_cls)


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
        return normalized_message

    if message_type == PLAYER_UPDATE_MESSAGE:
        normalized_message["player"] = validate_player_snapshot(normalized_message.get("player"))
        normalized_message["repaired_damage_markers"] = _validate_damage_markers(
            normalized_message.get("repaired_damage_markers", []),
            "repaired_damage_markers",
            InvalidProtocolMessageError,
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


def create_assignment_message(player_number, room_id, player_or_snapshot):
    return validate_message(
        create_message(
            PLAYER_ASSIGNMENT_MESSAGE,
            room_id=room_id,
            player_number=player_number,
            player=ensure_player_snapshot(player_or_snapshot),
        ),
        PLAYER_ASSIGNMENT_MESSAGE,
    )


def create_update_message(player_or_snapshot, repaired_damage_markers=None):
    return validate_message(
        create_message(
            PLAYER_UPDATE_MESSAGE,
            player=ensure_player_snapshot(player_or_snapshot),
            repaired_damage_markers=_validate_damage_markers(
                repaired_damage_markers,
                "repaired_damage_markers",
                InvalidProtocolMessageError,
            ),
        ),
        PLAYER_UPDATE_MESSAGE,
    )


def create_room_state_message(room_id, entities, self_player=None, damage_markers=None, enemy_projectiles=None):
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
        ),
        ROOM_STATE_MESSAGE,
    )


def extract_assigned_player(message):
    try:
        return validate_message(message, PLAYER_ASSIGNMENT_MESSAGE)["player"]
    except ProtocolValidationError:
        return None


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
    "extract_assigned_player",
    "extract_player_update",
    "extract_repaired_damage_markers",
    "extract_room_state_damage_markers",
    "extract_room_state_enemy_projectiles",
    "extract_room_state_self_player",
    "infer_entity_kind",
    "is_message_type",
    "serialize_message",
    "validate_message",
    "validate_player_snapshot",
]
