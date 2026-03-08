"""Runtime asset bundle builder for Better Together."""

from __future__ import annotations

import argparse
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import pygame

from .asset_catalog import (
    CLIENT_ASSET_BUNDLE,
    SERVER_ASSET_BUNDLE,
    iter_asset_specs,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUNDLE_PACKAGE_DIRS = {
    CLIENT_ASSET_BUNDLE: Path("src") / "better_together_client",
    SERVER_ASSET_BUNDLE: Path("src") / "better_together_server",
}
COPY_BUILD_STRATEGY = "copy"
SCALE_BY_CELLS_BUILD_STRATEGY = "scale_by_cells"
SCALE_TO_SIZE_BUILD_STRATEGY = "scale_to_size"
VALID_BUILD_STRATEGIES = frozenset((COPY_BUILD_STRATEGY, SCALE_BY_CELLS_BUILD_STRATEGY, SCALE_TO_SIZE_BUILD_STRATEGY))


@dataclass(frozen=True, slots=True)
class BuildTask:
    """A concrete source-to-destination asset build action."""

    asset_id: str
    bundle_target: str
    source_path: Path
    destination_path: Path
    build_strategy: str
    source_size: tuple[int, int] | None = None
    runtime_size: tuple[int, int] | None = None
    use_top_left_transparency: bool = False
    optimize_for_collision: bool = False


@dataclass(frozen=True, slots=True)
class BuildCheckIssue:
    """A validation problem detected in a generated runtime asset bundle."""

    asset_id: str
    bundle_target: str
    message: str


def normalize_project_root(project_root=None):
    return Path(PROJECT_ROOT if project_root is None else project_root).resolve()


def normalize_output_root(project_root, output_root=None):
    return Path(project_root if output_root is None else output_root).resolve()


def resolve_repo_path(project_root, relative_or_absolute_path):
    path = Path(relative_or_absolute_path)
    if path.is_absolute():
        return path
    return Path(project_root, path)


def validate_asset_spec(asset_spec):
    if asset_spec.build_strategy not in VALID_BUILD_STRATEGIES:
        raise ValueError(
            f"Asset {asset_spec.asset_id!r} uses unsupported build strategy {asset_spec.build_strategy!r}."
        )

    if asset_spec.build_strategy == SCALE_BY_CELLS_BUILD_STRATEGY:
        if asset_spec.source_size is None or asset_spec.runtime_size is None:
            raise ValueError(
                f"Asset {asset_spec.asset_id!r} needs both source_size and runtime_size for scale_by_cells."
            )

    if asset_spec.build_strategy == SCALE_TO_SIZE_BUILD_STRATEGY and asset_spec.runtime_size is None:
        raise ValueError(
            f"Asset {asset_spec.asset_id!r} needs runtime_size for scale_to_size."
        )

    return asset_spec


def resolve_build_source_path(asset_spec, project_root):
    validate_asset_spec(asset_spec)

    source_reference = asset_spec.build_source_path or asset_spec.source_path
    if source_reference is None:
        primary_bundle_target = sorted(asset_spec.bundle_targets)[0]
        source_reference = BUNDLE_PACKAGE_DIRS[primary_bundle_target] / Path(asset_spec.runtime_path)

    return resolve_repo_path(project_root, source_reference)


def resolve_bundle_output_path(asset_spec, bundle_target, output_root):
    if bundle_target not in asset_spec.bundle_targets:
        raise ValueError(f"Asset {asset_spec.asset_id!r} is not targeted for bundle {bundle_target!r}.")

    package_dir = BUNDLE_PACKAGE_DIRS[bundle_target]
    return Path(output_root, package_dir, Path(asset_spec.runtime_path))


def create_build_task(asset_spec, bundle_target, project_root=None, output_root=None):
    project_root = normalize_project_root(project_root)
    output_root = normalize_output_root(project_root, output_root)

    return BuildTask(
        asset_id=asset_spec.asset_id,
        bundle_target=bundle_target,
        source_path=resolve_build_source_path(asset_spec, project_root),
        destination_path=resolve_bundle_output_path(asset_spec, bundle_target, output_root),
        build_strategy=asset_spec.build_strategy,
        source_size=asset_spec.source_size,
        runtime_size=asset_spec.runtime_size,
        use_top_left_transparency=asset_spec.use_top_left_transparency,
        optimize_for_collision=(bundle_target == SERVER_ASSET_BUNDLE and asset_spec.optimize_for_collision_on_server),
    )


def build_asset_tasks(bundle_target=None, project_root=None, output_root=None):
    project_root = normalize_project_root(project_root)
    output_root = normalize_output_root(project_root, output_root)
    tasks = []

    for asset_spec in iter_asset_specs(bundle_target):
        bundle_targets = (bundle_target,) if bundle_target is not None else tuple(sorted(asset_spec.bundle_targets))
        for target in bundle_targets:
            tasks.append(create_build_task(asset_spec, target, project_root=project_root, output_root=output_root))

    return tasks


def compute_scaled_dimensions(surface_size, source_size, runtime_size):
    source_width, source_height = surface_size
    source_cell_width, source_cell_height = source_size
    runtime_cell_width, runtime_cell_height = runtime_size

    if source_cell_width <= 0 or source_cell_height <= 0:
        raise ValueError("source_size values must be positive integers.")
    if runtime_cell_width <= 0 or runtime_cell_height <= 0:
        raise ValueError("runtime_size values must be positive integers.")

    scaled_width = round(source_width * runtime_cell_width / source_cell_width)
    scaled_height = round(source_height * runtime_cell_height / source_cell_height)
    return scaled_width, scaled_height


def _normalize_color(color):
    return tuple(color[:3])


def promote_surface_transparency(surface, use_top_left_transparency=False):
    color_key = surface.get_colorkey()

    if color_key is None and use_top_left_transparency:
        color_key = surface.get_at((0, 0))

    if color_key is None:
        return surface.copy()

    keyed_surface = surface.copy()
    keyed_surface.set_colorkey(_normalize_color(color_key))
    alpha_surface = pygame.Surface(keyed_surface.get_size(), pygame.SRCALPHA, 32)
    alpha_surface.blit(keyed_surface, (0, 0))
    return alpha_surface


def create_collision_mask_surface(surface):
    mask = pygame.mask.from_surface(surface)
    collision_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA, 32)
    mask.to_surface(
        surface=collision_surface,
        setcolor=(255, 255, 255, 255),
        unsetcolor=(0, 0, 0, 0),
    )
    return collision_surface


