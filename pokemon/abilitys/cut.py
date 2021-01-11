from typing import NoReturn, Union

from pygame import Surface
from pygame.surface import SurfaceType

import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import random
import pygame


class CutAbility(abilitys.AbstractAbility):
    ball: Union[Surface, SurfaceType]
    cut: Union[Surface, SurfaceType]

    def __init__(self):
        super().__init__(id_='cut',
                         type="NORMAL",
                         category="PHYSICAL",
                         pp=30,
                         max_pp=48,
                         power=50,
                         accuracy=95,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 740
        self.need_sound = True

    def load_assets(self) -> bool:
        if super().load_assets():
            self.ball = pygame.image.load('assets/textures/ability/yellow_ball.png')
            self.cut = pygame.image.load('assets/textures/ability/cut.png')
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
            del self.ball
            del self.cut
            del self.random_vec
            return True
        return False

    def render(self, display: pygame.display, target: list[type[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)
            self.random_vec = [
                (random.uniform(-1, 1), random.uniform(-1, 1), random.randint(0, 100), random.randint(300, 400)) for _
                in range(10)]

        for t in target:
            if 150 < ps_t < 600:
                x_start, y_start = t[0] + 90, t[1] - 150
                edit = (ps_t - 150) / 600 * 80
                display.blit(self.cut, (x_start - self.cut.get_size()[0] - edit, y_start + edit))
            if ps_t > 250:
                ps_t -= 250
                x_start, y_start = t[0], t[1] - 40
                for bu in self.random_vec:
                    vec = [bu[0], bu[1]]
                    if 0 < (n_pst_t := ps_t - bu[2]) < bu[3]:
                        adv = (n_pst_t / bu[3])
                        vec[0] *= adv * 150
                        vec[1] *= adv * 150
                        display.blit(self.ball, (x_start - 16 + vec[0], y_start - 16 + vec[1]))
