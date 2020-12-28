from typing import Tuple, NoReturn
import pygame
import game

NPC_IMAGE = pygame.image.load("assets/textures/character/npc.png")


class Character:

    def __init__(self, pos: Tuple[int, int], size: Tuple[int, int]):
        # super().__init__()
        self.size = size
        self.rect = pygame.Rect(pos[0] * game.CASE_SIZE, pos[1] * game.CASE_SIZE, size[0], size[1])

    def get_render_coord(self, scroll: Tuple[int, int]) -> Tuple[int, int]:
        return self.rect.x-scroll[0], self.rect.y-scroll[1]

    def set_render_from_scroll(self, scroll: Tuple[int, int], coord: Tuple[int, int]):
        self.rect.x = coord[0] + scroll[0]
        self.rect.y = coord[1] + scroll[1]

    def get_image(self) -> pygame.Surface:
        raise RuntimeError("get_image need be redefine")

    def render(self, display: pygame.Surface):
        display.blit(self.get_image(), self.get_render_coord(game.came_scroll))

    def get_render_x(self) -> int:
        return self.get_render_coord(game.came_scroll)[0]

    def get_render_y(self) -> int:
        return self.get_render_coord(game.came_scroll)[1]

    def set_pos(self, coord: Tuple[float, float]):
        self.rect.x, self.rect.y = int(coord[0] * game.CASE_SIZE), int(coord[1] * game.CASE_SIZE)

    def get_pos(self) -> Tuple[float, float]:
        return self.rect.x / game.CASE_SIZE, self.rect.y / game.CASE_SIZE

    def get_absolute_pose(self) -> Tuple[int, int]:
        return self.rect.x, self.rect.y

    def get_box(self) -> NoReturn:
        s_coord = self.get_render_coord(game.came_scroll)
        return game.collision.SquaredCollisionBox(s_coord[0], s_coord[1], s_coord[0] + self.size[0], s_coord[1] + self.size[1])