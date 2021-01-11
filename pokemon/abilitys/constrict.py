import random
from typing import NoReturn, Union

from pygame import Surface
from pygame.surface import SurfaceType

import pokemon.abilitys as abilitys
import pygame
import pokemon.player_pokemon as p_poke
import pokemon.status.pokemon_status as pokemon_status
import sound_manager
from pokemon import pokemon


class ConstrictAbility(abilitys.AbstractAbility):

    img: Union[Surface, SurfaceType]

    def __init__(self):
        super().__init__(id_='constrict',
                         type="NORMAL",
                         category="PHYSICAL",
                         pp=35,
                         max_pp=56,
                         power=10,
                         accuracy=100,
                         protect=True,
                         mirror_move=True,
                         target=abilitys.TARGET_ENEMY
                         )
        self.render_during = 1200
        self.need_sound = True

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[tuple[dict[str, int], list['pokemon_status.Status']],
                  list[tuple[dict[str, int], list['pokemon_status.Status']]]]:
        return ({}, []), [({pokemon.SPEED: -1} if random.random() < 0.333333 else {}, []) for _ in range(len(targets))]

    def load_assets(self) -> bool:
        if super().load_assets():
            self.img = pygame.image.load('assets/textures/ability/constrict.png')
            return True
        return False

    def unload_assets(self) -> bool:
        if super().load_assets():
            del self.img
            return True
        return False

    def render(self, display: pygame.display, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)

        ed = ps_t / 400
        ed *= 0.4
        if ed > 1:
            ed = ed - int(ed)
            if ed % 2 == 0:
                ed = 1 - ed
            else:
                ed += 0.6
        else:
            ed *= 0.6
        im = pygame.transform.scale(self.img, (int(self.img.get_size()[0] * ed), self.img.get_size()[1]))
        for t in target:
            display.blit(im, (t[0] - im.get_size()[0] // 2, t[1] - 60))
