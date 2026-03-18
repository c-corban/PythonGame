"""Client gameplay loop orchestration."""

import pygame

from better_together_shared.collision import (
    is_player_in_cannon_zone as is_player_in_shared_cannon_zone,
    resolve_repair_target_for_player,
)
from better_together_shared.config import CLIENT_SERVER_HOST, CLIENT_SERVER_PORT

from . import render
from .network import Network
from .session import GameplaySessionState


ACTION_PROMPT_TEXT_COLOR = (255, 255, 255)
ACTION_PROMPT_BACKGROUND_COLOR = (35, 35, 35)
ACTION_PROMPT_BORDER_COLOR = (255, 255, 255)
REPAIR_PROGRESS_COLOR = (166, 111, 68)
RELOAD_PROGRESS_COLOR = (170, 170, 170)
ACTION_PROMPT_BAR_WIDTH = 220
ACTION_PROMPT_BAR_HEIGHT = 18
ACTION_PROMPT_BAR_GAP = 10
ACTION_PROMPT_ICON_GAP = 12
ACTION_PROMPT_STACK_GAP = 12
ACTION_PROMPT_BOTTOM_MARGIN = 42
ACTION_PROMPT_BAR_LABEL = "HOLD SPACE"
ACTION_PROMPT_BAR_LABEL_COLOR = (255, 255, 255)
ACTION_PROMPT_BAR_LABEL_FONT_SIZE = 24


def connect_to_server():
    server = Network()
    player_me = server.connect()
    if player_me is None:
        raise SystemExit(
            f"Could not connect to the server on {CLIENT_SERVER_HOST}:{CLIENT_SERVER_PORT}. "
            "Start the server entrypoint first (for example `python -m better_together_server`) or update the client host settings."
        )

    return server, server.getPlayer()


def sync_remote_players(server, player_me, runtime, session_state, action_state=None):
    player_others = server.send(player_me, action_state=action_state)
    runtime.hit[:] = server.damage_markers
    runtime.enemy_projectiles[:] = server.enemy_projectiles
    runtime.player_projectiles[:] = server.player_projectiles
    session_state.apply_authoritative_state(server.gameplay_state)
    if player_others is None:
        return []

    return player_others


def resolve_repair_target(runtime, player_me):
    return resolve_repair_target_for_player(
        runtime.hit,
        player_x=player_me.x,
        player_y=player_me.y,
        player_width=player_me.width,
        player_height=player_me.height,
    )


def player_in_cannon_zone(player_me):
    return is_player_in_shared_cannon_zone(player_x=player_me.x, player_y=player_me.y)


def reset_cannon_aim(session_state, player_me):
    session_state.aim_y = player_me.y - player_me.height
    if 470 <= player_me.x <= 550:
        session_state.aim_x = player_me.x - 6 * player_me.width
    elif 760 <= player_me.x <= 840:
        session_state.aim_x = player_me.x + 6 * player_me.width


def calculate_prompt_progress(total_ticks, remaining_ticks):
    if total_ticks <= 0:
        return 0.0

    bounded_remaining_ticks = max(0, min(total_ticks, remaining_ticks))
    completed_ticks = total_ticks - bounded_remaining_ticks
    return completed_ticks / total_ticks


def move_player_and_track_hint(session_state, player_me):
    starting_position = (player_me.x, player_me.y)
    player_me.move()
    if (player_me.x, player_me.y) != starting_position:
        session_state.register_local_movement()


