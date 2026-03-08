import unittest

try:
    from tests.test_support import add_workspace_package_paths
except ModuleNotFoundError:
    from test_support import add_workspace_package_paths


add_workspace_package_paths()

from better_together_shared.asset_catalog import (
    AIM_ASSET_ID,
    CLIENT_ASSET_BUNDLE,
    DEFAULT_CREW_SELECTION_ASSET_IDS,
    OBSTACLE_ASSET_ID,
    SERVER_ASSET_BUNDLE,
    WATER_ASSET_ID,
    get_asset_spec,
    get_pirate_ship_frame_asset_id,
    iter_asset_specs,
    normalize_asset_reference,
    resolve_runtime_asset_path,
)


class AssetCatalogTests(unittest.TestCase):
    def test_default_crew_selection_maps_to_runtime_generated_player_sheets(self):
        for asset_id in DEFAULT_CREW_SELECTION_ASSET_IDS:
            with self.subTest(asset_id=asset_id):
                asset_spec = get_asset_spec(asset_id)
                self.assertEqual(asset_spec.runtime_size, (36, 48))
                self.assertTrue(asset_spec.generated)
                self.assertIn(CLIENT_ASSET_BUNDLE, asset_spec.bundle_targets)
                self.assertIn(SERVER_ASSET_BUNDLE, asset_spec.bundle_targets)
                self.assertTrue(asset_spec.runtime_path.startswith("Images/players/36x48/"))
                self.assertTrue(asset_spec.source_path.startswith("assets/source/players/48x64/"))

    def test_pirate_ship_frame_asset_ids_cover_expected_runtime_sequence(self):
        self.assertEqual(
            get_asset_spec(get_pirate_ship_frame_asset_id(0)).runtime_path,
            "Images/Black Sail/pirate_ship_00000.png",
        )
        self.assertEqual(
            get_asset_spec(get_pirate_ship_frame_asset_id(0)).source_path,
            "assets/source/ships/black-sail/pirate_ship_00000.png",
        )
        self.assertEqual(
            get_asset_spec(get_pirate_ship_frame_asset_id(15)).runtime_path,
            "Images/Black Sail/pirate_ship_150000.png",
        )

    def test_resolve_runtime_asset_path_returns_catalog_runtime_path_for_asset_ids(self):
        self.assertEqual(resolve_runtime_asset_path(AIM_ASSET_ID), "Images/aim.png")
        self.assertEqual(resolve_runtime_asset_path(WATER_ASSET_ID), "Images/water.png")

    def test_normalize_asset_reference_preserves_asset_ids_and_normalizes_relative_paths(self):
        self.assertEqual(normalize_asset_reference(AIM_ASSET_ID), AIM_ASSET_ID)
        self.assertEqual(
            normalize_asset_reference(r"Images\players\36x48\captain-m-001-light.png"),
            "Images/players/36x48/captain-m-001-light.png",
        )

    def test_iter_asset_specs_filters_by_runtime_bundle_target(self):
        client_asset_ids = {asset_spec.asset_id for asset_spec in iter_asset_specs(CLIENT_ASSET_BUNDLE)}
        server_asset_ids = {asset_spec.asset_id for asset_spec in iter_asset_specs(SERVER_ASSET_BUNDLE)}

        self.assertIn(AIM_ASSET_ID, client_asset_ids)
        self.assertNotIn(AIM_ASSET_ID, server_asset_ids)
        self.assertIn(OBSTACLE_ASSET_ID, client_asset_ids)
        self.assertIn(OBSTACLE_ASSET_ID, server_asset_ids)


if __name__ == "__main__":
    unittest.main()
