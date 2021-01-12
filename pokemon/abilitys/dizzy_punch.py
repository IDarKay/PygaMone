from typing import NoReturn, Union

import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import pygame
import pokemon.player_pokemon as p_poke
import pokemon.status.pokemon_status as pokemon_status
import random


class DizzyPunchAbility(abilitys.AbstractAbility):

    img_y: Union[pygame.Surface]

    def __init__(self):
        super().__init__(id_='dizzy_punch',
                         type="NORMAL",
                         category="PHYSICAL",
                         pp=10,
                         max_pp=16,
                         power=70,
                         accuracy=100,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         target=abilitys.TARGET_ENEMY)

        self.render_during = 1200
        self.need_sound = True
        self.__data: list[bool] = [False]

    def get_rac(self, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        l_move = None
        e_move = None
        if ps_t < 150:
            v = int(15 * ps_t / 150)
            l_move = launcher[2], v, -v if launcher[1] > 300 else v
        if 600 < ps_t < 750:
            v = int(15 * ps_t / 150)
            l_move = launcher[2], v, -v if launcher[1] > 300 else v

        if 150 < ps_t < 500 or 750 < ps_t < 1000:
            v = ps_t % 180
            v = -4 if v < 60 else 0 if v < 120 else 4
            e_move = [(t[2], v, 0) for t in target]
        return battle_.RenderAbilityCallback(move_launcher=l_move, move_target=e_move)

    def load_assets(self) -> bool:
        if super().load_assets():
            self.img_y = pygame.image.load('assets/textures/ability/fist_y.png')
            return True
        return False

    def unload_assets(self) -> bool:
        if super().unload_assets():
            del self.img_y
            return True
        return False

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[tuple[dict[str, int], list['pokemon_status.Status']],
                  list[tuple[dict[str, int], list['pokemon_status.Status']]]]:
        return ({}, []), [({}, [status.CONFUSE] if random.random() < 0.2 else []) for _ in range(len(targets))]

    def render(self, display: pygame.display, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)

        if 150 < ps_t < 500 or 750 < ps_t < 1000:
            ps_t -= 150 if ps_t <= 500 else 650
            size = (1 - min(ps_t / 350, 1)) * 4 + 1
            sizes = self.img_y.get_size()
            sizes = (int(sizes[0] * size), int(sizes[1] * size))
            im = pygame.transform.scale(self.img_y, sizes)
            for t in target:
                display.blit(im, (t[0] - sizes[0] // 2, t[1] - 40 - sizes[1] // 2))
