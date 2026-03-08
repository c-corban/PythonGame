"""Server-side AI helpers for crew members and pirate ships."""
import random
import time

from better_together_shared.asset_catalog import OBSTACLE_ASSET_ID, get_pirate_ship_frame_asset_id
from better_together_shared.config import WINDOW_HEIGHT, WINDOW_WIDTH

from .assets import load_scaled_image
from .game import MAX_SIMULATION_STEPS_PER_ADVANCE

from .room_manager import default_room_registry


width = WINDOW_WIDTH
height = WINDOW_HEIGHT
games = default_room_registry.games
SIMULATION_POLL_INTERVAL_SECONDS = 0.01


def _resolve_room_registry(room_registry):
    return default_room_registry if room_registry is None else room_registry


def _obstacle_surface():
    return load_scaled_image(OBSTACLE_ASSET_ID, (width // 2, height))


def advance_ai_crew(game):
    obstacle = _obstacle_surface()

    for crew_index, ai_controlled in enumerate(game.ai):
        if ai_controlled:
            game.crew_members[crew_index].move(obstacle)


def _crew_member_hits_pirate_ship(crew_member, pirate_ship):
    return (
        crew_member.cannonBallAnimationX in range(pirate_ship.x, pirate_ship.x + pirate_ship.width)
        and crew_member.cannonBallAnimationY in range(pirate_ship.y, pirate_ship.y + pirate_ship.height)
    )


def _create_enemy_projectile(pirate_ship, impact_x, impact_y, total_ticks):
    total_ticks = max(1, int(total_ticks))
    origin_x = pirate_ship.x + pirate_ship.width // 4
    origin_y = pirate_ship.y + pirate_ship.height // 4
    return {
        "x": origin_x,
        "y": origin_y,
        "origin_x": origin_x,
        "origin_y": origin_y,
        "impact_x": impact_x,
        "impact_y": impact_y,
        "ticks_remaining": total_ticks,
        "total_ticks": total_ticks,
    }


def advance_enemy_projectiles(game):
    active_enemy_projectiles = []

    for projectile in game.enemy_projectiles:
        projectile["ticks_remaining"] -= 1

        if projectile["ticks_remaining"] <= 0:
            game.damage_markers.append((projectile["impact_x"], projectile["impact_y"]))
            continue

        elapsed_ticks = projectile["total_ticks"] - projectile["ticks_remaining"]
        projectile["x"] = round(
            projectile["origin_x"]
            + (projectile["impact_x"] - projectile["origin_x"]) * elapsed_ticks / projectile["total_ticks"]
        )
        projectile["y"] = round(
            projectile["origin_y"]
            + (projectile["impact_y"] - projectile["origin_y"]) * elapsed_ticks / projectile["total_ticks"]
        )
        active_enemy_projectiles.append(projectile)

    game.enemy_projectiles = active_enemy_projectiles


def advance_pirate_ships(game):
    for pirate_ship in game.pirate_ships:
        for crew_member in game.crew_members:
            if _crew_member_hits_pirate_ship(crew_member, pirate_ship):
                (pirate_ship.x, pirate_ship.y) = (WINDOW_WIDTH // 2, -600)

        if not random.randrange(60) % 20:
            pirate_ship.increment = random.randrange(-1, 2)
        elif random.randrange(60) % 20:
            pirate_ship.increment = 0

        if pirate_ship.frame == 0 and pirate_ship.increment == -1:
            pirate_ship.frame = 15
        elif pirate_ship.frame == 15 and pirate_ship.increment == 1:
            pirate_ship.frame = 0
        else:
            pirate_ship.frame += pirate_ship.increment

        pirate_ship.char = get_pirate_ship_frame_asset_id(pirate_ship.frame)

        if not random.randrange(60) % 12:
            break

        ship_min_width = -50
        ship_max_width = 900
        ship_min_height = -300
        ship_max_height = 900

        if pirate_ship.frame == 0:
            if pirate_ship.y + pirate_ship.velocity < pirate_ship.maxHeight and ((pirate_ship.x < ship_min_width or pirate_ship.x > ship_max_width) or (pirate_ship.y + pirate_ship.velocity < ship_min_height or pirate_ship.y + pirate_ship.velocity > ship_max_height)):
                pirate_ship.y += pirate_ship.velocity

        if pirate_ship.y + pirate_ship.velocity < pirate_ship.maxHeight and pirate_ship.x + pirate_ship.velocity < pirate_ship.maxWidth and ((pirate_ship.x + pirate_ship.velocity < ship_min_width or pirate_ship.x + pirate_ship.velocity > ship_max_width) or (pirate_ship.y + pirate_ship.velocity < ship_min_height or pirate_ship.y + pirate_ship.velocity > ship_max_height)):
            if pirate_ship.frame == 1:
                pirate_ship.x += pirate_ship.velocity // 2
                pirate_ship.y += pirate_ship.velocity

            if pirate_ship.frame == 2:
                pirate_ship.x += pirate_ship.velocity
                pirate_ship.y += pirate_ship.velocity

            if pirate_ship.frame == 3:
                pirate_ship.x += pirate_ship.velocity
                pirate_ship.y += pirate_ship.velocity // 2

        if pirate_ship.frame == 4:
            if pirate_ship.x + pirate_ship.velocity < pirate_ship.maxWidth and ((pirate_ship.x + pirate_ship.velocity < ship_min_width or pirate_ship.x + pirate_ship.velocity > ship_max_width) or (pirate_ship.y < ship_min_height or pirate_ship.y > ship_max_height)):
                pirate_ship.x += pirate_ship.velocity

        if pirate_ship.x + pirate_ship.velocity < pirate_ship.maxWidth and pirate_ship.y - pirate_ship.velocity > ship_min_height and ((pirate_ship.x + pirate_ship.velocity < ship_min_width or pirate_ship.x + pirate_ship.velocity > ship_max_width) or (pirate_ship.y - pirate_ship.velocity < ship_min_height or pirate_ship.y - pirate_ship.velocity > ship_max_height)):
            if pirate_ship.frame == 5:
                pirate_ship.x += pirate_ship.velocity
                pirate_ship.y -= pirate_ship.velocity // 2

            if pirate_ship.frame == 6:
                pirate_ship.x += pirate_ship.velocity
                pirate_ship.y -= pirate_ship.velocity

            if pirate_ship.frame == 7:
                pirate_ship.x += pirate_ship.velocity // 2
                pirate_ship.y -= pirate_ship.velocity

        if pirate_ship.frame == 8:
            if pirate_ship.y - pirate_ship.velocity > ship_min_height and ((pirate_ship.x < ship_min_width or pirate_ship.x > ship_max_width) or (pirate_ship.y - pirate_ship.velocity < ship_min_height or pirate_ship.y - pirate_ship.velocity > ship_max_height)):
                pirate_ship.y -= pirate_ship.velocity

        if pirate_ship.y - pirate_ship.velocity > ship_min_height and pirate_ship.x - pirate_ship.velocity > ship_min_width and ((pirate_ship.x - pirate_ship.velocity < ship_min_width or pirate_ship.x - pirate_ship.velocity > ship_max_width) or (pirate_ship.y - pirate_ship.velocity < ship_min_height or pirate_ship.y - pirate_ship.velocity > ship_max_height)):
            if pirate_ship.frame == 9:
                pirate_ship.x -= pirate_ship.velocity // 2
                pirate_ship.y -= pirate_ship.velocity

            if pirate_ship.frame == 10:
                pirate_ship.x -= pirate_ship.velocity
                pirate_ship.y -= pirate_ship.velocity

            if pirate_ship.frame == 11:
                pirate_ship.x -= pirate_ship.velocity
                pirate_ship.y -= pirate_ship.velocity // 2

        if pirate_ship.frame == 12:
            if pirate_ship.x - pirate_ship.velocity > ship_min_width and ((pirate_ship.x - pirate_ship.velocity < ship_min_width or pirate_ship.x - pirate_ship.velocity > ship_max_width) or (pirate_ship.y < ship_min_height or pirate_ship.y > ship_max_height)):
                pirate_ship.x -= pirate_ship.velocity

        if pirate_ship.x - pirate_ship.velocity > ship_min_width and pirate_ship.y + pirate_ship.velocity < pirate_ship.maxHeight and ((pirate_ship.x - pirate_ship.velocity < ship_min_width or pirate_ship.x - pirate_ship.velocity > ship_max_width) or (pirate_ship.y + pirate_ship.velocity < ship_min_height or pirate_ship.y + pirate_ship.velocity > ship_max_height)):
            if pirate_ship.frame == 13:
                pirate_ship.x -= pirate_ship.velocity
                pirate_ship.y += pirate_ship.velocity // 2
            if pirate_ship.frame == 14:
                pirate_ship.x -= pirate_ship.velocity
                pirate_ship.y += pirate_ship.velocity
            if pirate_ship.frame == 15:
                pirate_ship.x -= pirate_ship.velocity // 2
                pirate_ship.y += pirate_ship.velocity


def advance_resource_refills(game):
    for crew_index, crew_member in enumerate(game.crew_members):
        if crew_member.inventoryCannon <= 0:
            game.inventory_cannon_refill_ticks[crew_index] += 1
            if game.inventory_cannon_refill_ticks[crew_index] >= game.resource_refill_interval_ticks:
                crew_member.inventoryCannon = 9
                game.inventory_cannon_refill_ticks[crew_index] = 0
        else:
            game.inventory_cannon_refill_ticks[crew_index] = 0

        if crew_member.inventoryWood <= 0:
            game.inventory_wood_refill_ticks[crew_index] += 1
            if game.inventory_wood_refill_ticks[crew_index] >= game.resource_refill_interval_ticks:
                crew_member.inventoryWood = 9
                game.inventory_wood_refill_ticks[crew_index] = 0
        else:
            game.inventory_wood_refill_ticks[crew_index] = 0


def advance_enemy_attacks(game):
    game.enemy_attack_cooldown_ticks += 1
    if game.enemy_attack_cooldown_ticks < game.enemy_attack_interval_ticks:
        return

    game.enemy_attack_cooldown_ticks = 0
    target = random.choice(game.active_enemy_attack_targets())
    impact_x = target.x + target.width // 4 + random.randrange(-300, 301)
    impact_y = target.y + target.height // 4 + random.randrange(-300, 301)

    if impact_y < 820 and game.pirate_ships:
        firing_ship = random.choice(game.pirate_ships)
        game.enemy_projectiles.append(
            _create_enemy_projectile(
                firing_ship,
                impact_x,
                impact_y,
                total_ticks=game.tick_rate_hz,
            )
        )


def advance_game(game):
    advance_resource_refills(game)
    advance_ai_crew(game)
    advance_pirate_ships(game)
    advance_enemy_attacks(game)
    advance_enemy_projectiles(game)


def advance_ready_rooms(room_registry=None, now=None, max_steps_per_room=MAX_SIMULATION_STEPS_PER_ADVANCE):
    room_registry = _resolve_room_registry(room_registry)
    room_registry.advance_ready_games(
        advance_game,
        now=now,
        max_steps_per_room=max_steps_per_room,
    )


def run_simulation_loop(stop_event, room_registry=None, poll_interval=SIMULATION_POLL_INTERVAL_SECONDS):
    room_registry = _resolve_room_registry(room_registry)

    while not stop_event.wait(poll_interval):
        advance_ready_rooms(room_registry=room_registry)


def ai_move(game_id, room_registry=None):
    room_registry = _resolve_room_registry(room_registry)

    with room_registry.lock:
        game = room_registry.games.get(game_id)
        if game is None:
            return

        advance_ai_crew(game)


def ship_ai(game_id, room_registry=None):
    room_registry = _resolve_room_registry(room_registry)
    with room_registry.lock:
        game = room_registry.games.get(game_id)
        if game is None:
            return

        advance_pirate_ships(game)


__all__ = [
    "SIMULATION_POLL_INTERVAL_SECONDS",
    "advance_ai_crew",
    "advance_enemy_attacks",
    "advance_enemy_projectiles",
    "advance_game",
    "advance_pirate_ships",
    "advance_ready_rooms",
    "advance_resource_refills",
    "ai_move",
    "games",
    "height",
    "run_simulation_loop",
    "ship_ai",
    "width",
]
