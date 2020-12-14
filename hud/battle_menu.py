from typing import NoReturn, Callable

import pygame

import sound_manager
import sounds
from character.player import Player
from hud.menu import Menu
import game
import utils
import pokemon.player_pokemon as player_pokemon

SURFACE_SIZE = (1060, 600)


class ChangePokemonMenu(Menu):

    def __init__(self, player: 'Player', call_back: Callable[[bool, int], NoReturn], is_death: bool = False):
        super().__init__(player)
        self.is_death = is_death
        self.call_back = call_back
        self.selected = 0
        self.action_selected = -1

        # self.arrow = utils.get_part_i(MENU_IMAGE, (0, 64, 22, 91), (33, 41))
        self.arrow = utils.ARROW
        self.open_time = utils.current_milli_time()
        self.text_2 = [(game.FONT_20.render(game.get_game_instance().get_message(t), True, (0, 0, 0)),
                        game.FONT_20.render(game.get_game_instance().get_message(t), True, (255, 255, 255)))
                       for t in (["use", "back"] if is_death else ["use", "heal", "back"])]

    def render(self, display):
        display.fill((255, 255, 255))
        pygame.draw.polygon(display, (246, 250, 253), ((0, 0), (132, 0), (40, 600), (0, 600)))
        # pygame.draw.polygon(display, (206, 51, 65), TeamMenu.t_poly_2)

        g_x = 106
        g_y = 60

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

        for i in range(self.player.get_non_null_team_number()):

            self.draw_pokemon(display,  self.player.team[i], g_x, g_y, poke_y,
                              (0, 0, 0) if self.selected == i else (255, 255, 255),
                              (0, 0, 0) if self.selected != i else (255, 255, 255)
                              )
            g_y += 90

        # action hud
        if self.action_selected != -1:
            _y = 60 + 90 * self.selected
            _x = 1060 * 0.31
            utils.draw_select_box(display, _x, _y, self.text_2, self.action_selected, 100)

    def draw_pokemon(self, display: pygame.Surface,
                     poke: 'player_pokemon.PlayerPokemon',
                     _x: float, _y: float, poke_y: int,
                     color, text_color
                     ):
        if not poke:
            return
        heal = poke.heal, poke.get_max_heal()
        _x2 = 24
        utils.draw_rond_rectangle(display, _x, _y, SURFACE_SIZE[1] * 0.08, SURFACE_SIZE[0] * 0.2, color)

        utils.draw_progress_bar(display,
                                (_x + _x2, _y + 1060 * 0.02),
                                (600 * 0.28, 5),
                                (52, 56, 61), (45, 181, 4), heal[0] / heal[1])

        display.blit(poke.get_front_image(0.5), (_x - 20, _y + 4 - poke_y))

        # display heal
        display.blit(game.FONT_16.render("{}/{}".format(heal[0], heal[1]), True, text_color), (_x + _x2, _y + SURFACE_SIZE[0] * 0.028))
        # display lvl
        display.blit(game.FONT_24.render("N.{}".format(poke.lvl), True, text_color), (_x + _x2 + SURFACE_SIZE[1] * 0.25, _y + SURFACE_SIZE[0] * 0.025))
        # display name
        display.blit(game.FONT_20.render(poke.get_name(True), True, text_color), (_x + _x2, _y + 2))
        # display pokeball
        display.blit(pygame.transform.scale(poke.poke_ball.image, (16, 16)), (_x + _x2 + SURFACE_SIZE[1] * 0.3, _y + 5))

        # if self.selected == i:
        #     display.blit(self.arrow, (_x - 50, _y + 2))
        #     display.blit(self.display_large[i], (SURFACE_SIZE[0] * 0.5, SURFACE_SIZE[1] * 0.2))

    def on_key_y(self, value, press):
        if value < 0 and press:
            if self.action_selected != -1:
                if self.action_selected > 0:
                    self.action_selected -= 1
            elif self.selected > 0:
                self.selected -= 1
        elif value > 0 and press:
            if self.action_selected != -1:
                if self.action_selected < (1 if self.is_death else 2):
                    self.action_selected += 1
            elif self.selected < self.player.get_non_null_team_number() - 1:
                self.selected += 1

    def on_key_action(self):
        if self.action_selected == -1:
            self.action_selected = 0
        else:
            if self.action_selected == 0:
                if pk := self.player.team[self.selected]:
                    if pk.heal > 0 and not pk.use:
                        self.call_back(True, self.selected)
                    else:
                        sound_manager.start_in_first_empty_taunt(sounds.BLOCK.sound)
            elif self.action_selected == 1 and not self.is_death:
                # todo heal
                pass
            elif self.action_selected == 2 or (self.action_selected == 1 and self.is_death):
                self.action_selected = -1

    def on_key_escape(self) -> NoReturn:
        if self.action_selected != -1:
            self.action_selected = -1
        elif not self.is_death:
            self.call_back(False, self.selected)
        else:
            sound_manager.start_in_first_empty_taunt(sounds.BLOCK.sound)
