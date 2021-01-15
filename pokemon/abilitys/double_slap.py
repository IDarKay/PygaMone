from typing import NoReturn, Union
import pokemon.abilitys as abilitys
import pokemon.battle.battle as battle_
import pygame
import random

import sound_manager


class DoubleSlapAbility(abilitys.AbstractMultiHitAbility):
    chop_1: Union[pygame.Surface]
    chop_2: Union[pygame.Surface]

    def __init__(self):
        super().__init__(id_='double_slap',
                         type="NORMAL",
                         category="PHYSICAL",
                         pp=10,
                         max_pp=16,
                         power=15,
                         accuracy=85,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 0
        self.need_sound = True

    def get_hit_during(self) -> int:
        return 1200

    def load_assets(self) -> bool:
        if super().load_assets():
            self.chop_1 = pygame.image.load('assets/textures/ability/leftchop.png')
            self.chop_2 = pygame.image.load('assets/textures/ability/rightchop.png')
            return True
        return False

    def unload_assets(self) -> bool:
        if super().unload_assets():
            del self.chop_1
            del self.chop_2
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

    def hit_rac(self, target: list[tuple[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool,
                hit: int) -> 'battle_.RenderAbilityCallback':
        e_move = None
        if 150 < ps_t < 380 or 550 < ps_t < 780:
            v = ps_t % 180
            v = -4 if v < 60 else 0 if v < 120 else 4
            e_move = [(t[2], v, 0) for t in target]
        return battle_.RenderAbilityCallback(move_target=e_move)

    def hit_render(self, display: pygame.Surface, target: list[tuple[int, int, int]],
                   launcher: tuple[int, int, int], ps_t: int, first_time: bool, hit: int) -> NoReturn:
        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)
        if ps_t < 900:
            im = self.chop_1 if ps_t < 450 else self.chop_2
            ps_t %= 450
            if ps_t > 400:
                return
            size = (1 - (ps_t / 400)) * 3
            sizes = im.get_size()
            sizes = (int(sizes[0] * size), int(sizes[1] * size))
            im = pygame.transform.scale(im, sizes)
            for t in target:
                display.blit(im, (t[0] - sizes[0] // 2, t[1] - 40 - sizes[1] // 2))
