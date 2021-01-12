from typing import NoReturn, Union

import gif_manger
import pokemon.abilitys as abilitys
import sound_manager
import pokemon.player_pokemon as p_poke
import pokemon.status.pokemon_status as pokemon_status
import random
import pygame_gif
import pygame
from pokemon.status import status


class BoneClubAbility(abilitys.AbstractAbility):

    g_i: 'pygame_gif.GifInstance'
    bone: Union[pygame.Surface]

    def __init__(self):
        super().__init__(id_='bone_club',
                         type="GROUND",
                         category="PHYSICAL",
                         pp=20,
                         max_pp=32,
                         power=65,
                         accuracy=85,
                         protect=True,
                         mirror_move=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 1000
        self.need_sound = True

    def load_assets(self) -> bool:
        if super().load_assets():
            self.bone = pygame.image.load('assets/textures/ability/bone.png')
            gif_manger.CONTACT.load()
            return True
        return False

    def unload_assets(self) -> bool:
        if super().unload_assets():
            del self.bone
            gif_manger.CONTACT.un_load()
            return True
        return False

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[tuple[dict[str, int], list['pokemon_status.Status']],
                  list[tuple[dict[str, int], list['pokemon_status.Status']]]]:
        return ({}, []), [({}, [status.FLINCH] if random.random() < 0.1 else []) for _ in range(len(targets))]

    def render(self, display: pygame.display, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)
            self.g_i = gif_manger.CONTACT.get().display((target[0][0] - 60, target[0][1] - 60), 25)

        x1, y1 = launcher[0] + 40, launcher[1] - 50
        x2, y2 = target[0][0], target[0][1] - 30
        a = (y2 - y1) / (x2 - x1)
        b = y1 - a * x1
        max_delta_x = x2 - x1

        x = min((ps_t / 950), 1) * max_delta_x + x1
        y = (a * x + b) + (0.002 * (x - x1) * (x - x2))
        display.blit(pygame.transform.rotate(self.bone, (ps_t % 300) / 300 * 360), (x - 32, y - 32))

        if ps_t > 850:
            self.g_i.render(display)
