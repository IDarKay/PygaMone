import math
from typing import NoReturn, Union

import pokemon.abilitys as abilitys
import sound_manager
import pygame
import pokemon.pokemon as poke
import pokemon.player_pokemon as p_poke
import pokemon.status.pokemon_status as pokemon_status
import utils
from pokemon.battle import battle as battle_
from pokemon.status import status

COLORS = [
    "EAEF33", "C2EF34", "99EF34", "71F034", "49F034", "34F148", "34F171", "34F29A", "34F2C3", "34F2C3"
]


class ConfuseRayAbility(abilitys.AbstractAbility):

    orb: Union[pygame.Surface]

    def __init__(self):
        super().__init__(id_='confuse_ray',
                         type="GHOST",
                         category="STATUS",
                         pp=10,
                         max_pp=16,
                         power=0,
                         accuracy=-1,
                         protect=True,
                         magic_coat=True,
                         mirror_move=True,
                         target=abilitys.TARGET_ENEMY
                         )
        self.render_during = 2500
        self.need_sound = True

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[tuple[dict[str, int], list['pokemon_status.Status']],
                  list[tuple[dict[str, int], list['pokemon_status.Status']]]]:
        return ({}, []), [({}, [status.CONFUSE]) for _ in range(len(targets))]

    def render(self, display: pygame.Surface, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)

        x1, y1 = launcher[0] + 40, launcher[1] - 50
        x2, y2 = target[0][0], target[0][1] - 30
        a = (y2 - y1) / (x2 - x1)
        b = y1 - a * x1
        max_delta_x = x2 - x1

        color = (*utils.hexa_color_to_rgb(COLORS[((ps_t % 100) // 10) * (1 if (ps_t // 100) % 2 else -1)]), 180)

        im = utils.color_image(self.orb.copy(), color)

        if ps_t < 1900:
            x = min((ps_t / 1900), 1) * max_delta_x + x1
            y = (a * x + b) + (0.0005 * (x - x1) * (x - x2))

            display.blit(im, (x - 32, y - 32))
        else:
            p = min(((ps_t - 1900) / 550), 1.0) * math.pi * 2
            x, y = math.cos(p) * 20, math.sin(p) * 10
            display.blit(im, (x2 - 32 + x, y2 - 32 + y))

    def load_assets(self) -> bool:
        if super().load_assets():
            self.orb = pygame.image.load('assets/textures/ability/orb.png').convert_alpha()
            return True
        return False

    def unload_assets(self) -> bool:
        if super().unload_assets():
            del self.orb
            return True
        return False
