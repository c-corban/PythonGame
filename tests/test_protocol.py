import sys
import unittest
from types import SimpleNamespace

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()

from better_together_shared.asset_catalog import (
    CREW_CAPTAIN_M_001_LIGHT_ASSET_ID,
    get_pirate_ship_frame_asset_id,
)
from better_together_shared.protocol import (
    CREW_MEMBER_ENTITY_KIND,
    InvalidPlayerSnapshotError,
    PIRATE_SHIP_ENTITY_KIND,
    PLAYER_ASSIGNMENT_MESSAGE,
    PLAYER_UPDATE_MESSAGE,
    ROOM_STATE_MESSAGE,
    PROTOCOL_VERSION,
    create_assignment_message,
    create_player_from_snapshot,
    create_player_snapshot,
    create_players_from_room_state,
    create_room_state_message,
    create_update_message,
    deserialize_message,
    extract_assigned_player,
    extract_player_update,
    extract_repaired_damage_markers,
    extract_room_state_damage_markers,
    extract_room_state_enemy_projectiles,
    extract_room_state_self_player,
    is_message_type,
    serialize_message,
    validate_message,
)


class DummyPlayer:
    def __init__(self, x, y, width, height, char):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.char = char
        self.updated = 0

    def update(self):
        self.updated += 1


