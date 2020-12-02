import pygame
import character.character as chr
import game
from datetime import datetime
from typing import Tuple
import time
from utils import *
import character.player as pl

MENU_IMAGE = pygame.image.load("assets/textures/hud/menu.png")
SURFACE_SIZE = (1060, 600)


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

    def on_key_escape(self):
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
        self.text = [game.get_game_instance().get_message(t).upper() for t in
                     ["pokemon", "bag", "map", "save", "options"]]

    def render(self, display):
        pygame.draw.polygon(display, (239, 226, 235), poly_1)
        pygame.draw.polygon(display, (206, 51, 65), poly_2)
        pygame.draw.polygon(display, (241, 65, 78), poly_3)
        pygame.draw.polygon(display, (206, 51, 65), poly_4)
        pygame.draw.polygon(display, (239, 226, 235), poly_5)
        pygame.draw.polygon(display, (40, 35, 32), poly_6)
        pygame.draw.polygon(display, (50, 50, 50), poly_7)
        pygame.draw.polygon(display, (40, 35, 32), poly_8)

        info = game.FONT_16.render("todo: information here and back to line", True, (255, 255, 255))
        display.blit(info, (int(SURFACE_SIZE[0] * 0.25), int(SURFACE_SIZE[1] * 0.85)))

        for i in range(len(centre_circle)):
            c = centre_circle[i]
            if self.selected == i:
                pygame.draw.circle(display, (0, 0, 0), c, 40)
                display.blit(self.arrow, (c[0] - 51, c[1] - 13))
            else:
                pygame.draw.circle(display, (255, 255, 255), c, 40)
            display.blit(self.image[i], (c[0] - 32, c[1] - 32))
            t_i = game.FONT_16.render(self.text[i], True, (255, 255, 255))
            x_min = (len(self.text[i]) / 2) * game.FONT_SIZE_16[0]
            display.blit(t_i, (c[0] - x_min, c[1] + 45))

    def on_key_x(self, value, press):
        if value < 0 and press:
            if self.selected > 0:
                self.selected -= 1
        elif value > 0 and press:
            if self.selected < 4:
                self.selected += 1

    def on_key_y(self, value, press):
        if value < 0 and press:
            if self.selected - 3 >= 0:
                self.selected -= 3
        elif value > 0 and press:
            if self.selected + 3 <= 4:
                self.selected += 3

    def on_key_escape(self):
        self.player.close_menu()

    def on_key_action(self):
        if self.selected == 3:
            self.player.open_menu(SaveMenu(self.player))
        elif self.selected == 0:
            self.player.open_menu(TeamMenu(self.player))


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
        self.text_2 = [
            game.FONT_16.render(game.get_game_instance().get_message(t) + " :", True, (0, 0, 0)) for t in
            ["date_hour", "actual_position", "time_play", "pokedex", ]]
        self.last_save_f = game.FONT_16.render(game.get_game_instance().get_message("last_save"), True, (255, 255, 255))
        self.last_save_size = game.FONT_SIZE_16[0] * len(game.get_game_instance().get_message("last_save"))
        self.time_play = game.FONT_16.render(time_to_string(game.get_game_instance().get_save_value("time_played", 0)),
                                             True, (0, 0, 0))
        # todo: pokedex n
        self.pokedex = game.FONT_16.render("0", True, (0, 0, 0))
        self.last_save = game.FONT_16.render(
            str(datetime.fromtimestamp(game.get_game_instance().get_save_value("last_save", 0))
                .strftime('%d/%m/%y  %H:%M')), True, (255, 255, 255))
        self.open_time = time.time()

    def render(self, display):
        if time.time() - self.open_time < 0.2:
            display.fill((255, 255, 255))
        else:
            display.fill((55, 193, 193))
            pygame.draw.polygon(display, (225, 223, 234), s_poly_1)
            pygame.draw.polygon(display, (51, 171, 169), s_poly_2)

            _x = SURFACE_SIZE[0] * 0.55
            _y = SURFACE_SIZE[1] * 0.38

            for i in range(4):
                display.blit(self.text_2[i], (_x, _y))
                _y += SURFACE_SIZE[1] * 0.07

            _x = SURFACE_SIZE[0] * 0.76
            _y = SURFACE_SIZE[1] * 0.38

            time_f = game.FONT_16.render(str(datetime.fromtimestamp(time.time()).strftime('%d/%m/%y %H:%M')), True,
                                         (0, 0, 0))
            display.blit(time_f, (_x, _y))
            _y += SURFACE_SIZE[1] * 0.07
            display.blit(game.FONT_16.render(game.get_game_instance().level.get_translate_name(), True, (0, 0, 0)),
                         (_x, _y))
            _y += SURFACE_SIZE[1] * 0.07
            display.blit(self.time_play, (_x, _y))
            _y += SURFACE_SIZE[1] * 0.07
            display.blit(self.pokedex, (_x, _y))

            display.blit(self.last_save_f, (SURFACE_SIZE[0] * 0.85 - self.last_save_size, SURFACE_SIZE[1] * 0.95))
            display.blit(self.last_save, (SURFACE_SIZE[0] * 0.86, SURFACE_SIZE[1] * 0.95))

            _x = SURFACE_SIZE[0] * 0.6
            _y = SURFACE_SIZE[1] * 0.75

            for i in range(2):

                color = (0, 0, 0) if self.selected == i else (255, 255, 255)
                tex_color = (255, 255, 255) if self.selected == i else (0, 0, 0)
                pygame.draw.circle(display, color, (_x + 10, _y + SURFACE_SIZE[1] * 0.025), SURFACE_SIZE[1] * 0.025)
                pygame.draw.circle(display, color, (_x + 10 + SURFACE_SIZE[0] * 0.3, _y + SURFACE_SIZE[1] * 0.025),
                                   SURFACE_SIZE[1] * 0.025)
                pygame.draw.rect(display, color,
                                 pygame.Rect(_x + 10, _y, SURFACE_SIZE[0] * 0.3, SURFACE_SIZE[1] * 0.05))

                t_i = game.FONT_16.render(self.text[i], True, tex_color)
                x_min = (len(self.text[i]) / 2) * game.FONT_SIZE_16[0]
                display.blit(t_i, (_x + 10 + (SURFACE_SIZE[0] * 0.3) / 2 - x_min, _y + 6))

                if self.selected == i:
                    display.blit(self.arrow, (_x - 10, _y))
                _y += SURFACE_SIZE[1] * 0.07

    def on_key_y(self, value, press):
        if value < 0 and press:
            if self.selected > 0:
                self.selected -= 1
        elif value > 0 and press:
            if self.selected < 1:
                self.selected += 1

    def on_key_escape(self):
        self.player.open_menu(MainMenu(self.player))

    def on_key_action(self):
        if self.selected == 0:
            game.get_game_instance().save()
            self.player.close_menu()
        else:
            self.player.open_menu(MainMenu(self.player))


