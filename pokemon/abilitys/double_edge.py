import math
from typing import NoReturn, Union, List

import game
import gif_manger
import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import pygame

from pygame_gif import GifInstance


class DoubleEdgeAbility(abilitys.AbstractAbility):

    g_i: list[GifInstance]
    img_y: Union[pygame.Surface]

    def __init__(self):
        super().__init__(id_='double_edge',
                         type="NORMAL",
                         category="PHYSICAL",
                         pp=15,
                         max_pp=24,
                         power=120,
                         accuracy=100,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=abilitys.TARGET_ENEMY,
                         recoil_type=abilitys.RECOIL_DAMAGE,
                         recoil=0.33
                         )
        self.render_during = 2900
        self.need_sound = True

    def get_rac(self, target: list[type[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':

        if ps_t < 1800:
            v = ps_t % 450
            pi_part = ((math.pi * 2) * v / 450) - (math.pi / 2)
            x = int(math.cos(pi_part) * 10)
            y = int(math.sin(pi_part) * 20) + 20
            return battle_.RenderAbilityCallback(move_launcher=(launcher[2], x, y))
        elif ps_t > 1800:
            v = int(min(((ps_t - 1800) / 100), 1.0) * 50)
            target_m = [(t[2], v, 0) for t in target]
            return battle_.RenderAbilityCallback(move_target=target_m)
        return super().get_rac(target, launcher, ps_t, first_time)

    def unload_assets(self) -> bool:
        if super().unload_assets():
            gif_manger.CONTACT.un_load()
            del self.g_i
            return True
        return False

    def render(self, display: pygame.Surface, target: list[type[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:

        if first_time:
            self.g_i = []
            gif = gif_manger.CONTACT.get()
            sound_manager.start_in_first_empty_taunt(self.sound)
            for t in target:
                self.g_i.append(gif.display((t[0] - 24, t[1] - 60), speed=71))
        if 1800 < ps_t < 2298:
            for t in target:
                for g in self.g_i:
                    g.render(display)
