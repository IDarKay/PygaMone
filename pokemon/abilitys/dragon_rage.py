from typing import NoReturn, Union
import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import pokemon.player_pokemon as p_poke
import random
import pygame

import utils

SPEED = 200


class BubbleBeamAbility(abilitys.AbstractAbility):

    current_vars: list[int]
    p_generic: list[Union[pygame.Surface]]
    y_generic: list[Union[pygame.Surface]]

    def __init__(self):
        super().__init__(id_='dragon_rage',
                         type="DRAGON",
                         category="SPECIAL",
                         pp=10,
                         max_pp=16,
                         power=0,
                         accuracy=100,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 2500
        self.need_sound = True

    def get_damage(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) -> \
            tuple[list[tuple[int, float]], bool, int]:
        back = []
        for tr in targets:
            if tr:
                type_edit = self.type.get_attack_edit(tr.poke)

                f_damage = int(type_edit * 40)

                self.last_damage.append(f_damage)
                back.append((f_damage, type_edit))
            else:
                self.last_damage.append(0)
                back.append((0, 0.0))
        return back, False, 0

    def get_rac(self, target: list[tuple[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        if ps_t > SPEED:
            v = ps_t % 180
            v = -3 if v < 60 else 0 if v < 120 else 3
            target_m = [(t[2], v, 0) for t in target]
            target_c = [(t[2], 135, 50, 168, 130) for t in target]
            return battle_.RenderAbilityCallback(color_editor_target=target_c, move_target=target_m)
        return battle_.RenderAbilityCallback()

    def load_assets(self) -> bool:
        if super().load_assets():
            generic = [pygame.image.load(f'assets/textures/ability/generic_{i}.png') for i in range(8)]

            def resize_and_color(im: pygame.Surface, size, color):
                img = im.copy()
                if size != 1:
                    img = pygame.transform.scale(img, (int(img.get_size()[0] * size), int(img.get_size()[1] * size)))
                utils.color_image(img, color)
                return img

            self.p_generic = [resize_and_color(e, 3, (124, 35, 176, 255)) for e in generic]
            self.y_generic = [resize_and_color(e, 2, (207, 189, 54, 255)) for e in generic]
            return True
        return False

    def unload_assets(self) -> bool:
        if super().unload_assets():
            del self.p_generic
            del self.y_generic
            del self.current_vars
            return True
        return False

    def render(self, display: pygame.Surface, target: list[type[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:

        if first_time:
            self.current_vars = [random.randint(-40, 40) for _ in range(100)]
            sound_manager.start_in_first_empty_taunt(self.sound)

        for t_i in range(len(target)):

            x1, x2, y2 = launcher[0] + 40, target[t_i][0], target[t_i][1] - 30

            for i in range(100):
                i_60 = int((i / 100) * (2000 - SPEED))
                if i_60 < ps_t < i_60 + SPEED:
                    y1 = launcher[1] - 50
                    a = (y2 - y1) / (x2 - x1)
                    b = y1 - a * x1
                    max_delta_x = x2 - x1
                    x = x1 + ((ps_t - i_60) / SPEED) * max_delta_x
                    y = a * x + b + self.current_vars[i]
                    display.blit(im := self.p_generic[-1], (x - im.get_size()[0] // 2, y - im.get_size()[1] // 2))
                    display.blit(im := self.y_generic[-1], (x - im.get_size()[0] // 2, y - im.get_size()[1] // 2))
