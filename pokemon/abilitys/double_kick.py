from typing import NoReturn, Union
import pokemon.abilitys as abilitys
import pokemon.battle.battle as battle_
import pygame

import sound_manager


class DoubleKickAbility(abilitys.AbstractMultiHitAbility):
    foot: Union[pygame.Surface]
    current_vars: list

    def __init__(self):
        super().__init__(id_='double_kick',
                         type="FIGHTING",
                         category="PHYSICAL",
                         pp=30,
                         max_pp=48,
                         power=30,
                         accuracy=100,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 0
        self.need_sound = True

    def get_hit_during(self) -> int:
        return 1500

    def load_assets(self) -> bool:
        if super().load_assets():
            self.foot = pygame.image.load('assets/textures/ability/foot.png')
            return True
        return False

    def unload_assets(self) -> bool:
        if super().unload_assets():
            del self.foot
            del self.current_vars
            return True
        return False

    def get_nb_hit(self) -> int:
        return 2

    def hit_rac(self, target: list[tuple[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool,
                hit: int) -> 'battle_.RenderAbilityCallback':
        e_move = None
        if 200 < ps_t < 500 or 600 < ps_t < 900:
            v = ps_t % 180
            v = -4 if v < 60 else 0 if v < 120 else 4
            e_move = [(t[2], v, 0) for t in target]
        return battle_.RenderAbilityCallback(move_target=e_move)

    def hit_render(self, display: pygame.Surface, target: list[tuple[int, int, int]],
                   launcher: tuple[int, int, int], ps_t: int, first_time: bool, hit: int) -> NoReturn:
        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)
        print(ps_t)
        if ps_t < 1000:
            ps_t %= 500
            if ps_t > 450:
                return
            size = (1 - (ps_t / 450)) * 4 + 1
            sizes = self.foot.get_size()
            sizes = (int(sizes[0] * size), int(sizes[1] * size))
            im = pygame.transform.scale(self.foot, sizes)
            for t in target:
                display.blit(im, (t[0] - sizes[0] // 2, t[1] - 40 - sizes[1] // 2))
