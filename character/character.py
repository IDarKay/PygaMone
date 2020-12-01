import pygame
import game

NPC_IMAGE = pygame.image.load("assets/textures/character/npc.png")

class Character(pygame.sprite.Sprite):

    def __init__(self, pos, size):
        super().__init__()
        self.size = size
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])

    def get_render_coord(self, scroll):
        return self.rect.x-scroll[0], self.rect.y-scroll[1]

    def set_render_from_scroll(self, scroll, coord):
        self.rect.x = coord[0] + scroll[0]
        self.rect.y = coord[1] + scroll[1]

    def get_image(self):
        raise RuntimeError("get_image need be redefine")

    def render(self, display):
        display.blit(self.get_image(), self.get_render_coord(game.came_scroll))

    def get_render_x(self):
        return self.get_render_coord(game.came_scroll)[0]

    def get_render_y(self):
        return self.get_render_coord(game.came_scroll)[1]

    def set_pos(self, coord):
        self.rect.x, self.rect.y = coord

    def get_box(self):
        """

        :rtype: collision.SquaredCollisionBox
        """
        s_coord = self.get_render_coord(game.came_scroll)
        return game.collision.SquaredCollisionBox(s_coord[0], s_coord[1], s_coord[0] + self.size[0], s_coord[1] + self.size[1])


def get_part(image, coord, transform=(0, 0)):
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