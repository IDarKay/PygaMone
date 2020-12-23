from typing import NoReturn, Union
import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import random
import pygame


class BarrageAbility(abilitys.AbstractAbility):

    ball: Union[pygame.Surface]
    current_vars: list

    def __init__(self):
        super().__init__(id_='barrage',
                         type="NORMAL",
                         category="PHYSICAL",
                         pp=20,
                         max_pp=32,
                         power=15,
                         accuracy=85,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=abilitys.TARGET_ENEMY,
                         range=abilitys.RANGE_TWO
                         )
        self.render_during = 0
        self.need_sound = True

    def get_render_during(self):
        return 1200 * self.last_nb_hit

    def load_assets(self) -> bool:
        if super().load_assets():
            self.ball = pygame.image.load('assets/textures/ability/barrage.png')
            return True
        return False

    def unload_assets(self) -> bool:
        if super().load_assets():
            del self.ball
            del self.current_vars
            return True
        return False

    def get_nb_hit(self) -> int:
        r = random.random()
        if r <= (1/3):
            return 2
        if r <= (2/3):
            return 3
        if r <= (5/6):
            return 4
        return 5

    def get_rac(self, target: list[tuple[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        if ps_t % 1200 > 950:
            v = ps_t % 180
            v = -6 if v < 60 else 0 if v < 120 else 6
            target_m = [(t[2], 0, v) for t in target]
            return battle_.RenderAbilityCallback(move_target=target_m)
        return battle_.RenderAbilityCallback()

    def render(self, display: pygame.display, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            self.current_vars = [False] * self.last_nb_hit

        c_hit = min(self.last_nb_hit - 1, ps_t // 1200)
        if not self.current_vars[c_hit]:
            self.current_vars[c_hit] = True
            sound_manager.start_in_first_empty_taunt(self.sound)

        x1, y1 = launcher[0] + 40, launcher[1] - 50
        x2, y2 = target[0][0], target[0][1] - 30
        a = (y2 - y1) / (x2 - x1)
        b = y1 - a * x1
        max_delta_x = x2 - x1

        if ps_t % 1200 < 1000:
            x = min(((ps_t % 1200) / 1000), 1) * max_delta_x + x1
            y = (a * x + b) + (0.002 * (x - x1) * (x - x2))
            display.blit(self.ball, (x - 32, y - 32))
        else:
            display.blit(self.ball, (x2 - 32, y2 - 32))