def draw_action_prompt(runtime, message, progress_ratio=0.0, icon=None, fill_color=RELOAD_PROGRESS_COLOR):
    progress_ratio = max(0.0, min(1.0, progress_ratio))
    prompt_surface = runtime.font.render(message, True, ACTION_PROMPT_TEXT_COLOR)
    bar_label_font = pygame.font.SysFont(None, ACTION_PROMPT_BAR_LABEL_FONT_SIZE)
    bar_label_surface = bar_label_font.render(ACTION_PROMPT_BAR_LABEL, True, ACTION_PROMPT_BAR_LABEL_COLOR)
    prompt_width = prompt_surface.get_width()
    prompt_height = prompt_surface.get_height()
    icon_width = 0 if icon is None else icon.get_width()
    icon_height = 0 if icon is None else icon.get_height()
    row_width = ACTION_PROMPT_BAR_WIDTH + (0 if icon is None else icon_width + ACTION_PROMPT_ICON_GAP)
    row_height = max(ACTION_PROMPT_BAR_HEIGHT, icon_height)
    content_width = max(prompt_width, row_width)
    content_left = (render.width - content_width) // 2
    row_y = render.height - ACTION_PROMPT_BOTTOM_MARGIN - row_height
    prompt_y = row_y - ACTION_PROMPT_STACK_GAP - prompt_height
    prompt_x = content_left + (content_width - prompt_width) // 2
    runtime.window.blit(prompt_surface, (prompt_x, prompt_y))

    row_x = content_left + (content_width - row_width) // 2
    icon_offset_x = 0
    if icon is not None:
        icon_y = row_y + (row_height - icon_height) // 2
        runtime.window.blit(icon, (row_x, icon_y))
        icon_offset_x = icon.get_width() + ACTION_PROMPT_ICON_GAP

    bar_rect = pygame.Rect(
        row_x + icon_offset_x,
        row_y + (row_height - ACTION_PROMPT_BAR_HEIGHT) // 2,
        ACTION_PROMPT_BAR_WIDTH,
        ACTION_PROMPT_BAR_HEIGHT,
    )
    pygame.draw.rect(runtime.window, ACTION_PROMPT_BACKGROUND_COLOR, bar_rect)

    if progress_ratio > 0:
        fill_rect = pygame.Rect(
            bar_rect.x,
            bar_rect.y,
            max(1, round(bar_rect.width * progress_ratio)),
            bar_rect.height,
        )
        pygame.draw.rect(runtime.window, fill_color, fill_rect)

    pygame.draw.rect(runtime.window, ACTION_PROMPT_BORDER_COLOR, bar_rect, 2)
    runtime.window.blit(
        bar_label_surface,
        (
            bar_rect.x + (bar_rect.width - bar_label_surface.get_width()) // 2,
            bar_rect.y + (bar_rect.height - bar_label_surface.get_height()) // 2,
        ),
    )