x = SURFACE_SIZE[0]
y = SURFACE_SIZE[1]

t_poly_1 = (
    (0, 0),
    (int(x * 0.5), 0),
    (int(x * 0.30), y),
    (0, y),
)
t_poly_2 = (
    (int(x * 0.5), 0),
    (int(x * 0.6), 0),
    (int(x * 0.4), y),
    (int(x * 0.30), y),
)


class TeamMenu(Menu):
    def __init__(self, player):
        super().__init__(player)
        self.selected = 0
        self.arrow = chr.get_part(MENU_IMAGE, (0, 64, 22, 91), (33, 41))
        self.open_time = current_milli_time()
        self.progress = []
        self.display_small = []
        self.display_large = []
        self.text = []
        for poke in self.player.team:
            if not poke:
                break
            heal = poke.heal, poke.get_max_heal()
            self.progress.append(heal)
            self.display_small.append(pygame.transform.scale(poke.poke.display.get_image(), (40, 40)))
            self.display_large.append(pygame.transform.scale(poke.poke.display.get_image(), (512, 512)))
            self.text.append([
                game.FONT_16.render("{}/{}".format(heal[0], heal[1]), True, (0, 0, 0)),
                game.FONT_16.render("{}/{}".format(heal[0], heal[1]), True, (255, 255, 255)),
                game.FONT_24.render("N.{}".format(poke.lvl), True, (0, 0, 0)),
                game.FONT_24.render("N.{}".format(poke.lvl), True, (255, 255, 255)),
                game.FONT_20.render(poke.get_name(True), True, (0, 0, 0)),
                game.FONT_20.render(poke.get_name(True), True, (255, 255, 255)),
            ])


    def render(self, display):
        display.fill((255, 255, 255))
        pygame.draw.polygon(display, (241, 65, 78), t_poly_1)
        pygame.draw.polygon(display, (206, 51, 65), t_poly_2)

        _x = SURFACE_SIZE[0] * 0.1
        _y = SURFACE_SIZE[1] * 0.1

        _time = current_milli_time() - self.open_time
        part_time = _time % 2000
        poke_y = 0
        if part_time < 900:
            poke_y = 0
        elif part_time < 950 or 1950 <= part_time:
            poke_y = 1
        elif part_time < 1000 or 1900 <= part_time:
            poke_y = 3
        elif part_time < 1900:
            poke_y = 5

        for i in range(len(self.progress)):

            color, start = ((0, 0, 0), 1) if self.selected == i else ((255, 255, 255), 0)
            draw_rond_rectangle(display, _x, _y, SURFACE_SIZE[1] * 0.08, SURFACE_SIZE[0] * 0.2, color)
            xp = self.progress[i]
            _x2 = SURFACE_SIZE[1] * 0.04
            text = self.text[i]
            # todo: change  for heal and no xp
            draw_progress_bar(display,
                              (_x + _x2, _y + SURFACE_SIZE[0] * 0.02),
                              (SURFACE_SIZE[1] * 0.28, 5),
                              (52, 56, 61), (45, 181, 4), xp[0] / xp[1])

            display.blit(self.display_small[i], (_x - 15, _y + 6 - poke_y))

            # display heal
            # todo: change  for heal and no xp
            display.blit(text[start], (_x + _x2, _y + SURFACE_SIZE[0] * 0.028))
            # display lvl
            display.blit(text[start + 2], (_x + _x2 + SURFACE_SIZE[1] * 0.25, _y + SURFACE_SIZE[0] * 0.025))
            # dismay name
            display.blit(text[start + 4], (_x + _x2, _y + 2))



            # tex_color = (255, 255, 255) if self.selected == i else (0, 0, 0)
            # t_i = game.FONT_16.render(self.text[i], True, tex_color)
            # x_min = (len(self.text[i]) / 2) * game.FONT_SIZE_16[0]
            # display.blit(t_i, (_x + 10 + (SURFACE_SIZE[0] * 0.3) / 2 - x_min, _y + 6))

            if self.selected == i:
                display.blit(self.arrow, (_x - 50, _y + 2))
                display.blit(self.display_large[i], (SURFACE_SIZE[0] * 0.5, SURFACE_SIZE[1] * 0.2))
            _y += SURFACE_SIZE[1] * 0.15

    def on_key_escape(self):
        self.player.open_menu(MainMenu(self.player))

    def on_key_y(self, value, press):
        if value < 0 and press:
            if self.selected > 0:
                self.selected -= 1
        elif value > 0 and press:
            if self.selected < len(self.progress) - 1:
                self.selected += 1

    def on_key_action(self):
        pass