def perform_build_task(task):
    task.destination_path.parent.mkdir(parents=True, exist_ok=True)

    requires_surface_processing = (
        task.build_strategy != COPY_BUILD_STRATEGY
        or task.use_top_left_transparency
        or task.optimize_for_collision
    )

    if task.build_strategy == COPY_BUILD_STRATEGY and not requires_surface_processing:
        if task.source_path.resolve() == task.destination_path.resolve():
            return task.destination_path
        shutil.copy2(task.source_path, task.destination_path)
        return task.destination_path

    source_surface = promote_surface_transparency(
        pygame.image.load(task.source_path),
        use_top_left_transparency=task.use_top_left_transparency,
    )

    if task.build_strategy == SCALE_BY_CELLS_BUILD_STRATEGY:
        destination_size = compute_scaled_dimensions(
            source_surface.get_size(),
            task.source_size,
            task.runtime_size,
        )
        output_surface = pygame.transform.scale(source_surface, destination_size)
    elif task.build_strategy == SCALE_TO_SIZE_BUILD_STRATEGY:
        output_surface = pygame.transform.smoothscale(source_surface, task.runtime_size)
    elif task.build_strategy == COPY_BUILD_STRATEGY:
        output_surface = source_surface
    else:
        raise ValueError(f"Unsupported build strategy {task.build_strategy!r}.")

    if task.optimize_for_collision:
        output_surface = create_collision_mask_surface(output_surface)

    pygame.image.save(output_surface, task.destination_path)
    return task.destination_path


