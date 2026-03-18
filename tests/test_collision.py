import unittest

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()


from better_together_shared.collision import (
    DAMAGE_MARKER_SIZE,
    is_damage_marker_in_repair_range,
    is_player_in_cannon_zone,
    resolve_repair_target_for_player,
)


def _damage_marker_from_center(center_x, center_y):
    offset = DAMAGE_MARKER_SIZE // 2
    return (center_x - offset, center_y - offset)


class SharedCollisionHelperTests(unittest.TestCase):
    def test_is_damage_marker_in_repair_range_preserves_existing_boundaries(self):
        player = {
            "player_x": 100,
            "player_y": 200,
            "player_width": 36,
            "player_height": 48,
        }
        cases = (
            ("left just outside", _damage_marker_from_center(87, 220), False),
            ("left inclusive", _damage_marker_from_center(88, 220), True),
            ("right inclusive", _damage_marker_from_center(147, 220), True),
            ("right just outside", _damage_marker_from_center(148, 220), False),
            ("top just outside", _damage_marker_from_center(100, 187), False),
            ("top inclusive", _damage_marker_from_center(100, 188), True),
            ("bottom inclusive", _damage_marker_from_center(100, 259), True),
            ("bottom just outside", _damage_marker_from_center(100, 260), False),
        )

        for label, damage_marker, expected in cases:
            with self.subTest(case=label):
                self.assertEqual(
                    is_damage_marker_in_repair_range(
                        **player,
                        damage_marker=damage_marker,
                    ),
                    expected,
                )

    def test_resolve_repair_target_prefers_requested_marker_and_normalizes_lists(self):
        damage_markers = [
            [100, 210],
            [120, 220],
        ]

        resolved_target = resolve_repair_target_for_player(
            damage_markers,
            player_x=100,
            player_y=200,
            player_width=36,
            player_height=48,
            requested_target=[120, 220],
        )

        self.assertEqual(resolved_target, (120, 220))

    def test_is_player_in_cannon_zone_preserves_inclusive_edges(self):
        cases = (
            ("left upper edge", 470, 420, True),
            ("left lower edge", 550, 740, True),
            ("right upper edge", 760, 420, True),
            ("right lower edge", 840, 740, True),
            ("left x just outside", 469, 420, False),
            ("between cannons", 700, 420, False),
            ("right x just outside", 841, 420, False),
            ("y just above", 470, 419, False),
            ("y just below", 470, 741, False),
        )

        for label, player_x, player_y, expected in cases:
            with self.subTest(case=label):
                self.assertEqual(
                    is_player_in_cannon_zone(player_x=player_x, player_y=player_y),
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