def make_player_like(**overrides):
    values = {
        "x": 100,
        "y": 200,
        "width": 36,
        "height": 48,
        "char": CREW_CAPTAIN_M_001_LIGHT_ASSET_ID,
        "animation": (36, 96, 36, 48),
        "frame": 17,
        "velocity": 2,
        "increment": 3,
        "maxHeight": 960,
        "maxWidth": 1280,
        "inventoryWood": 8,
        "inventoryCannon": 7,
        "cannonBallAnimationX": -1000,
        "cannonBallAnimationY": -1000,
        "targetX": 500,
        "targetY": 600,
        "direction": 4,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


class ProtocolHelperTests(unittest.TestCase):
    def test_player_snapshot_marks_crew_and_pirate_entities(self):
        crew_snapshot = create_player_snapshot(make_player_like())
        pirate_snapshot = create_player_snapshot(
            make_player_like(
                animation=None,
                width=549,
                height=549,
                char=get_pirate_ship_frame_asset_id(0),
            )
        )

        self.assertEqual(crew_snapshot["entity_kind"], CREW_MEMBER_ENTITY_KIND)
        self.assertEqual(pirate_snapshot["entity_kind"], PIRATE_SHIP_ENTITY_KIND)

    def test_create_player_from_snapshot_applies_full_state(self):
        snapshot = create_player_snapshot(make_player_like(x=123, y=456, direction=2, inventoryWood=3))

        player = create_player_from_snapshot(DummyPlayer, snapshot)

        self.assertEqual((player.x, player.y), (123, 456))
        self.assertEqual((player.width, player.height), (36, 48))
        self.assertEqual(player.inventoryWood, 3)
        self.assertEqual(player.direction, 2)
        self.assertEqual(player.updated, 1)

    def test_protocol_messages_round_trip_through_pickle(self):
        snapshot = create_player_snapshot(make_player_like())

        assignment_message = deserialize_message(serialize_message(create_assignment_message(1, 7, snapshot)))
        update_message = deserialize_message(serialize_message(create_update_message(snapshot, repaired_damage_markers=[(12, 34)])))
        room_state_message = deserialize_message(
            serialize_message(
                create_room_state_message(
                    7,
                    [snapshot],
                    self_player=snapshot,
                    damage_markers=[(12, 34), (56, 78)],
                    enemy_projectiles=[(90, 91)],
                )
            )
        )

        self.assertTrue(is_message_type(assignment_message, PLAYER_ASSIGNMENT_MESSAGE))
        self.assertEqual(assignment_message["player_number"], 1)
        self.assertEqual(assignment_message["room_id"], 7)
        self.assertEqual(extract_assigned_player(assignment_message)["char"], snapshot["char"])

        self.assertTrue(is_message_type(update_message, PLAYER_UPDATE_MESSAGE))
        self.assertEqual(extract_player_update(update_message)["targetY"], snapshot["targetY"])
        self.assertEqual(extract_repaired_damage_markers(update_message), [(12, 34)])

        self.assertTrue(is_message_type(room_state_message, ROOM_STATE_MESSAGE))
        self.assertEqual(extract_room_state_self_player(room_state_message)["char"], snapshot["char"])
        self.assertEqual(extract_room_state_damage_markers(room_state_message), [(12, 34), (56, 78)])
        self.assertEqual(extract_room_state_enemy_projectiles(room_state_message), [(90, 91)])
        rebuilt_players = create_players_from_room_state(DummyPlayer, room_state_message)
        self.assertEqual(len(rebuilt_players), 1)
        self.assertEqual(rebuilt_players[0].char, snapshot["char"])
        self.assertEqual(rebuilt_players[0].updated, 1)

    def test_create_update_message_rejects_missing_snapshot_fields(self):
        with self.assertRaises(InvalidPlayerSnapshotError):
            create_update_message({"x": 10, "y": 20})

    def test_extract_assigned_player_rejects_invalid_assignment_metadata(self):
        snapshot = create_player_snapshot(make_player_like())
        message = {
            "protocol_version": PROTOCOL_VERSION,
            "message_type": PLAYER_ASSIGNMENT_MESSAGE,
            "room_id": "room-zero",
            "player_number": 0,
            "player": snapshot,
        }

        self.assertIsNone(extract_assigned_player(message))

    def test_extract_player_update_rejects_invalid_snapshot_shape(self):
        malformed_snapshot = create_player_snapshot(make_player_like())
        malformed_snapshot["animation"] = [1, 2, 3]
        message = {
            "protocol_version": PROTOCOL_VERSION,
            "message_type": PLAYER_UPDATE_MESSAGE,
            "player": malformed_snapshot,
        }

        self.assertIsNone(extract_player_update(message))

    def test_create_players_from_room_state_rejects_invalid_entity_snapshot(self):
        malformed_snapshot = create_player_snapshot(make_player_like())
        malformed_snapshot["entity_kind"] = PIRATE_SHIP_ENTITY_KIND
        message = {
            "protocol_version": PROTOCOL_VERSION,
            "message_type": ROOM_STATE_MESSAGE,
            "room_id": 7,
            "entities": [malformed_snapshot],
        }

        self.assertEqual(create_players_from_room_state(DummyPlayer, message), [])

    def test_validate_message_returns_normalized_valid_assignment(self):
        snapshot = create_player_snapshot(make_player_like())
        validated_message = validate_message(create_assignment_message(1, 7, snapshot))

        self.assertEqual(validated_message["room_id"], 7)
        self.assertEqual(validated_message["player_number"], 1)
        self.assertEqual(validated_message["player"]["entity_kind"], CREW_MEMBER_ENTITY_KIND)

    def test_validate_message_normalizes_room_state_damage_markers(self):
        snapshot = create_player_snapshot(make_player_like())
        validated_message = validate_message(
            create_room_state_message(
                7,
                [snapshot],
                self_player=snapshot,
                damage_markers=[[10, 20]],
                enemy_projectiles=[[30, 40]],
            )
        )

        self.assertEqual(validated_message["damage_markers"], [(10, 20)])
        self.assertEqual(validated_message["enemy_projectiles"], [(30, 40)])
        self.assertEqual(validated_message["self_player"]["char"], snapshot["char"])

    def test_shoot_animation_positions_remain_serializable_for_updates(self):
        from better_together_client.game_loop import update_shoot_animation
        from better_together_client.session import GameplaySessionState

        player = make_player_like(
            x=520,
            y=640,
            targetX=-1000,
            targetY=-1000,
        )
        session_state = GameplaySessionState(
            aim_x=333,
            aim_y=187,
            cannon_shoot=0,
            shoot_animation=True,
        )

        update_shoot_animation(session_state, player)
        update_message = create_update_message(player)

        self.assertEqual(session_state.cannon_shoot, 1)
        self.assertIsInstance(player.cannonBallAnimationX, int)
        self.assertIsInstance(player.cannonBallAnimationY, int)
        self.assertEqual(update_message["player"]["cannonBallAnimationX"], player.cannonBallAnimationX)
        self.assertEqual(update_message["player"]["cannonBallAnimationY"], player.cannonBallAnimationY)
