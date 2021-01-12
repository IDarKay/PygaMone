from typing import NoReturn, Union

from pygame import Surface
from pygame.surface import SurfaceType

import pokemon.abilitys as abilitys
import pygame_gif
import sound_manager
import pokemon.battle.battle as battle_
import pokemon.player_pokemon as p_poke
import pokemon.status.pokemon_status as pokemon_status
import pokemon.status.status as status
import random
import pygame

import utils


class ClampAbility(abilitys.AbstractAbility):
    img_r: Union[Surface, SurfaceType]
    img_l: Union[Surface, SurfaceType]

    def __init__(self):
        super().__init__(id_='clamp',
                         type="WATER",
                         category="PHYSICAL",
                         pp=15,
                         max_pp=24,
                         power=40,
                         accuracy=85,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 600
        self.need_sound = True

    def load_assets(self) -> bool:
        if super().load_assets():
            im = pygame.image.load('assets/textures/ability/clamp.png')
            self.img_l = im
            self.img_r = pygame.transform.flip(im, True, False)
            return True
        return False

    def get_rac(self, target: list[type[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        if ps_t > 200:
            v = ps_t % 180
            v = -6 if v < 60 else 0 if v < 120 else 6
            target_m = [(t[2], v, 0) for t in target]
            return battle_.RenderAbilityCallback(move_target=target_m)
        return battle_.RenderAbilityCallback()

    def unload_assets(self) -> bool:
        if super().unload_assets():
            del self.img_l
            del self.img_r
            return True
        return False

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[tuple[dict[str, int], list['pokemon_status.Status']],
                  list[tuple[dict[str, int], list['pokemon_status.Status']]]]:
        return ({}, []), [({}, [status.CLAMP]) for _ in range(len(targets))]

    def render(self, display: pygame.display, target: list[type[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)

        move = (ps_t / 600) * 120

        for t in target:
            display.blit(self.img_l, (t[0] - 100 + move, t[1] - 40))
            display.blit(self.img_r, (t[0] + 100 - move, t[1] - 40))

