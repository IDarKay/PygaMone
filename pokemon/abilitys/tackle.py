from typing import NoReturn

import pokemon.abilitys as abilitys
import gif_manger
import sound_manager
import pokemon.battle.battle as battle_
import pygame


class TackleAbility(abilitys.AbstractAbility):

    def __init__(self):
        super().__init__(id_='tackle',
                         type="NORMAL",
                         category="PHYSICAL",
                         pp=34,
                         max_pp=56,
                         power=40,
                         accuracy=100,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=abilitys.TARGET_ENEMY)

        self.render_during = 1300
        self.need_sound = True
        self.__data: list[bool] = [False]

    def get_rac(self, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        l_move = None
        e_move = None
        if ps_t < 500:
            v = int(15 if ps_t > 300 else 15 * ps_t / 280)
            l_move = launcher[2], v, -v if launcher[1] > 300 else v

        if 400 < ps_t < 1300:
            v = ps_t % 180
            v = -4 if v < 60 else 0 if v < 120 else 4
            e_move = [(t[2], v, 0) for t in target]
        return battle_.RenderAbilityCallback(move_launcher=l_move, move_target=e_move)

    def render(self, display: pygame.display, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            self.__data = [True]

            self.g_i = []
            gif = gif_manger.CONTACT.get()
            for t in target:
                self.g_i.append(gif.display((t[0] - 24, t[1] - 60), speed=170))

        if ps_t > 380 and self.__data[0]:
            self.__data[0] = False
            sound_manager.start_in_first_empty_taunt(self.sound)

        if 400 < ps_t < 1300:
            for g in self.g_i:
                g.render(display)
