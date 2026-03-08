"""Client gameplay loop orchestration."""

import pygame

from better_together_shared.config import CLIENT_SERVER_HOST, CLIENT_SERVER_PORT

from . import render
from .network import Network
from .session import GameplaySessionState


def connect_to_server():
    server = Network()
    player_me = server.connect()
    if player_me is None:
        raise SystemExit(
            f"Could not connect to the server on {CLIENT_SERVER_HOST}:{CLIENT_SERVER_PORT}. "
            "Start the server entrypoint first (for example `python -m better_together_server`) or update the client host settings."
        )

    return server, server.getPlayer()


def sync_remote_players(server, player_me, runtime, repaired_damage_markers=None):
    player_others = server.send(player_me, repaired_damage_markers=repaired_damage_markers)
    runtime.hit[:] = server.damage_markers
    runtime.enemy_projectiles[:] = server.enemy_projectiles
    if player_others is None:
        return []

    return player_others


def update_game_over_overlay(runtime, session_state):
    if len(runtime.hit) >= 30:
        session_state.game_over = True

    if not session_state.game_over:
        return True

    game_over_font = pygame.font.SysFont(None, 256)
    runtime.window.blit(
        game_over_font.render("Game Over", True, (255, 0, 0)),
        (render.width // 8, render.height // 2),
    )
    session_state.game_over_count += 1
    return session_state.game_over_count <= 60 * 10


def handle_repairs(runtime, session_state, player_me, frame_state):
    for damage in runtime.hit[:]:
        if damage[0] + 15 // 2 in range(player_me.x - player_me.width // 3, player_me.x + player_me.width + player_me.width // 3) and damage[1] + 15 // 2 in range(player_me.y - player_me.width // 3, player_me.y + player_me.height + player_me.width // 3):
            if player_me.inventoryWood > 0:
                runtime.window.blit(runtime.font.render(f"Hold SPACE for {int(session_state.repair_cooldown / 6) / 10} seconds to repair", True, (255, 255, 255)), (render.width // 4 - 50, render.height - render.height // 12))
                frame_state.repair_info_displayed = True
                keys = pygame.key.get_pressed()
                if session_state.repair_cooldown > 0:
                    if keys[pygame.K_SPACE]:
                        session_state.repair_cooldown -= 1
                else:
                    player_me.inventoryWood -= 1
                    runtime.hit.remove(damage)
                    session_state.queue_repaired_damage_marker(damage)
                    session_state.repair_cooldown = 60 * 3
            else:
                if not frame_state.shoot_info_displayed and not frame_state.repair_info_displayed:
                    runtime.window.blit(runtime.font.render("No Wood", True, (255, 255, 255)), (render.width // 2 - 50, render.height - render.height // 12))


def handle_cannon_controls(runtime, session_state, player_me, frame_state):
    if 420 <= player_me.y <= 740 and (470 <= player_me.x <= 550 or 760 <= player_me.x <= 840):
        keys = pygame.key.get_pressed()
        if player_me.inventoryCannon > 0 and session_state.cannon_cooldown <= 0 and not frame_state.repair_info_displayed:
            frame_state.shoot_info_displayed = True
            if keys[pygame.K_SPACE]:
                if session_state.cannon_shoot <= 0:
                    runtime.window.blit(runtime.font.render("Release SPACE to shoot", True, (255, 255, 255)), (render.width // 3 - 50, render.height - render.height // 12))
                else:
                    runtime.window.blit(runtime.font.render("Release SPACE to cancel", True, (255, 255, 255)), (render.width // 3 - 50, render.height - render.height // 12))
                if (keys[ord("w")] or keys[pygame.K_UP]) and session_state.aim_y - session_state.aim_velocity > 0:
                    session_state.aim_y -= session_state.aim_velocity
                    session_state.cannon_shoot = 0

                if (keys[ord("a")] or keys[pygame.K_LEFT]) and session_state.aim_x - session_state.aim_velocity > 0:
                    session_state.aim_x -= session_state.aim_velocity
                    session_state.cannon_shoot = 0

                if (keys[ord("s")] or keys[pygame.K_DOWN]) and session_state.aim_y + session_state.aim_velocity < render.height:
                    session_state.aim_y += session_state.aim_velocity
                    session_state.cannon_shoot = 0

                if (keys[ord("d")] or keys[pygame.K_RIGHT]) and session_state.aim_x + session_state.aim_velocity < render.width:
                    session_state.aim_x += session_state.aim_velocity
                    session_state.cannon_shoot = 0

                runtime.window.blit(runtime.aim, (session_state.aim_x, session_state.aim_y), (0, 0, render.width, render.height))
            else:
                session_state.shoot_animation = True
                if not session_state.cannon_shoot:
                    player_me.inventoryCannon -= 1
                    session_state.cannon_cooldown = 60 * 3

                if session_state.cannon_shoot > 60 * 1:
                    session_state.aim_y = player_me.y - player_me.height
                    if 470 <= player_me.x <= 550:
                        session_state.aim_x = player_me.x - 6 * player_me.width
                    if 760 <= player_me.x <= 840:
                        session_state.aim_x = player_me.x + 6 * player_me.width
                if not frame_state.repair_info_displayed:
                    runtime.window.blit(runtime.font.render("Hold SPACE to use Cannon", True, (255, 255, 255)), (render.width // 3 - 50, render.height - render.height // 12))
                player_me.move()
        else:
            if session_state.cannon_cooldown > 0 and player_me.inventoryCannon > 0:
                if not frame_state.repair_info_displayed:
                    runtime.window.blit(runtime.font.render(f"Hold SPACE for {int(session_state.cannon_cooldown / 6) / 10} seconds to reload", True, (255, 255, 255)), (render.width // 4 - 50, render.height - render.height // 12))
                if keys[pygame.K_SPACE]:
                    session_state.cannon_cooldown -= 1
                    session_state.aim_y = player_me.y - player_me.height
                    if 470 <= player_me.x <= 550:
                        session_state.aim_x = player_me.x - 6 * player_me.width
                    if 760 <= player_me.x <= 840:
                        session_state.aim_x = player_me.x + 6 * player_me.width
            elif not frame_state.repair_info_displayed:
                runtime.window.blit(runtime.font.render("No Ammo", True, (255, 255, 255)), (render.width // 2 - 50, render.height - render.height // 12))
            player_me.move()
        return

    player_me.move()
    if session_state.info_count < 60 * 5:
        session_state.info_count += 1
        if not frame_state.shoot_info_displayed and not frame_state.repair_info_displayed:
            runtime.window.blit(runtime.font.render("Use WASD or Arrow Keys to MOVE", True, (255, 255, 255)), (render.width // 4 - 50, render.height - render.height // 12))


def update_shoot_animation(session_state, player_me):
    if not session_state.shoot_animation:
        return

    if session_state.cannon_shoot <= 60 * 1:
        session_state.cannon_shoot += 1
        player_me.cannonBallAnimationX = round(
            player_me.x
            - 60
            - (player_me.x - session_state.aim_x + 20) * session_state.cannon_shoot / 60
        )
        player_me.cannonBallAnimationY = round(
            player_me.y
            + 20
            - (player_me.y - session_state.aim_y + 20) * session_state.cannon_shoot / 60
        )
        return

    (player_me.targetX, player_me.targetY) = (player_me.cannonBallAnimationX, player_me.cannonBallAnimationY)
    session_state.shoot_animation = False


def main():
    runtime = render.initialize_runtime()

    game = True
    server = None

    try:
        server, player_me = connect_to_server()

        framerate = pygame.time.Clock()
        session_state = GameplaySessionState()

        while game:
            frame_state = session_state.begin_frame()
            framerate.tick(60)

            repaired_damage_markers = session_state.consume_repaired_damage_markers()
            player_others = sync_remote_players(
                server,
                player_me,
                runtime,
                repaired_damage_markers=repaired_damage_markers,
            )

            render.refresh(runtime, player_me, player_others)
            keep_running = update_game_over_overlay(runtime, session_state)

            if not session_state.game_over:
                handle_repairs(runtime, session_state, player_me, frame_state)
                handle_cannon_controls(runtime, session_state, player_me, frame_state)
                update_shoot_animation(session_state, player_me)

            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game = False

            if not keep_running:
                game = False
    finally:
        if server is not None:
            server.close()
        render.shutdown_runtime(runtime)
        pygame.quit()


__all__ = ["main"]
