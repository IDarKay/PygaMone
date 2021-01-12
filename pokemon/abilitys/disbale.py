import random
from typing import NoReturn, Union

import pokemon.abilitys as abilitys
import sound_manager
import pygame
import pokemon.player_pokemon as p_poke


class DisableAbility(abilitys.AbstractAbility):

    shine: Union[pygame.Surface]
    current_vars: list

    def __init__(self):
        super().__init__(id_='disable',
                         type="NORMAL",
                         category="STATUS",
                         pp=20,
                         max_pp=32,
                         power=0,
                         accuracy=80,
                         protect=True,
                         magic_coat=True,
                         mirror_move=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 1100
        self.need_sound = True

    def get_damage(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[list[tuple[int, float]], bool, int]:
        if len(targets) > 0:
            first = targets[0]
            abs = []
            for i in range(len(first.ability)):
                if (a := first.ability[i]) is not None and a.pp > 0:
                    abs.append(i)
            if len(abs) > 0:
                ab = abs[random.randint(0, len(abs) - 1)]
                first.ram_data["disable_ab"] = [ab, random.randint(4, 7)]

        return super().get_damage(launcher, targets)

    def is_fail(self, poke_: 'p_poke.PlayerPokemon', target: 'p_poke.PlayerPokemon'):
        disable = target.ram_data.get("disable_ab", [])
        if (len(disable) > 0 and disable[1] != 0) or sum(map(lambda ab: ab is not None and ab.pp > 0, target.ability)) == 0:
            return True
        else:
            return super().is_fail(poke_, target)

    def render(self, display: pygame.Surface, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)

        opa = int(((550 - abs(550 - ps_t)) / 550) * 180)
        sur = pygame.Surface(display.get_size(), pygame.SRCALPHA)
        sur.fill((0, 0, 0))
        sur.set_alpha(opa)
        display.blit(sur, (0, 0))

        im = self.shine.copy()
        im.set_alpha(opa)
        display.blit(im, (launcher[0] + 20, launcher[1] - 110))

    def load_assets(self) -> bool:
        if super().load_assets():
            self.shine = pygame.image.load('assets/textures/ability/shine.png').convert_alpha()
            return True
        return False

    def unload_assets(self) -> bool:
        if super().unload_assets():
            del self.shine
            del self.current_vars
            return True
        return False