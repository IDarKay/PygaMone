from typing import NoReturn, Union
import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import random
import pygame

SPEED = 100


class CometPunchAbility(abilitys.AbstractAbility):

    img_g: Union[pygame.Surface]
    img_y: Union[pygame.Surface]
    current_vars: list

    def __init__(self):
        super().__init__(id_='comet_punch',
                         type="NORMAL",
                         category="PHYSICAL",
                         pp=15,
                         max_pp=24,
                         power=18,
                         accuracy=85,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=abilitys.TARGET_ENEMY,
                         range=abilitys.RANGE_TWO
                         )
        self.render_during = 0
        self.need_sound = True

    def get_render_during(self):
        return 1000 * self.last_nb_hit

    def load_assets(self) -> bool:
        if super().load_assets():
            self.img_g = pygame.image.load('assets/textures/ability/fist_g.png')
            self.img_y = pygame.image.load('assets/textures/ability/fist_y.png')
            return True
        return False

    def unload_assets(self) -> bool:
        if super().unload_assets():
            del self.img_g
            del self.img_y
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
            self.current_vars = [[False] * self.last_nb_hit, [(random.randint(-50, 50), random.randint(-50, 50)) for _ in range(15)]]

        c_hit = min(self.last_nb_hit - 1, ps_t // 1000)
        if not self.current_vars[0][c_hit]:
            self.current_vars[0][c_hit] = True
            sound_manager.start_in_first_empty_taunt(self.sound)

        for t_i in range(len(target)):

            x, y = target[t_i][0], target[t_i][1] - 55

            for i in range(15):
                i_60 = int((i / 15) * ((1000 * (c_hit + 1)) - SPEED))
                if i_60 < ps_t < i_60 + SPEED:
                    rdm = self.current_vars[1][i]
                    display.blit(self.img_y if (ps_t - i_60) // 50 else self.img_g, (x + rdm[0] - 14, y + rdm[1] - 14))