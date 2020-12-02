import pygame
import game
import collision
import typing

NPC_IMAGE = pygame.image.load("assets/textures/character/npc.png")


class Character(pygame.sprite.Sprite):

    def __init__(self, pos: typing.Tuple[int, int], size: typing.Tuple[int, int]):
        super().__init__()
        self.size = size
        self.rect = pygame.Rect(pos[0] * game.CASE_SIZE, pos[1] * game.CASE_SIZE, size[0], size[1])

    def get_render_coord(self, scroll: typing.Tuple[int, int]) -> typing.Tuple[int, int]:
        return self.rect.x-scroll[0], self.rect.y-scroll[1]

    def set_render_from_scroll(self, scroll: typing.Tuple[int, int], coord: typing.Tuple[int, int]):
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

    def set_pos(self, coord: typing.Tuple[float, float]):
        self.rect.x, self.rect.y = int(coord[0] * game.CASE_SIZE), int(coord[1] * game.CASE_SIZE)

    def get_pos(self) -> typing.Tuple[float, float]:
        return self.rect.x / game.CASE_SIZE, self.rect.y / game.CASE_SIZE

    def get_absolute_pose(self) -> typing.Tuple[int, int]:
        return self.rect.x, self.rect.y

    def get_box(self):
        s_coord = self.get_render_coord(game.came_scroll)
        return game.collision.SquaredCollisionBox(s_coord[0], s_coord[1], s_coord[0] + self.size[0], s_coord[1] + self.size[1])


def get_part(image: pygame.Surface, coord: typing.Tuple[float, float, float, float], transform: typing.Tuple[int, int] = (0, 0)) -> pygame.Surface:
    s = pygame.Surface((coord[2] - coord[0], coord[3] - coord[1]), pygame.SRCALPHA)
    s.blit(image, (0, 0), pygame.Rect(coord))
    if transform != (0, 0):
        copy_transform = [transform[0], transform[1]]
        if copy_transform[0] == -1:
            copy_transform[0] = coord[2] - coord[0]
        if copy_transform[1] == -1:
            copy_transform[1] = coord[3] - coord[1]
        transform = int(copy_transform[0]), int(copy_transform[1])
        return pygame.transform.scale(s, transform)
    return s