def check_build_task(task, check_staleness=False):
    if not task.source_path.exists():
        return BuildCheckIssue(
            asset_id=task.asset_id,
            bundle_target=task.bundle_target,
            message=f"missing source: {task.source_path}",
        )

    if not task.destination_path.exists():
        return BuildCheckIssue(
            asset_id=task.asset_id,
            bundle_target=task.bundle_target,
            message=f"missing output: {task.destination_path}",
        )

    if task.source_path.resolve() == task.destination_path.resolve():
        return None

    if check_staleness and task.destination_path.stat().st_mtime < task.source_path.stat().st_mtime:
        return BuildCheckIssue(
            asset_id=task.asset_id,
            bundle_target=task.bundle_target,
            message=(
                f"stale output: {task.destination_path} is older than source {task.source_path}"
            ),
        )

    return None


def check_runtime_assets(bundle_target=None, project_root=None, output_root=None, check_staleness=False):
    return [
        issue
        for issue in (
            check_build_task(task, check_staleness=check_staleness)
            for task in build_asset_tasks(
                bundle_target=bundle_target,
                project_root=project_root,
                output_root=output_root,
            )
        )
        if issue is not None
    ]


def build_runtime_assets(bundle_target=None, project_root=None, output_root=None):
    tasks = build_asset_tasks(bundle_target=bundle_target, project_root=project_root, output_root=output_root)
    for task in tasks:
        perform_build_task(task)
    return tasks


def format_build_task(task):
    return (
        f"[{task.bundle_target}] {task.asset_id}: {task.source_path} -> {task.destination_path} "
        f"({task.build_strategy})"
    )


def build_argument_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bundle",
        choices=("all", CLIENT_ASSET_BUNDLE, SERVER_ASSET_BUNDLE),
        default="all",
        help="Which runtime bundle to build or validate.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT_ROOT,
        help="Repository root used to resolve source inputs.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=None,
        help="Root directory that will receive the generated src/better_together_* runtime bundles.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Validate that the generated outputs required by the catalog exist.",
    )
    parser.add_argument(
        "--strict-staleness",
        action="store_true",
        help="When used with --check, also fail if an output is older than its preferred source.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the build plan without copying or generating files.",
    )
    return parser


def main(argv=None):
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    bundle_target = None if args.bundle == "all" else args.bundle
    project_root = normalize_project_root(args.project_root)
    output_root = normalize_output_root(project_root, args.output_root)
    tasks = build_asset_tasks(bundle_target=bundle_target, project_root=project_root, output_root=output_root)

    if args.dry_run:
        for task in tasks:
            print(format_build_task(task))
        return 0

    if args.check:
        issues = check_runtime_assets(
            bundle_target=bundle_target,
            project_root=project_root,
            output_root=output_root,
            check_staleness=args.strict_staleness,
        )
        if issues:
            for issue in issues:
                print(f"[{issue.bundle_target}] {issue.asset_id}: {issue.message}")
            return 1

        print(f"Verified {len(tasks)} runtime asset outputs.")
        return 0

    build_runtime_assets(bundle_target=bundle_target, project_root=project_root, output_root=output_root)
    print(f"Built {len(tasks)} runtime asset outputs.")
    return 0


__all__ = [
    "BUNDLE_PACKAGE_DIRS",
    "BuildCheckIssue",
    "BuildTask",
    "COPY_BUILD_STRATEGY",
    "PROJECT_ROOT",
    "SCALE_TO_SIZE_BUILD_STRATEGY",
    "SCALE_BY_CELLS_BUILD_STRATEGY",
    "VALID_BUILD_STRATEGIES",
    "build_argument_parser",
    "build_asset_tasks",
    "build_runtime_assets",
    "check_build_task",
    "check_runtime_assets",
    "compute_scaled_dimensions",
    "create_collision_mask_surface",
    "create_build_task",
    "format_build_task",
    "main",
    "normalize_output_root",
    "normalize_project_root",
    "perform_build_task",
    "promote_surface_transparency",
    "resolve_build_source_path",
    "resolve_bundle_output_path",
    "resolve_repo_path",
    "validate_asset_spec",
]
