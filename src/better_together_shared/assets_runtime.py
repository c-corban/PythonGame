"""Shared asset-loader implementation for both runtime packages."""

import os

import pygame


def resolve_asset_path(base_dir, path):
    normalized_path = path.replace("\\", os.sep)
    if os.path.isabs(normalized_path):
        return normalized_path

    return os.path.join(base_dir, normalized_path)


def can_convert_images():
    return pygame.display.get_init() and pygame.display.get_surface() is not None


def load_image(base_dir, path, alpha=True):
    image = pygame.image.load(resolve_asset_path(base_dir, path))

    if not can_convert_images():
        return image

    return image.convert_alpha() if alpha else image.convert()


def load_scaled_image(image, size):
    return pygame.transform.scale(image, size)


__all__ = ["can_convert_images", "load_image", "load_scaled_image", "pygame", "resolve_asset_path"]
