"""Shared runtime asset identifiers and metadata for Better Together."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import PurePosixPath


CLIENT_ASSET_BUNDLE = "client"
SERVER_ASSET_BUNDLE = "server"


@dataclass(frozen=True, slots=True)
class AssetSpec:
    """Describes one logical asset and its current runtime/source locations."""

    asset_id: str
    runtime_path: str
    source_path: str | None = None
    build_source_path: str | None = None
    bundle_targets: frozenset[str] = frozenset((CLIENT_ASSET_BUNDLE,))
    generated: bool = False
    hot: bool = False
    alpha: bool = True
    build_strategy: str = "copy"
    source_size: tuple[int, int] | None = None
    runtime_size: tuple[int, int] | None = None
    use_top_left_transparency: bool = False
    optimize_for_collision_on_server: bool = False


def _posix_path(*parts):
    return str(PurePosixPath(*parts))


def _bundle_targets(*targets):
    return frozenset(targets)


def _client_package_path(*parts):
    return _posix_path("src", "better_together_client", *parts)


def _server_package_path(*parts):
    return _posix_path("src", "better_together_server", *parts)


def _source_asset_path(*parts):
    return _posix_path("assets", "source", *parts)


AIM_ASSET_ID = "ui.aim"
CANNONBALL_ASSET_ID = "projectile.cannonball"
WOOD_PLANK_ASSET_ID = "ui.wood-plank"
WATER_ASSET_ID = "world.water"
SHIP_DECK_ASSET_ID = "world.ship-deck"
OBSTACLE_ASSET_ID = "world.obstacle"

CREW_CAPTAIN_M_001_LIGHT_ASSET_ID = "crew.captain-m-001-light"
CREW_PIRATE_F_001_BROWN_ASSET_ID = "crew.pirate-f-001-brown"
CREW_PIRATE_F_001_LIGHT_ASSET_ID = "crew.pirate-f-001-light"
CREW_PIRATE_M_001_LIGHT_ASSET_ID = "crew.pirate-m-001-light"
CREW_PIRATE_M_002_LIGHT_ASSET_ID = "crew.pirate-m-002-light"
CREW_PIRATE_M_003_LIGHT_ALT_ASSET_ID = "crew.pirate-m-003-light-alt"
CREW_PIRATE_M_003_LIGHT_ASSET_ID = "crew.pirate-m-003-light"
CREW_PIRATE_M_004_LIGHT_ASSET_ID = "crew.pirate-m-004-light"

CREW_MEMBER_ASSET_IDS = (
    CREW_CAPTAIN_M_001_LIGHT_ASSET_ID,
    CREW_PIRATE_F_001_BROWN_ASSET_ID,
    CREW_PIRATE_F_001_LIGHT_ASSET_ID,
    CREW_PIRATE_M_001_LIGHT_ASSET_ID,
    CREW_PIRATE_M_002_LIGHT_ASSET_ID,
    CREW_PIRATE_M_003_LIGHT_ALT_ASSET_ID,
    CREW_PIRATE_M_003_LIGHT_ASSET_ID,
    CREW_PIRATE_M_004_LIGHT_ASSET_ID,
)

DEFAULT_CREW_SELECTION_ASSET_IDS = (
    CREW_CAPTAIN_M_001_LIGHT_ASSET_ID,
    CREW_PIRATE_M_001_LIGHT_ASSET_ID,
    CREW_PIRATE_M_003_LIGHT_ALT_ASSET_ID,
    CREW_PIRATE_M_004_LIGHT_ASSET_ID,
)

PIRATE_SHIP_FRAME_ASSET_IDS = tuple(
    f"pirate-ship.black-sail.frame-{frame:02d}"
    for frame in range(16)
)


def _crew_runtime_path(filename):
    return _posix_path("Images", "players", "36x48", filename)


def _crew_source_path(filename):
    return _source_asset_path("players", "48x64", filename)


def _crew_spec(asset_id, filename):
    return AssetSpec(
        asset_id=asset_id,
        runtime_path=_crew_runtime_path(filename),
        source_path=_crew_source_path(filename),
        build_source_path=_crew_source_path(filename),
        bundle_targets=_bundle_targets(CLIENT_ASSET_BUNDLE, SERVER_ASSET_BUNDLE),
        generated=True,
        hot=True,
        alpha=True,
        build_strategy="scale_by_cells",
        source_size=(48, 64),
        runtime_size=(36, 48),
        optimize_for_collision_on_server=True,
    )


def _pirate_ship_runtime_path(frame):
    return _posix_path("Images", "Black Sail", f"pirate_ship_{frame}0000.png")


def _pirate_ship_source_path(frame):
    return _source_asset_path("ships", "black-sail", f"pirate_ship_{frame}0000.png")


def _pirate_ship_spec(frame):
    asset_id = PIRATE_SHIP_FRAME_ASSET_IDS[frame]
    return AssetSpec(
        asset_id=asset_id,
        runtime_path=_pirate_ship_runtime_path(frame),
        source_path=_pirate_ship_source_path(frame),
        build_source_path=_pirate_ship_source_path(frame),
        bundle_targets=_bundle_targets(CLIENT_ASSET_BUNDLE),
        generated=True,
        hot=True,
        alpha=True,
    )


ASSET_SPECS = {
    AIM_ASSET_ID: AssetSpec(
        asset_id=AIM_ASSET_ID,
        runtime_path=_posix_path("Images", "aim.png"),
        build_source_path=_client_package_path("Images", "aim.png"),
        bundle_targets=_bundle_targets(CLIENT_ASSET_BUNDLE),
        alpha=True,
    ),
    CANNONBALL_ASSET_ID: AssetSpec(
        asset_id=CANNONBALL_ASSET_ID,
        runtime_path=_posix_path("Images", "cannonball.png"),
        source_path=_source_asset_path("projectiles", "cannonball.png"),
        build_source_path=_source_asset_path("projectiles", "cannonball.png"),
        bundle_targets=_bundle_targets(CLIENT_ASSET_BUNDLE),
        alpha=True,
        build_strategy="scale_to_size",
        runtime_size=(40, 40),
    ),
    WOOD_PLANK_ASSET_ID: AssetSpec(
        asset_id=WOOD_PLANK_ASSET_ID,
        runtime_path=_posix_path("Images", "wood plank.png"),
        source_path=_source_asset_path("ui", "wood-plank.png"),
        build_source_path=_source_asset_path("ui", "wood-plank.png"),
        bundle_targets=_bundle_targets(CLIENT_ASSET_BUNDLE),
        alpha=True,
        build_strategy="scale_to_size",
        runtime_size=(40, 40),
    ),
    WATER_ASSET_ID: AssetSpec(
        asset_id=WATER_ASSET_ID,
        runtime_path=_posix_path("Images", "water.png"),
        build_source_path=_client_package_path("Images", "water.png"),
        bundle_targets=_bundle_targets(CLIENT_ASSET_BUNDLE),
        alpha=False,
    ),
    SHIP_DECK_ASSET_ID: AssetSpec(
        asset_id=SHIP_DECK_ASSET_ID,
        runtime_path=_posix_path("Images", "ocean_e_new_ship_small.png"),
        build_source_path=_client_package_path("Images", "ocean_e_new_ship_small.png"),
        bundle_targets=_bundle_targets(CLIENT_ASSET_BUNDLE),
        alpha=False,
    ),
    OBSTACLE_ASSET_ID: AssetSpec(
        asset_id=OBSTACLE_ASSET_ID,
        runtime_path=_posix_path("Images", "obstacle.png"),
        source_path=_source_asset_path("world", "obstacle.png"),
        build_source_path=_source_asset_path("world", "obstacle.png"),
        bundle_targets=_bundle_targets(CLIENT_ASSET_BUNDLE, SERVER_ASSET_BUNDLE),
        hot=True,
        alpha=True,
        use_top_left_transparency=True,
        optimize_for_collision_on_server=True,
    ),
    CREW_CAPTAIN_M_001_LIGHT_ASSET_ID: _crew_spec(
        CREW_CAPTAIN_M_001_LIGHT_ASSET_ID,
        "captain-m-001-light.png",
    ),
    CREW_PIRATE_F_001_BROWN_ASSET_ID: _crew_spec(
        CREW_PIRATE_F_001_BROWN_ASSET_ID,
        "pirate-f-001-brown.png",
    ),
    CREW_PIRATE_F_001_LIGHT_ASSET_ID: _crew_spec(
        CREW_PIRATE_F_001_LIGHT_ASSET_ID,
        "pirate-f-001-light.png",
    ),
    CREW_PIRATE_M_001_LIGHT_ASSET_ID: _crew_spec(
        CREW_PIRATE_M_001_LIGHT_ASSET_ID,
        "pirate-m-001-light.png",
    ),
    CREW_PIRATE_M_002_LIGHT_ASSET_ID: _crew_spec(
        CREW_PIRATE_M_002_LIGHT_ASSET_ID,
        "pirate-m-002-light.png",
    ),
    CREW_PIRATE_M_003_LIGHT_ALT_ASSET_ID: _crew_spec(
        CREW_PIRATE_M_003_LIGHT_ALT_ASSET_ID,
        "pirate-m-003-light-alt.png",
    ),
    CREW_PIRATE_M_003_LIGHT_ASSET_ID: _crew_spec(
        CREW_PIRATE_M_003_LIGHT_ASSET_ID,
        "pirate-m-003-light.png",
    ),
    CREW_PIRATE_M_004_LIGHT_ASSET_ID: _crew_spec(
        CREW_PIRATE_M_004_LIGHT_ASSET_ID,
        "pirate-m-004-light.png",
    ),
}

ASSET_SPECS.update(
    {
        pirate_ship_asset_id: _pirate_ship_spec(frame)
        for frame, pirate_ship_asset_id in enumerate(PIRATE_SHIP_FRAME_ASSET_IDS)
    }
)


def get_asset_spec(asset_id):
    return ASSET_SPECS[asset_id]


def is_asset_id(asset_reference):
    return isinstance(asset_reference, str) and asset_reference in ASSET_SPECS


def normalize_asset_reference(asset_reference):
    reference_text = os.fspath(asset_reference)
    if reference_text in ASSET_SPECS:
        return reference_text
    return reference_text.replace("\\", "/")


def resolve_runtime_asset_path(asset_reference):
    normalized_reference = normalize_asset_reference(asset_reference)
    asset_spec = ASSET_SPECS.get(normalized_reference)
    if asset_spec is not None:
        return asset_spec.runtime_path
    return normalized_reference


def iter_asset_specs(bundle_target=None):
    if bundle_target is None:
        return tuple(ASSET_SPECS.values())

    return tuple(
        asset_spec
        for asset_spec in ASSET_SPECS.values()
        if bundle_target in asset_spec.bundle_targets
    )


def get_pirate_ship_frame_asset_id(frame):
    if not 0 <= frame < len(PIRATE_SHIP_FRAME_ASSET_IDS):
        raise ValueError(f"Pirate ship frame must be in range 0..{len(PIRATE_SHIP_FRAME_ASSET_IDS) - 1}.")

    return PIRATE_SHIP_FRAME_ASSET_IDS[frame]


__all__ = [
    "AIM_ASSET_ID",
    "ASSET_SPECS",
    "AssetSpec",
    "CANNONBALL_ASSET_ID",
    "CLIENT_ASSET_BUNDLE",
    "CREW_CAPTAIN_M_001_LIGHT_ASSET_ID",
    "CREW_MEMBER_ASSET_IDS",
    "CREW_PIRATE_F_001_BROWN_ASSET_ID",
    "CREW_PIRATE_F_001_LIGHT_ASSET_ID",
    "CREW_PIRATE_M_001_LIGHT_ASSET_ID",
    "CREW_PIRATE_M_002_LIGHT_ASSET_ID",
    "CREW_PIRATE_M_003_LIGHT_ALT_ASSET_ID",
    "CREW_PIRATE_M_003_LIGHT_ASSET_ID",
    "CREW_PIRATE_M_004_LIGHT_ASSET_ID",
    "DEFAULT_CREW_SELECTION_ASSET_IDS",
    "OBSTACLE_ASSET_ID",
    "PIRATE_SHIP_FRAME_ASSET_IDS",
    "SERVER_ASSET_BUNDLE",
    "SHIP_DECK_ASSET_ID",
    "WATER_ASSET_ID",
    "WOOD_PLANK_ASSET_ID",
    "get_asset_spec",
    "get_pirate_ship_frame_asset_id",
    "is_asset_id",
    "iter_asset_specs",
    "normalize_asset_reference",
    "resolve_runtime_asset_path",
]
