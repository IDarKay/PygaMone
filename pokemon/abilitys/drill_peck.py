from typing import NoReturn

import pokemon.abilitys as abilitys
import gif_manger
import sound_manager
import pokemon.battle.battle as battle_
import pygame


class DrillPeckAbility(abilitys.AbstractAbility):

    def __init__(self):
        super().__init__(id_='drill_peck',
                         type="FLYING",
                         category="PHYSICAL",
                         pp=20,
                         max_pp=32,
                         power=80,
                         accuracy=100,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=abilitys.TARGET_ENEMY
                         )

        self.render_during = 1950
        self.need_sound = True

    def get_rac(self, target: list[tuple[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        l_rotate = None
        e_move = None
        if 90 < ps_t < 1300:
            if ps_t < 1000:
                r = 22.5 * min((ps_t - 90) / 500, 1)
            else:
                r = 22.5 * (1 - min((ps_t - 1000) / 300, 1))
            l_rotate = launcher[2], -r

        if 1000 < ps_t < 1900:
            v = ps_t % 180
            v = -4 if v < 60 else 0 if v < 120 else 4
            e_move = [(t[2], v, 0) for t in target]
        return battle_.RenderAbilityCallback(rotate_launcher=l_rotate, move_target=e_move)

    def unload_assets(self) -> bool:
        if super().unload_assets():
            gif_manger.CONTACT.un_load()
            del self.g_i
            return True
        return False

    def render(self, display: pygame.display, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            self.g_i = []
            gif = gif_manger.CONTACT.get()
            sound_manager.start_in_first_empty_taunt(self.sound)
            for t in target:
                self.g_i.append(gif.display((t[0] - 24, t[1] - 60), speed=71))

        if 1000 < ps_t < 1497:
            for g in self.g_i:
                g.render(display)
