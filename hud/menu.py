import pygame
import character.character as chr
import game
import character.player as pl

MENU_IMAGE = pygame.image.load("assets/textures/hud/menu.png")
SURFACE_SIZE = (530, 300)


class Menu(object):

    def __init__(self, player):
        """
        :type player: character.player.Player
        """
        self.player = player

    def on_key_x(self, value, press):
        pass

    def on_key_y(self, value, press):
        pass

    def on_key_action(self):
        pass

    def render(self, display):
        """
        :type display: pygame.Surface
        """
        pass


x = SURFACE_SIZE[0]
y = SURFACE_SIZE[1] - 10
poly_1 = (
    (0, 0),
    (int(x * 0.1), 0),
    (0, int(y * 0.5)))
poly_2 = (
    (int(x * 0.1), 0),
    (int(x * 0.2), 0),
    (0, y),
    (0, int(y * 0.5))
)
poly_3 = (
    (int(x * 0.2), 0),
    (x, 0),
    (int(x * 0.8), y),
    (0, y)
)
poly_4 = (
    (x, 0),
    (x, int(y * 0.5)),
    (int(x * 0.9), y),
    (int(x * 0.8), y)
)
poly_5 = (
    (x, int(y * 0.5)),
    (x, y),
    (int(x * 0.9), y),
)

centre_circle = (
    (int(x * 0.3), int(y * 0.2)),
    (int(x * 0.5), int(y * 0.2)),
    (int(x * 0.7), int(y * 0.2)),
    (int(x * 0.3), int(y * 0.6)),
    (int(x * 0.5), int(y * 0.6))
)

poly_6 = (
    (int(x * 0.2), int(y * 0.85)),
    (int(x * 0.25), int(y * 0.85)),
    (int(x * 0.2), int(y * 0.98))
)

poly_7 = (
    (int(x * 0.25), int(y * 0.85)),
    (int(x * 0.8), int(y * 0.85)),
    (int(x * 0.75), int(y * 0.98)),
    (int(x * 0.2), int(y * 0.98))
)

poly_8 = (
    (int(x * 0.8), int(y * 0.85)),
    (int(x * 0.8), int(y * 0.98)),
    (int(x * 0.750), int(y * 0.98))
)

class MainMenu(Menu):

    def __init__(self, player):
        super().__init__(player)
        coord = (
            (0, 0, 64, 64),
            (64, 0, 128, 64),
            (256, 0, 320, 64),
            (128, 0, 195, 64),
            (192, 0, 256, 64)
        )
        self.image = [chr.get_part(MENU_IMAGE, c) for c in coord]
        self.arrow = chr.get_part(MENU_IMAGE, (0, 64, 22, 91))
        self.selected = 0
        self.text = [game.get_game_instance().get_message(t).upper() for t in ["pokemon", "bag", "map", "save", "options"]]

    def render(self, display):
        pygame.draw.polygon(display, (239, 226, 235), poly_1)
        pygame.draw.polygon(display, (206, 51, 65), poly_2)
        pygame.draw.polygon(display, (241, 65, 78), poly_3)
        pygame.draw.polygon(display, (206, 51, 65), poly_4)
        pygame.draw.polygon(display, (239, 226, 235), poly_5)
        pygame.draw.polygon(display, (40, 35, 32), poly_6)
        pygame.draw.polygon(display, (50, 50, 50), poly_7)
        pygame.draw.polygon(display, (40, 35, 32), poly_8)

        info = game.FONT.render("todo: information here and back to line", True, (255, 255, 255))
        display.blit(info, (int(SURFACE_SIZE[0] * 0.25), int(SURFACE_SIZE[1] * 0.85)))

        for i in range(len(centre_circle)):
            c = centre_circle[i]
            if self.selected == i:
                pygame.draw.circle(display, (0, 0, 0), c, 40)
                display.blit(self.arrow, (c[0] - 51, c[1] - 13))
            else:
                pygame.draw.circle(display, (255, 255, 255), c, 40)
            display.blit(self.image[i], (c[0] - 32, c[1] - 32))
            t_i = game.FONT.render(self.text[i], True, (255, 255, 255))
            x_min = (len(self.text[i]) / 2) * game.FONT_SIZE[0]
            display.blit(t_i, (c[0] - x_min, c[1] + 45))


    def on_key_x(self, value, press):
        if value < 0 and press:
            if self.selected > 0:
                self.selected -= 1
        elif value > 0 and press:
            if self.selected < 5:
                self.selected += 1

    def on_key_y(self, value, press):
        if value < 0 and press:
            if self.selected - 3 >= 0:
                self.selected -= 3
        elif value > 0 and press:
            if self.selected + 3 <= 4:
                self.selected += 3

    def on_key_action(self):
        print(self.selected)
        if self.selected == 3:
            self.player.open_menu(SaveMenu(self.player))

x = SURFACE_SIZE[0]
y = SURFACE_SIZE[1]

s_poly_1 = (
    (0, 0),
    (int(x * 0.45), 0),
    (int(x * 0.25), y),
    (0, y)
)

s_poly_2 = (
    (int(x * 0.45), 0),
    (int(x * 0.55), 0),
    (int(x * 0.35), y),
    (int(x * 0.25), y)
)

class SaveMenu(Menu):

    def __init__(self, player):
        super().__init__(player)
        self.selected = 0
        self.arrow = chr.get_part(MENU_IMAGE, (0, 64, 22, 91), (12, 14))
        self.text = [game.get_game_instance().get_message(t) for t in ["save_game", "back"]]

    def render(self, display):
        display.fill((55, 193, 193))
        pygame.draw.polygon(display, (225, 223, 234), s_poly_1)
        pygame.draw.polygon(display, (51, 171, 169), s_poly_2)

        x = SURFACE_SIZE[0] * 0.6
        y = SURFACE_SIZE[1] * 0.75

        for i in range(2):

            color = (0, 0, 0) if self.selected == i else (255, 255, 255)
            tex_color = (255, 255, 255) if self.selected == i else (0, 0, 0)
            pygame.draw.circle(display, color, (x + 10, y + SURFACE_SIZE[1] * 0.025), SURFACE_SIZE[1] * 0.025)
            pygame.draw.circle(display, color, (x + 10 + SURFACE_SIZE[0] * 0.3, y + SURFACE_SIZE[1] * 0.025), SURFACE_SIZE[1] * 0.025)
            pygame.draw.rect(display, color, pygame.Rect(x + 10, y, SURFACE_SIZE[0] * 0.3, SURFACE_SIZE[1] * 0.05))

            t_i = game.FONT.render(self.text[i], True, tex_color)
            x_min = (len(self.text[i]) / 2) * game.FONT_SIZE[0]
            display.blit(t_i, (x + 20 + (SURFACE_SIZE[0] * 0.3) / 2 - x_min, y + 2))

            if self.selected == i:
                display.blit(self.arrow, (x - 10, y))
            y += SURFACE_SIZE[1] * 0.07

    def on_key_y(self, value, press):
        if value < 0 and press:
            if self.selected > 0:
                self.selected -= 1
        elif value > 0 and press:
            if self.selected < 1:
                self.selected += 1

    def on_key_action(self):
        if self.selected == 0:
            game.get_game_instance().save()
            self.player.close_menu()
        else:
            self.player.open_menu(MainMenu(self.player))
