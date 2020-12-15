from typing import NoReturn, Callable, Optional
from hud.menu_calass import Menu
import pygame
import pokemon.pokemon as pokemon
import pokemon.player_pokemon as player_pokemon
import game
import utils
import option
import sound_manager
import sounds
import hud.hud as hud


class ForgetAbility(Menu):

    def __init__(self, player, poke: 'player_pokemon.PlayerPokemon', new_ab: str, callback: Callable[[int], NoReturn]):
        super().__init__(player)
        self.callback = callback
        self.__new_ab: str = new_ab
        self.__ab: 'player_pokemon.PokemonAbility' = player_pokemon.PokemonAbility.new_ability(new_ab)
        self.__keys = {
            game.get_game_instance().get_message("back"): option.KEY_QUITE,
            game.get_game_instance().get_message("validate"): option.KEY_ACTION
        }
        self.__poke = poke
        self.selected = 0
        self.__on_question = 0
        self.__ask = [
            game.game_instance.get_message("yes"),
            game.game_instance.get_message("no")
        ]

    def render(self, display: pygame.Surface):
        # background ==========
        display.fill('#e6ffff')
        pygame.draw.polygon(display, "#c42833", ((424, 0), (530, 0), (212, 600), (106, 600)))
        pygame.draw.polygon(display, "#e3313f", ((0, 0), (424, 0), (106, 600), (0, 600)))
        pygame.draw.polygon(display, (0, 0, 0), ((585, 30), (1060, 30), (1060, 60), (570, 60)))
        # ====================
        utils.draw_button_info(display, **self.__keys)
        self.draw_name_and_stats(display)
        self.draw_ability(display)

    def draw_name_and_stats(self, display: pygame.Surface):
        display.blit(game.FONT_24.render(self.__poke.get_name(True), True, "#FFFFFF"),
                     (636, 45 - game.FONT_SIZE_24[1] // 2))
        display.blit(game.FONT_24.render(f'N. {self.__poke.lvl}', True, "#FFFFFF"),
                     (848, 45 - game.FONT_SIZE_24[1] // 2))
        display.blit(pygame.transform.scale(self.__poke.poke_ball.image, (16, 16)), (590, 37))

        y, h, c, l, x = 80, 40, 3, 400, 600,
        tx = (game.game_instance.get_message('type'),
              *(game.game_instance.get_message(f'stats.{st}') for st in pokemon.STATS))
        tx_v = (None, f'{self.__poke.heal}/{self.__poke.get_max_heal()}',
                *(str(self.__poke.stats[st]) for st in pokemon.STATS if st != pokemon.HEAL))
        half = int(l * 0.4)

        pygame.draw.rect(display, (0, 0, 0), (x, y, l, h))
        display.blit(
            r_t := game.FONT_24.render(f'N° {str(self.__poke.poke.id_):<3s}  -  {self.__poke.poke.get_name(True)}',
                                       True, "#ffffff"), (x + 5, y + (h - r_t.get_size()[1]) // 2))
        y += h

        def right_getter(i, x_, y_):
            if i == 0:
                for ii in range(len(self.__poke.poke.types)):
                    utils.draw_type(display, x_, y_ + h // 2 - 8, self.__poke.poke.types[ii])
                    x_ += 106
                return None
            return tx_v[i]

        utils.draw_table(display, y=y, x=x, h=h, c=c, l=l, size=7, half=half,
                         left_getter=lambda i: tx[i], right_getter=right_getter)

    def draw_ability(self, display: pygame.Surface):
        _x, _y = 40, 50
        for ab in range(4):
            c1, tx_c = ((0, 0, 0), (255, 255, 255)) if self.selected == ab else ((255, 255, 255), (0, 0, 0))
            utils.draw_ability(display, (_x, _y), self.__poke.get_ability(ab),
                               color_1=c1, text_color_1=tx_c)
            _y += 40
        c1, tx_c = ((0, 0, 0), (255, 255, 255)) if self.selected == 4 else ((255, 255, 255), (0, 0, 0))
        utils.draw_ability(display, (_x + 20, _y), self.__ab,
                           color_1=c1, text_color_1=tx_c)

        left = [game.game_instance.get_message(m) for m in ("categories", "power", "accuracy")]
        c_ab = self.get_select_ab()
        right = (c_ab.ability.get_category_name(), str(c_ab.ability.power), str(c_ab.ability.accuracy)) if c_ab else ('---',) * 3

        y = utils.draw_table(display, x=0, y=280, h=40, c=3, l=500, half=250, size=3, left_getter=lambda i: left[i],
                         right_getter=lambda i, x, y: right[i], split_color_1=None, split_color_2=None, font=game.FONT_20)

        pygame.draw.rect(display, (255, 255, 255), (0, y, 500, 100))
        if c_ab:
            y += 10
            for p_l in hud.Dialog.split(c_ab.ability.get_description(), 60):
                display.blit(game.FONT_20.render(p_l, True, (0, 0, 0)), (10, y))
                y += game.FONT_SIZE_24[1] + 5

    def get_select_ab(self) -> Optional['player_pokemon.PokemonAbility']:
        if self.selected < 4:
            return self.__poke.get_ability(self.selected)
        return self.__ab

    def on_key_y(self, value: float, press: bool) -> NoReturn:
        if press and not self.__on_question:
            if value < 0 and self.selected > 0:
                self.selected -= 1
                sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)
            elif value > 0 and self.selected < 4:
                self.selected += 1
                sound_manager.start_in_first_empty_taunt(sounds.PLINK_2)

    def on_key_action(self) -> NoReturn:
        if not self.__on_question:
            if self.selected < 4:
                ab = self.__poke.get_ability(self.selected)
                self.__on_question = True
                self.player.open_dialogue(
                    hud.QuestionDialog("battle.xp.forget_menu.confirm_yes",
                                       callback=lambda v, i: self.ask_callback(True, i),
                                       ask=self.__ask, speed_skip=True, speed=25, need_morph_text=True, style=2,
                                       text_var=[ab.ability.get_name() if ab else '---', self.__ab.ability.get_name()]))
            else:
                self.ask_cancel()
        elif self.__on_question == -1:
            self.__on_question = False

    def ask_callback(self, yes: bool, index):
        if index == 0:
            self.player.close_menu()
            self.callback(self.selected if yes else -1)
        else:
            self.__on_question = -1

    def ask_cancel(self):
        self.__on_question = True
        self.player.open_dialogue(
            hud.QuestionDialog("battle.xp.forget_menu.confirm_no",
                               callback=lambda v, i: self.ask_callback(False, i),
                               ask=self.__ask, speed_skip=True, speed=25, need_morph_text=True, style=2,
                               text_var=[self.__ab.ability.get_name()]))

    def on_key_escape(self) -> NoReturn:
        if not self.__on_question:
            self.ask_cancel()
        elif self.__on_question == -1:
            self.__on_question = False
