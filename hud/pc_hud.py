from typing import NoReturn, Optional

import game
import option
import sound_manager
import sounds
import utils
from character import player
from hud.menu_calass import Menu
import pygame

from pokemon import player_pokemon, pokemon


class PCHud(Menu):
    POLY_1 = ((0, 0), (212, 0), (0, 480))
    POLY_2 = ((212, 0), (318, 0), (53, 600), (0, 600), (0, 480))

    def __init__(self, player_):
        super().__init__(player_)
        self.box = 0
        self.selected = [0, 0]  # x [-1: 5] y [0: 5]
        self.move = [-2, -2]
        self.move_box = 0
        self.keys = {
            game.get_game_instance().get_message("back"): option.KEY_QUITE,
            game.get_game_instance().get_message("box_next"): option.KEY_MENU_RIGHT,
            game.get_game_instance().get_message("box_previous"): option.KEY_MENU_LEFT,
            game.get_game_instance().get_message("move"): option.KEY_ACTION
        }
        self.tab_cat = [game.FONT_20.render(game.game_instance.get_message(f'stats.{st}'), True, (0, 0, 0))
                        for st in pokemon.STATS]
        self.tab_cat.append(game.FONT_20.render(game.game_instance.get_message("object"), True, (0, 0, 0)))


    def render(self, display: pygame.Surface):
        display.fill("#e8f2fe")
        pygame.draw.polygon(display, "#b4ea34", PCHud.POLY_1)
        pygame.draw.polygon(display, "#9bd600", PCHud.POLY_2)

        utils.draw_button_info(display, **self.keys)

        self.draw_team(display)
        self.draw_box(display)
        self.draw_info(display)

    def draw_info(self, display: pygame.Surface):
        poke = self.get_selected()
        if poke is None:
            return
        x, y = 750, 20
        box_height = 32
        separator = 4
        pygame.draw.rect(display, "#dbdbd9", (x, y, 1060 - x, box_height))
        display.blit(pk := poke.poke_ball.image, (x, y + (box_height - pk.get_size()[1]) // 2))
        display.blit(
            tx := game.FONT_24.render(poke.get_name(True), True, (0, 0, 0)),
            (x + 30, y + (box_height - tx.get_size()[1]) // 2)
        )
        display.blit(
            tx := game.FONT_24.render(f"Lvl. {poke.get_lvl()}", True, (0, 0, 0)),
            (1060 - tx.get_size()[0] - 10, y + (box_height - tx.get_size()[1]) // 2)
        )
        y += separator + box_height
        tab_value = [f'{str(poke.get_stats(st)):<2s}' if st != pokemon.HEAL else
                     f'{poke.heal}/{poke.get_max_heal()}' for st in pokemon.STATS]
        tab_value.append(poke.item.get_name() if poke.item else "-")
        cat_size = max(self.tab_cat, key=lambda sur: sur.get_size()[0]).get_size()[0] + 15
        for i in range(len(self.tab_cat)):
            pygame.draw.rect(display, "#dbdbd9", (x, y, cat_size, box_height))
            display.blit(im := self.tab_cat[i], (x + (cat_size - im.get_size()[0]) // 2,
                                                 y + (box_height - im.get_size()[1]) // 2))
            pygame.draw.rect(display, "#f6fbff", (x + cat_size, y, 1060 - x - cat_size, box_height))
            display.blit(im := game.FONT_20.render(tab_value[i], True, (0, 0, 0)),
                         (x + cat_size + 10, y + (box_height - im.get_size()[1]) // 2)
                         )
            y += box_height
            if i != len(self.tab_cat) - 1:
                pygame.draw.rect(display, "#f6fbff", (x, y, 1060 - x, separator))
                y += separator
        pygame.draw.rect(display, "#f6fbff", (x, y, 1060 - x, box_height * 4 + separator * 4))
        y += separator
        for i in range(4):
            ab = poke.get_ability(i)
            if ab:
                color = ab.ability.type.image.get_at((0, 0))
                pygame.draw.rect(display, color, (x + 5, y, 1050 - x, box_height), border_radius=2)
                display.blit(im := pygame.transform.scale(ab.ability.type.image, (44, 32)),
                             (x + 5, y + (box_height - im.get_size()[1]) // 2), pygame.Rect(0, 0, 32, 32))
                display.blit(tx := game.FONT_20.render(ab.ability.get_name(), True, (0, 0, 0)),
                             (x + 50, y + (box_height - tx.get_size()[1]) // 2))
                y += box_height + separator

    def draw_box(self, display: pygame.Surface):
        case_size, marge_size = 64, 8
        total_size = 6 * case_size + 5 * marge_size

        x, y = 530 - total_size // 2, 40
        utils.draw_rond_rectangle(display, 530 - 100, y, 40, 200, (255, 255, 255))
        display.blit(
            tx := game.FONT_24.render(game.game_instance.get_message("box_n").format(self.box + 1), True, (0, 0, 0)),
            (530 - tx.get_size()[0] // 2, y + 20 - tx.get_size()[1] // 2)
        )

        y += 50
        for y_ in range(6):
            for x_ in range(6):
                coord: tuple[int, int] = (x + case_size * x_ + marge_size * x_, y + case_size * y_ + marge_size * y_)
                pygame.draw.rect(display, (245, 245, 245), (*coord, case_size, case_size), border_radius=6)
                poke = self.player.pc.get_poke(self.box, x_ + 6 * y_)
                if poke:
                    display.blit(im := poke.get_front_image(0.75), (coord[0] + case_size // 2 - im.get_size()[0] // 2,
                                                                    coord[1] + case_size // 2 - im.get_size()[1] // 2))
                if self.selected[0] == x_ and self.selected[1] == y_:
                    display.blit(ar := utils.ARROW, (coord[0] - ar.get_size()[0] + 5,
                                                     coord[1] + case_size // 2 - ar.get_size()[1] // 2))

    def draw_team(self, display: pygame.Surface):
        x = 50
        y = 40
        length = 140
        utils.draw_rond_rectangle(display, x - 10, y, 40, length + 20, (255, 255, 255))
        tx = game.FONT_24.render(game.game_instance.get_message("team"), True, (0, 0, 0))
        display.blit(tx, (x + (length + 10 - tx.get_size()[0]) // 2, y + 20 - tx.get_size()[1] // 2))
        y += 60

        for i in range(6):
            utils.draw_rond_rectangle(display, x, y, 60, length, (255, 255, 255))
            poke = self.player.team[i]
            if poke:
                display.blit(im := poke.get_front_image(0.5), (x - 5 - im.get_size()[0] // 2,
                                                               y + 30 - im.get_size()[1] // 2))
                display.blit(
                    game.FONT_16.render(poke.get_name(True), True, (0, 0, 0)),
                    (x + 15, y + 5)
                )
                display.blit(
                    game.FONT_24.render(f'Lvl. {poke.get_lvl()}', True, (0, 0, 0)),
                    (x + 15, y + 25)
                )
            if self.selected[0] == -1 and self.selected[1] == i:
                display.blit(ar := utils.ARROW, (x - ar.get_size()[0] - 15,
                                                 y + 30 - ar.get_size()[1] // 2))
            y += 80

    def on_key_action(self) -> NoReturn:
        if self.move == [-2, -2]:
            if self.get_selected() is None:
                sound_manager.start_in_first_empty_taunt(sounds.BLOCK)
            else:
                sound_manager.start_in_first_empty_taunt(sounds.PLINK)
                self.move = self.selected.copy()
                self.move_box = self.box
        else:
            sound_manager.start_in_first_empty_taunt(sounds.PLINK)
            m_team, s_team = self.move[0] == -1, self.selected[0] == -1
            if m_team ^ s_team:
                if m_team:
                    self.player.switch_pc_pokemon(self.move[1], self.box, self.selected[0] + self.selected[1] * 6)
                else:
                    self.player.switch_pc_pokemon(self.selected[1], self.move_box, self.move[0] + self.move[1] * 6)
            elif m_team and s_team:
                self.player.switch_pokemon(self.move[1], self.move[1])
            else:
                self.player.pc.switch((self.box, self.selected[0] + self.selected[1] * 6),
                                      (self.move_box, self.move[0] + self.move[1] * 6))
            self.move = [-2, -2]

    def get_case(self):
        return self.selected[0] + self.selected[1] * 6

    def get_selected(self) -> Optional['player_pokemon.PlayerPokemon']:
        if self.selected[0] == -1:
            return self.player.team[self.selected[1]]
        return self.player.pc.get_poke(self.box, self.selected[0] + self.selected[1] * 6)

    def on_key_y(self, value: float, press: bool) -> NoReturn:
        if press:
            if value < 0 and self.selected[1] > 0:
                sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
                self.selected[1] -= 1
            elif value > 0 and self.selected[1] < 5:
                sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
                self.selected[1] += 1

    def on_key_x(self, value: float, press: bool) -> NoReturn:
        if press:
            if value < 0 and self.selected[0] > -1:
                sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
                self.selected[0] -= 1
            elif value > 0 and self.selected[0] < 5:
                sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
                self.selected[0] += 1

    def on_key_menu_x(self, value: float, press: bool) -> NoReturn:
        if press:
            if value < 0 and self.box > 0:
                sound_manager.start_in_first_empty_taunt(sounds.PLINK)
                self.box -= 1
            elif value > 0 and self.box < player.NB_BOX - 1:
                sound_manager.start_in_first_empty_taunt(sounds.PLINK)
                self.box += 1

    def on_key_escape(self) -> NoReturn:
        if self.move == [-2, -2]:
            sound_manager.start_in_first_empty_taunt(sounds.PC_CLOSE)
            self.player.close_menu()
        else:
            self.move = [-2, -2]

    def __del__(self):
        game.POKE_CACHE.clear()
        pass
