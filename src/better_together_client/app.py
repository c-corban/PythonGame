"""Client application entrypoint for Better Together."""

from . import network as network_module
from . import render as render_module
from .game_loop import main


Network = network_module.Network
buffer = network_module.buffer
refresh = render_module.refresh
size = render_module.size
width = render_module.width
height = render_module.height


def __getattr__(name):
    if name in {
        "aim",
        "cannonball_icon",
        "client_player_class",
        "font",
        "hit",
        "ship",
        "water",
        "window",
        "wood_icon",
    }:
        runtime = render_module.get_runtime()
        if runtime is not None and hasattr(runtime, name):
            return getattr(runtime, name)
        if hasattr(render_module, name):
            return getattr(render_module, name)
        return getattr(network_module, name)

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["Network", "buffer", "height", "main", "refresh", "size", "width"]
