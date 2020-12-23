from typing import NoReturn, Union

import pokemon.abilitys as abilitys
import sound_manager
import pygame
import pokemon.pokemon as poke
import pokemon.player_pokemon as p_poke
import pokemon.status.pokemon_status as pokemon_status


class BarrierAbility(abilitys.AbstractAbility):

    glass: Union[pygame.Surface]
    current_vars: list

    def __init__(self):
        super().__init__(id_='barrier',
                         type="PSYCHIC",
                         category="STATUS",
                         pp=20,
                         max_pp=32,
                         power=0,
                         accuracy=-1,
                         snatch=True,
                         target=abilitys.TARGET_SELF,
                         )
        self.render_during = 2400
        self.need_sound = True

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) -> tuple[
        tuple[dict[str, int], list['pokemon_status.Status']],
        list[tuple[dict[str, int], list['pokemon_status.Status']]]]:

        return ({}, []), [({poke.DEFENSE: 2}, [])]

    def render(self, display: pygame.Surface, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)

        size = ps_t / 1500
        if size < 1:
            display.blit(pygame.transform.scale(self.glass, (int(self.glass.get_size()[0] * size),
                                                             int(self.glass.get_size()[1] * size))),
                         (launcher[0] + 20 - 64 * size, launcher[1] - 80 - 64 * size))
        else:
            display.blit(self.glass, (launcher[0] - 44, launcher[1] - 144))

    def load_assets(self) -> bool:
        if super().load_assets():
            self.glass = pygame.image.load('assets/textures/ability/barrier.png')
            return True
        return False

    def unload_assets(self) -> bool:
        if super().load_assets():
            del self.glass
            del self.current_vars
            return True
        return False