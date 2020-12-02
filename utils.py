import time
import pygame
from typing import Tuple


def current_milli_time() -> int:
    return int(round(time.time() * 1000))


def time_to_string(t: int) -> str:
    hours = t // (60 * 60)
    t -= hours * (60 * 60)
    minutes = t // 60
    t -= minutes * 60
    return str(hours) + ":" + ("0" if minutes < 9 else "") + str(minutes)


def draw_rond_rectangle(display: pygame.Surface, _x, _y, height, width, color):
    height *= 0.5
    pygame.draw.circle(display, color, (_x, _y + height), height)
    pygame.draw.circle(display, color, (_x + width, _y + height), height)
    pygame.draw.rect(display, color, pygame.Rect(_x, _y, width, height * 2))


def draw_progress_bar(display: pygame.Surface, coord: Tuple[float, float], size: Tuple[float, float],
                      bg_color: Tuple[int, int, int], color: Tuple[int, int, int], progress: float):

    pygame.draw.rect(display, bg_color, pygame.Rect(coord[0], coord[1], size[0], size[1]))
    pygame.draw.rect(display, color, pygame.Rect(coord[0], coord[1], size[0] * progress , size[1]))