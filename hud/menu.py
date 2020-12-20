from typing import NoReturn
from hud.menu_calass import Menu
from datetime import datetime
import pygame
import game
import utils
import time
import sounds
import sound_manager
import hud.pokedex as menu_pokedex
import option

SURFACE_SIZE = (1060, 600)

x = SURFACE_SIZE[0]
y = SURFACE_SIZE[1] - 30
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
    (int(x * 0.5), int(y * 0.6)),
    (int(x * 0.7), int(y * 0.6))
)

class MainMenu(Menu):

    def __init__(self, player):
        super().__init__(player)
        coord = (
            (320, 0, 684, 64),
            (0, 0, 64, 64),
            (64, 0, 128, 64),
            (256, 0, 320, 64),
            (128, 0, 195, 64),
            (192, 0, 256, 64)
        )
        self.image = [utils.get_part_i(utils.MENU_IMAGE, c) for c in coord]
        # self.arrow = utils.get_part_i(MENU_IMAGE, (0, 64, 22, 91))
        self.arrow = utils.ARROW
        self.selected = 0
        self.text = [game.get_game_instance().get_message(t).upper() for t in
                     ["pokedex", "pokemon", "bag", "map", "save", "options"]]
        self.keys = {
            game.get_game_instance().get_message("back"): option.KEY_QUITE,
            game.get_game_instance().get_message("save"): option.KEY_BIKE,
            game.get_game_instance().get_message("select"): option.KEY_ACTION
        }

    def render(self, display):
        pygame.draw.polygon(display, (239, 226, 235), poly_1)
        pygame.draw.polygon(display, (206, 51, 65), poly_2)
        pygame.draw.polygon(display, (241, 65, 78), poly_3)
        pygame.draw.polygon(display, (206, 51, 65), poly_4)
        pygame.draw.polygon(display, (239, 226, 235), poly_5)

        # pygame.draw.polygon(display, (40, 35, 32), poly_6)
        # pygame.draw.polygon(display, (50, 50, 50), poly_7)
        # pygame.draw.polygon(display, (40, 35, 32), poly_8)

        utils.draw_button_info(display, **self.keys)

        # info = game.FONT_16.render("todo: information here and back to line", True, (255, 255, 255))
        # display.blit(info, (int(SURFACE_SIZE[0] * 0.25), int(SURFACE_SIZE[1] * 0.85)))

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
            if self.selected < 5:
                self.selected += 1

    def on_key_y(self, value, press):
        if value < 0 and press:
            if self.selected - 3 >= 0:
                self.selected -= 3
        elif value > 0 and press:
            if self.selected + 3 <= 5:
                self.selected += 3

    def on_key_bike(self) -> NoReturn:
        sound_manager.start_in_first_empty_taunt(pygame.mixer.Sound(sounds.SAVE.path))
        game.get_game_instance().save()
        self.player.close_menu()

    def on_key_escape(self):
        self.player.close_menu()

    def on_key_menu(self) -> NoReturn:
        self.player.close_menu()

    def on_key_action(self):
        sound_manager.start_in_first_empty_taunt(sounds.PLINK)
        if self.selected == 4:
            self.player.open_menu(SaveMenu(self.player))
        elif self.selected == 1:
            self.player.open_menu(TeamMenu(self.player))
        elif self.selected == 0:
            self.player.open_menu(menu_pokedex.PokeDex(self.player))


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
        # self.arrow = utils.get_part_i(MENU_IMAGE, (0, 64, 22, 91), (12, 14))
        self.arrow = utils.ARROW
        self.text = [game.get_game_instance().get_message(t) for t in ["save_game", "back"]]
        self.text_2 = [
            game.FONT_16.render(game.get_game_instance().get_message(t) + " :", True, (0, 0, 0)) for t in
            ["date_hour", "actual_position", "time_play", "pokedex", ]]
        self.last_save_f = game.FONT_16.render(game.get_game_instance().get_message("last_save"), True, (255, 255, 255))
        self.last_save_size = game.FONT_SIZE_16[0] * len(game.get_game_instance().get_message("last_save"))
        self.time_play = game.FONT_16.render(utils.time_to_string(game.get_game_instance().get_save_value("time_played", 0)),
                                             True, (0, 0, 0))
        # todo: pokedex n
        self.pokedex = game.FONT_16.render(str(sum(map(game.POKEDEX_CATCH.__eq__, game.get_game_instance().get_pokedex_catch_status_values()))), True, (0, 0, 0))
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
            sound_manager.start_in_first_empty_taunt(pygame.mixer.Sound(sounds.SAVE.path))
            game.get_game_instance().save()
            self.player.close_menu()
        else:
            self.player.open_menu(MainMenu(self.player))


