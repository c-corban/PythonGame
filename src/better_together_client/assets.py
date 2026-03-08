"""Client asset helpers for the package runtime."""

import os
from functools import lru_cache
from pathlib import Path

import pygame

from better_together_shared.asset_catalog import normalize_asset_reference, resolve_runtime_asset_path
from better_together_shared.assets_runtime import (
    load_image as load_image_from_base,
    load_scaled_image as scale_image,
    resolve_asset_path as resolve_asset_path_from_base,
)


MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parents[1]
PACKAGE_IMAGES_DIR = MODULE_DIR / "Images"
PROJECT_IMAGES_DIR = PROJECT_ROOT / "Images"
ASSET_ROOT_OVERRIDE_ENV_VAR = "BETTER_TOGETHER_CLIENT_ASSET_ROOT"


def _discover_base_dir():
    override = os.environ.get(ASSET_ROOT_OVERRIDE_ENV_VAR)
    if override:
        return os.path.abspath(override)

    if PACKAGE_IMAGES_DIR.exists():
        return os.path.abspath(os.fspath(MODULE_DIR))

    if PROJECT_IMAGES_DIR.exists():
        return os.path.abspath(os.fspath(PROJECT_ROOT))

    return os.path.abspath(os.fspath(MODULE_DIR))


BASE_DIR = _discover_base_dir()


def resolve_asset_path(path):
    return resolve_asset_path_from_base(BASE_DIR, resolve_runtime_asset_path(path))


@lru_cache(maxsize=None)
def _load_image_cached(path, alpha=True):
    return load_image_from_base(BASE_DIR, resolve_runtime_asset_path(path), alpha)


def load_image(path, alpha=True):
    return _load_image_cached(normalize_asset_reference(path), alpha)


load_image.cache_clear = _load_image_cached.cache_clear
load_image.cache_info = _load_image_cached.cache_info


@lru_cache(maxsize=None)
def _load_scaled_image_cached(path, size, alpha=True):
    return scale_image(load_image(path, alpha), size)


def load_scaled_image(path, size, alpha=True):
    return _load_scaled_image_cached(normalize_asset_reference(path), tuple(size), alpha)


load_scaled_image.cache_clear = _load_scaled_image_cached.cache_clear
load_scaled_image.cache_info = _load_scaled_image_cached.cache_info


__all__ = [
    "ASSET_ROOT_OVERRIDE_ENV_VAR",
    "BASE_DIR",
    "load_image",
    "load_scaled_image",
    "pygame",
    "resolve_asset_path",
]
