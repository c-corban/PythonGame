"""Client-side rendering helpers and runtime state."""
from dataclasses import dataclass, field

import pygame

from better_together_shared.asset_catalog import (
    AIM_ASSET_ID,
    CANNONBALL_ASSET_ID,
    SHIP_DECK_ASSET_ID,
    WATER_ASSET_ID,
    WOOD_PLANK_ASSET_ID,
)
from better_together_shared.config import GAME_TITLE, WINDOW_SIZE

from .assets import load_image, load_scaled_image


size = (width, height) = WINDOW_SIZE


@dataclass
class RenderRuntime:
    window: object
    ship: object
    water: object
    aim: object
    wood_icon: object
    cannonball_icon: object
    font: object
    hit: list = field(default_factory=list)
    enemy_projectiles: list = field(default_factory=list)


_current_runtime = None
window = None
ship = None
water = None
aim = None
wood_icon = None
cannonball_icon = None
font = None
hit = []
enemy_projectiles = []


def _set_current_runtime(runtime):
    global _current_runtime, window, ship, water, aim, wood_icon, cannonball_icon, font, hit, enemy_projectiles

    _current_runtime = runtime
    if runtime is None:
        window = None
        ship = None
        water = None
        aim = None
        wood_icon = None
        cannonball_icon = None
        font = None
        hit = []
        enemy_projectiles = []
        return

    window = runtime.window
    ship = runtime.ship
    water = runtime.water
    aim = runtime.aim
    wood_icon = runtime.wood_icon
    cannonball_icon = runtime.cannonball_icon
    font = runtime.font
    hit = runtime.hit
    enemy_projectiles = runtime.enemy_projectiles


def get_runtime():
    return _current_runtime


def require_runtime():
    if _current_runtime is None:
        raise RuntimeError("Client render runtime has not been initialized.")

    return _current_runtime


def initialize_runtime():
    pygame.init()

    runtime_window = pygame.display.set_mode(size)
    pygame.display.set_caption(GAME_TITLE)

    runtime = RenderRuntime(
        window=runtime_window,
        ship=load_scaled_image(SHIP_DECK_ASSET_ID, (width // 2, height), alpha=False),
        water=load_scaled_image(WATER_ASSET_ID, (width // 4, height), alpha=False),
        aim=load_scaled_image(AIM_ASSET_ID, (80, 80)),
        wood_icon=load_image(WOOD_PLANK_ASSET_ID),
        cannonball_icon=load_image(CANNONBALL_ASSET_ID),
        font=pygame.font.SysFont(None, 64),
    )

    _set_current_runtime(runtime)
    return runtime


def shutdown_runtime(runtime=None):
    current_runtime = require_runtime() if runtime is None and _current_runtime is not None else runtime
    if current_runtime is None or current_runtime is _current_runtime:
        _set_current_runtime(None)


def _resolve_runtime_and_surface(runtime_or_surface):
    if isinstance(runtime_or_surface, RenderRuntime):
        return runtime_or_surface, runtime_or_surface.window

    return require_runtime(), runtime_or_surface


def refresh(runtime_or_surface, player_me, player_others):
    runtime, surface = _resolve_runtime_and_surface(runtime_or_surface)
    surface.blit(runtime.water, (0, 0), (0, 0, width, height))
    surface.blit(runtime.water, (width - width // 4, 0), (0, 0, width, height))
    surface.blit(runtime.ship, (width // 4, 0), (0, 0, width, height))

    for damage in runtime.hit:
        surface.blit(runtime.water, damage, (0, 0, 15, 15))
    for player in player_others:
        player.draw(surface)

    player_me.draw(surface)

    for enemy_projectile in runtime.enemy_projectiles:
        surface.blit(runtime.cannonball_icon, enemy_projectile)

    surface.blit(runtime.wood_icon, (10, 20))
    surface.blit(runtime.cannonball_icon, (10, 70))

    surface.blit(runtime.font.render("{}".format(player_me.inventoryWood), True, (0, 0, 0)), (60, 20))
    surface.blit(runtime.font.render("{}".format(player_me.inventoryCannon), True, (0, 0, 0)), (60, 70))


__all__ = [
    "RenderRuntime",
    "aim",
    "cannonball_icon",
    "font",
    "get_runtime",
    "height",
    "enemy_projectiles",
    "hit",
    "initialize_runtime",
    "refresh",
    "ship",
    "shutdown_runtime",
    "size",
    "water",
    "window",
    "width",
    "wood_icon",
]