class TeamMenu(Menu):

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

    def __init__(self, player):
        super().__init__(player)

        self.selected = 0
        self.action_selected = -1
        self.move = -1
        self.keys = {
            game.get_game_instance().get_message("back"): option.KEY_QUITE,
            game.get_game_instance().get_message("move_pokemon"): option.KEY_BIKE,
            game.get_game_instance().get_message("select"): option.KEY_ACTION
        }
        # self.arrow = utils.get_part_i(MENU_IMAGE, (0, 64, 22, 91), (33, 41))
        self.arrow = utils.ARROW
        self.open_time = utils.current_milli_time()
        self.progress = []
        self.display_small = []
        self.display_large = []
        self.text = []
        self.poke_ball = []
        self.text_2 = [(game.FONT_20.render(game.get_game_instance().get_message(t), True, (0, 0, 0)),
                        game.FONT_20.render(game.get_game_instance().get_message(t), True, (255, 255, 255)))
                       for t in ["summary", "move", "heal", "object", "back"]]
        for poke in self.player.team:
            if not poke:
                break
            heal = poke.heal, poke.get_max_heal()
            self.progress.append(heal)
            self.display_small.append(poke.get_front_image(0.5))
            self.display_large.append(poke.get_front_image(4))
            self.text.append([
                game.FONT_16.render("{}/{}".format(heal[0], heal[1]), True, (0, 0, 0)),
                game.FONT_16.render("{}/{}".format(heal[0], heal[1]), True, (255, 255, 255)),
                game.FONT_24.render("N.{}".format(poke.lvl), True, (0, 0, 0)),
                game.FONT_24.render("N.{}".format(poke.lvl), True, (255, 255, 255)),
                game.FONT_20.render(poke.get_name(True), True, (0, 0, 0)),
                game.FONT_20.render(poke.get_name(True), True, (255, 255, 255)),
            ])
            self.poke_ball.append(pygame.transform.scale(poke.poke_ball.image, (16, 16)))

    def render(self, display):
        display.fill((255, 255, 255))
        pygame.draw.polygon(display, (241, 65, 78), TeamMenu.t_poly_1)
        pygame.draw.polygon(display, (206, 51, 65), TeamMenu.t_poly_2)
        pygame.draw.rect(display, (0, 0, 0), (0, 570, 1060, 30))
        g_x = SURFACE_SIZE[0] * 0.1
        g_y = SURFACE_SIZE[1] * 0.1

        _time = utils.current_milli_time() - self.open_time
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

            if self.move != i:
                self.draw_pokemon(display, i, g_x, g_y, poke_y)
            g_y += SURFACE_SIZE[1] * 0.15

        # draw move
        if self.move != -1:
            self.draw_pokemon(display, self.move, g_x + SURFACE_SIZE[0] * 0.04, self.selected * SURFACE_SIZE[1] * 0.15 + SURFACE_SIZE[1] * 0.05, poke_y)

        # action hud
        if self.action_selected != -1:
            _y = SURFACE_SIZE[1] * 0.13 + SURFACE_SIZE[1] * 0.15 * self.selected
            _x = SURFACE_SIZE[0] * 0.31
            utils.draw_select_box(display, _x, _y, self.text_2, self.action_selected, 100)

        utils.draw_button_info(display, **self.keys)

    def draw_pokemon(self, display: pygame.Surface, i: int, _x: float, _y: float, poke_y: int):
        color, start = ((0, 0, 0), 1) if self.selected == i else ((255, 255, 255), 0)
        utils.draw_rond_rectangle(display, _x, _y, 49, 212, color)
        xp = self.progress[i]
        _x2 = SURFACE_SIZE[1] * 0.04
        text = self.text[i]
        utils.draw_progress_bar(display,
                          (_x + _x2, _y + 21),
                          (SURFACE_SIZE[1] * 0.28, 5),
                          (52, 56, 61), (45, 181, 4), xp[0] / xp[1])

        display.blit(self.display_small[i], (_x - 20, _y + 4 - poke_y))

        # display heal
        display.blit(text[start], (_x + _x2, _y + SURFACE_SIZE[0] * 0.028))
        # display lvl
        display.blit(text[start + 2], (_x + _x2 + SURFACE_SIZE[1] * 0.24, _y + SURFACE_SIZE[0] * 0.024))
        # display name
        display.blit(text[start + 4], (_x + _x2, _y + 2))
        # display pokeball
        display.blit(self.poke_ball[i], (_x + _x2 + SURFACE_SIZE[1] * 0.3, _y + 5))
        # display status
        poke = self.player.team[i]
        if poke:
            im = poke.combat_status.get_all_image()
            if len(im) > 0:
                current = im[min(utils.current_milli_time() % (len(im) * 2000) // 2000, len(im) - 1)]
                utils.draw_rond_rectangle(display, _x + 105, _y + 31, 12, 50, current[1])
                display.blit(tx := game.FONT_12.render(current[0], True, (255, 255, 255)),
                             (_x + 130 - tx.get_size()[0] // 2, _y + 37 - tx.get_size()[1] // 2))

        if self.selected == i:
            display.blit(self.arrow, (_x - 50, _y + 2))
            display.blit(self.display_large[i], (SURFACE_SIZE[0] * 0.5, SURFACE_SIZE[1] * 0.2))

    def on_key_escape(self):
        if self.action_selected != -1:
            self.action_selected = -1
        else:
            self.player.open_menu(MainMenu(self.player))

    def on_key_bike(self) -> NoReturn:
        if self.move != -1:
            if self.selected == self.move:
                self.move = -1
            else:
                self.player.switch_pokemon(self.move, self.selected)
                # reopen to actualise data
                self.player.open_menu(TeamMenu(self.player))
        else:
            self.move, self.action_selected = self.selected, -1

    def on_key_y(self, value, press):
        if value < 0 and press:
            if self.action_selected != -1:
                if self.action_selected > 0:
                    self.action_selected -= 1
            elif self.selected > 0:
                self.selected -= 1
        elif value > 0 and press:
            if self.action_selected != -1:
                if self.action_selected < 4:
                    self.action_selected += 1
            elif self.selected < len(self.progress) - 1:
                self.selected += 1

    def on_key_action(self):
        if self.move != -1:
            if self.selected == self.move:
                self.move = -1
            else:
                self.player.switch_pokemon(self.move, self.selected)
                # reopen to actualise data
                self.player.open_menu(TeamMenu(self.player))
        elif self.action_selected == -1:
            sound_manager.start_in_first_empty_taunt(sounds.PLINK)
            self.action_selected = 0
        else:
            if self.action_selected != 4:
                sound_manager.start_in_first_empty_taunt(sounds.PLINK)
            if self.action_selected == 0:
                self.player.open_menu(StatusMenu(self.player, self.selected))
            elif self.action_selected == 1:
                self.move, self.action_selected = self.selected, -1
            elif self.action_selected == 2:
                # todo heal
                pass
            elif self.action_selected == 3:
                # todo object
                pass
            elif self.action_selected == 4:
                self.action_selected = -1


class StatusMenu(Menu):

    x = SURFACE_SIZE[0]
    y = SURFACE_SIZE[1]

    st_poly_1 = (
        (0, 0),
        (SURFACE_SIZE[0] * 0.43, 0),
        (SURFACE_SIZE[0] * 0.23, y),
        (0, y)
    )

    st_poly_2 = (
        (SURFACE_SIZE[0] * 0.43, 0),
        (SURFACE_SIZE[0] * 0.5, 0),
        (SURFACE_SIZE[0] * 0.3, y),
        (SURFACE_SIZE[0] * 0.23, y)
    )

    st_poly_3 = (
        (SURFACE_SIZE[0] * 0.55, SURFACE_SIZE[1] * 0.05),
        (x, SURFACE_SIZE[1] * 0.05),
        (x, SURFACE_SIZE[1] * 0.1),
        (SURFACE_SIZE[0] * 0.54, SURFACE_SIZE[1] * 0.1)
    )

    st_arrow_1 = (
        (SURFACE_SIZE[0] * 0.555, SURFACE_SIZE[1] * 0.045),
        (SURFACE_SIZE[0] * 0.575, SURFACE_SIZE[1] * 0.045),
        (SURFACE_SIZE[0] * 0.565, SURFACE_SIZE[1] * 0.032),
    )

    st_arrow_2 = (
        (SURFACE_SIZE[0] * 0.555, SURFACE_SIZE[1] * 0.105),
        (SURFACE_SIZE[0] * 0.575, SURFACE_SIZE[1] * 0.105),
        (SURFACE_SIZE[0] * 0.565, SURFACE_SIZE[1] * 0.119),
    )

    def __init__(self, player, poke_n: int):
        super().__init__(player)
        self.poke_n = poke_n
        # self.display_large = None
        self.get_data()
        self.text = [game.FONT_20.render(game.get_game_instance().get_message(m) + ":", True, (0, 0, 0)) for m in ["name", "type", "xp_point", "next_level"]]

        self.text_width = [t.get_rect().size[0] * 0.5 for t in self.text]

    # noinspection PyAttributeOutsideInit
    def get_data(self):
        poke = self.player.team[self.poke_n]
        self.poke = poke
        self.display_large = poke.get_front_image(4)
        self.name = game.FONT_20.render(poke.get_name(True), True, (255, 255, 255))
        self.name2 = game.FONT_20.render(poke.get_name(True), True, (0, 0, 0))
        self.lvl = game.FONT_20.render("N.{}".format(poke.lvl), True, (255, 255, 255))
        self.xp = game.FONT_20.render("{:,}".format(poke.xp).replace(',', ' '), True, (0, 0, 0))
        self.xp_need = game.FONT_20.render("{:,}".format((s := poke.current_xp_status())[1] - s[0]).replace(',', ' '), True, (0, 0, 0))
        self.xp_size = self.xp.get_rect().size[0]
        self.xp_need_size = self.xp_need.get_rect().size[0]
        self.xp_s = poke.current_xp_status()
        self.need_xp = game.FONT_20.render("{:,}".format(self.xp_s[1] - self.xp_s[0]).replace(',', ' '), True, (0, 0, 0))
        self._type = [game.FONT_16.render(_type.get_name(), True, (255, 255, 255)) for _type in poke.poke.types]
        self.poke_ball = pygame.transform.scale(self.poke.poke_ball.image, (16, 16))
        # todo: add pokeball

    def on_key_escape(self):
        self.player.open_menu(TeamMenu(self.player))

    def on_key_y(self, value, press):
        l = self.player.get_non_null_team_number()
        if l == 0:
            self.player.close_menu()
        if value < 0 and press:
            if self.poke_n > 0:
                self.poke_n -= 1
            else:
                self.poke_n = l - 1
            self.get_data()
        elif value > 0 and press:
            if self.poke_n < l - 1:
                self.poke_n += 1
            else:
                self.poke_n = 0
            self.get_data()


    def render(self, display):
        display.fill((238, 235, 252))
        pygame.draw.polygon(display, (241, 65, 78), StatusMenu.st_poly_1)
        pygame.draw.polygon(display, (206, 51, 65), StatusMenu.st_poly_2)
        pygame.draw.polygon(display, (0, 0, 0), StatusMenu.st_poly_3)
        pygame.draw.polygon(display, (241, 65, 78), StatusMenu.st_arrow_1)
        pygame.draw.polygon(display, (241, 65, 78), StatusMenu.st_arrow_2)

        display.blit(self.display_large, (SURFACE_SIZE[0] * 0.5, SURFACE_SIZE[1] * 0.2))

        display.blit(self.name, (SURFACE_SIZE[0] * 0.6, SURFACE_SIZE[1] * 0.06))
        display.blit(self.lvl, (SURFACE_SIZE[0] * 0.8, SURFACE_SIZE[1] * 0.06))
        display.blit(self.poke_ball, (SURFACE_SIZE[0] * 0.555, SURFACE_SIZE[1] * 0.06 + 1))

        _y = SURFACE_SIZE[1] * 0.1

        for i in range(2):
            pygame.draw.rect(display, (219, 219, 217), pygame.Rect(0, _y, SURFACE_SIZE[0] * 0.25, SURFACE_SIZE[1] * 0.13))
            pygame.draw.rect(display, (255, 255, 255), pygame.Rect(SURFACE_SIZE[0] * 0.25, _y, SURFACE_SIZE[0] * 0.25, SURFACE_SIZE[1] * 0.13))

            pygame.draw.rect(display, (241, 241, 241), pygame.Rect(0, _y + SURFACE_SIZE[1] * 0.06, SURFACE_SIZE[0] * 0.5, SURFACE_SIZE[1] * 0.01))

            a = 0 if i == 0 else 2

            display.blit(self.text[a], (SURFACE_SIZE[0] * 0.125 - self.text_width[a], _y + SURFACE_SIZE[1] * 0.015))
            display.blit(self.text[a + 1], (SURFACE_SIZE[0] * 0.125 - self.text_width[a + 1], _y + SURFACE_SIZE[1] * 0.085))

            _x_ = SURFACE_SIZE[0] * 0.27

            if i == 0:
                display.blit(self.name2, (_x_, _y + SURFACE_SIZE[1] * 0.015))
                for ii in range(len(self._type)):
                    utils.draw_type(display, _x_, _y + SURFACE_SIZE[1] * 0.085, self.poke.poke.types[ii])
                    _x_ += SURFACE_SIZE[0] * 0.11
            else:
                display.blit(self.xp, (_x_, _y + SURFACE_SIZE[1] * 0.015))
                display.blit(self.xp_need, (SURFACE_SIZE[0] * 0.46 - self.xp_need_size, _y + SURFACE_SIZE[1] * 0.078))
                utils.draw_progress_bar(display, (_x_, _y + SURFACE_SIZE[1] * 0.11), (SURFACE_SIZE[0] * 0.19, 4), (101, 100, 98), (96, 204, 212), self.xp_s[0] / self.xp_s[1])

            _y += SURFACE_SIZE[1] * 0.14

        _x = SURFACE_SIZE[0] * 0.03
        _y = SURFACE_SIZE[1] * 0.5

        for ab in range(4):
            utils.draw_ability(display, (_x, _y), self.poke.get_ability(ab))
            _y += 40