def update_game_over_overlay(runtime, session_state):
    if not session_state.authoritative_state.game_over:
        return True

    game_over_font = pygame.font.SysFont(None, 256)
    runtime.window.blit(
        game_over_font.render("Game Over", True, (255, 0, 0)),
        (render.width // 8, render.height // 2),
    )
    return session_state.authoritative_state.game_over_ticks_remaining > 0


def handle_repairs(runtime, session_state, player_me, frame_state, keys, action_state):
    repair_target = resolve_repair_target(runtime, player_me)
    if repair_target is None:
        return action_state

    if player_me.inventoryWood > 0:
        repair_ticks_remaining = session_state.authoritative_state.repair_duration_ticks
        repair_progress = 0.0
        if session_state.authoritative_state.repair_target == repair_target:
            repair_ticks_remaining = session_state.authoritative_state.repair_ticks_remaining
            repair_progress = calculate_prompt_progress(
                session_state.authoritative_state.repair_duration_ticks,
                repair_ticks_remaining,
            )

        draw_action_prompt(
            runtime,
            "Hold SPACE to repair",
            progress_ratio=repair_progress,
            icon=runtime.wood_icon,
            fill_color=REPAIR_PROGRESS_COLOR,
        )
        frame_state.repair_info_displayed = True
        if keys[pygame.K_SPACE]:
            action_state["repair_target"] = repair_target
        return action_state

    if not frame_state.shoot_info_displayed and not frame_state.repair_info_displayed:
        runtime.window.blit(
            runtime.font.render("No Wood", True, (255, 255, 255)),
            (render.width // 2 - 50, render.height - render.height // 12),
        )

    return action_state


def handle_cannon_controls(runtime, session_state, player_me, frame_state, keys, action_state):
    if player_in_cannon_zone(player_me):
        action_state["aim_target"] = (session_state.aim_x, session_state.aim_y)
        reload_ticks_remaining = session_state.authoritative_state.cannon_reload_ticks_remaining

        if player_me.inventoryCannon > 0 and reload_ticks_remaining <= 0 and not frame_state.repair_info_displayed:
            if keys[pygame.K_SPACE]:
                frame_state.shoot_info_displayed = True
                runtime.window.blit(
                    runtime.font.render("Release SPACE to shoot", True, (255, 255, 255)),
                    (render.width // 3 - 50, render.height - render.height // 12),
                )
                if (keys[ord("w")] or keys[pygame.K_UP]) and session_state.aim_y - session_state.aim_velocity > 0:
                    session_state.aim_y -= session_state.aim_velocity

                if (keys[ord("a")] or keys[pygame.K_LEFT]) and session_state.aim_x - session_state.aim_velocity > 0:
                    session_state.aim_x -= session_state.aim_velocity

                if (keys[ord("s")] or keys[pygame.K_DOWN]) and session_state.aim_y + session_state.aim_velocity < render.height:
                    session_state.aim_y += session_state.aim_velocity

                if (keys[ord("d")] or keys[pygame.K_RIGHT]) and session_state.aim_x + session_state.aim_velocity < render.width:
                    session_state.aim_x += session_state.aim_velocity

                action_state["aim_target"] = (session_state.aim_x, session_state.aim_y)
                runtime.window.blit(
                    runtime.aim,
                    (session_state.aim_x, session_state.aim_y),
                    (0, 0, render.width, render.height),
                )
                return action_state

            runtime.window.blit(
                runtime.font.render("Hold SPACE to use Cannon", True, (255, 255, 255)),
                (render.width // 3 - 50, render.height - render.height // 12),
            )
            move_player_and_track_hint(session_state, player_me)
            return action_state

        if reload_ticks_remaining > 0 and player_me.inventoryCannon > 0:
            if not frame_state.repair_info_displayed:
                draw_action_prompt(
                    runtime,
                    "Hold SPACE to reload",
                    progress_ratio=calculate_prompt_progress(
                        session_state.authoritative_state.cannon_reload_duration_ticks,
                        reload_ticks_remaining,
                    ),
                    icon=runtime.cannonball_icon,
                    fill_color=RELOAD_PROGRESS_COLOR,
                )
            reset_cannon_aim(session_state, player_me)
            action_state["aim_target"] = (session_state.aim_x, session_state.aim_y)
        elif not frame_state.repair_info_displayed:
            runtime.window.blit(
                runtime.font.render("No Ammo", True, (255, 255, 255)),
                (render.width // 2 - 50, render.height - render.height // 12),
            )

        move_player_and_track_hint(session_state, player_me)
        return action_state

    move_player_and_track_hint(session_state, player_me)
    if session_state.should_show_movement_hint() and not frame_state.shoot_info_displayed and not frame_state.repair_info_displayed:
        runtime.window.blit(runtime.font.render("Use WASD or Arrow Keys to MOVE", True, (255, 255, 255)), (render.width // 4 - 50, render.height - render.height // 12))

    return action_state


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
        session_state.apply_authoritative_state(server.gameplay_state)
        pending_action_state = session_state.create_action_state()

        while game:
            framerate.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game = False

            if not game:
                break

            player_others = sync_remote_players(
                server,
                player_me,
                runtime,
                session_state,
                action_state=pending_action_state,
            )

            render.refresh(runtime, player_me, player_others)
            keep_running = update_game_over_overlay(runtime, session_state)

            frame_state = session_state.begin_frame()
            keys = pygame.key.get_pressed()
            action_state = session_state.create_action_state(action_pressed=keys[pygame.K_SPACE])

            if not session_state.authoritative_state.game_over:
                action_state = handle_repairs(runtime, session_state, player_me, frame_state, keys, action_state)
                action_state = handle_cannon_controls(runtime, session_state, player_me, frame_state, keys, action_state)

            pending_action_state = action_state

            pygame.display.update()

            if not keep_running:
                game = False
    finally:
        if server is not None:
            server.close()
        render.shutdown_runtime(runtime)
        pygame.quit()


__all__ = ["main"]
