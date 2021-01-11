from typing import NoReturn, Union

from pygame import Surface
from pygame.surface import SurfaceType

import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import random
import pygame


class CrabhammerAbility(abilitys.AbstractAbility):
    bubble: Union[Surface, SurfaceType]

    def __init__(self):
        super().__init__(id_='crabhammer',
                         type="WATER",
                         category="PHYSICAL",
                         pp=10,
                         max_pp=16,
                         power=100,
                         accuracy=90,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 2500
        self.need_sound = True

    def load_assets(self) -> bool:
        if super().load_assets():
            self.bubble = pygame.image.load('assets/textures/ability/bubble.png')
            return True
        return False

    def get_rac(self, target: list[type[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        if ps_t > 1000:
            v = ps_t % 180
            v = -6 if v < 60 else 0 if v < 120 else 6
            target_m = [(t[2], v, 0) for t in target]
            target_c = [(t[2], 64, 134, 199, 130) for t in target]
            return battle_.RenderAbilityCallback(color_editor_target=target_c, move_target=target_m)
        return battle_.RenderAbilityCallback()

    def unload_assets(self) -> bool:
        if super().load_assets():
            del self.bubble
            del self.random_vec
            return True
        return False

    def render(self, display: pygame.display, target: list[type[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)
            self.random_vec = [
                (random.uniform(-2, 2), random.uniform(-2, 2), random.randint(0, 1000), random.randint(400, 1000)) for _
                in range(20)]

        for t in target:
            if ps_t < 1000:
                x1, y1 = launcher[0] + 40, launcher[1] - 50
                x2, y2 = t[0], t[1] - 30
                a = (y2 - y1) / (x2 - x1)
                b = y1 - a * x1
                max_delta_x = x2 - x1
                x = min((ps_t / 1000), 1) * max_delta_x + x1
                y = (a * x + b) + (0.002 * (x - x1) * (x - x2))
                display.blit(pygame.transform.scale(self.bubble, (64, 64)), (x - 32, y - 32))
            else:
                ps_t -= 1000
                x_start, y_start = t[0], t[1] - 40
                for bu in self.random_vec:
                    vec = [bu[0], bu[1]]
                    if 0 < (n_pst_t := ps_t - bu[2]) < bu[3]:
                        adv = (n_pst_t / bu[3])
                        vec[0] *= adv * 150
                        vec[1] *= adv * 150
                        display.blit(self.bubble, (x_start - 16 + vec[0], y_start - 16 + vec[1]))
