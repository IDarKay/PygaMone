import math
from typing import NoReturn
import pokemon.abilitys as abilitys
import pygame_gif
import sound_manager
import pokemon.battle.battle as battle_
import pokemon.player_pokemon as p_poke
import pokemon.pokemon as poke
import pokemon.status.pokemon_status as pokemon_status
import pygame


class AmnesiaAbility(abilitys.AbstractAbility):
    g_i: 'pygame_gif.GifInstance'
    gif: 'pygame_gif.PygameGif'

    def __init__(self):
        super().__init__(id_='amnesia',
                         type="PSYCHIC",
                         category="STATUS",
                         pp=20,
                         max_pp=32,
                         power=0,
                         accuracy=-1,
                         snatch=True,
                         target=abilitys.TARGET_SELF
                         )

        self.render_during = 1250
        self.need_sound = True

    def load_assets(self) -> bool:
        if super().load_assets():
            self.gif = pygame_gif.PygameGif('assets/textures/ability/amnesia.gif')
            return True
        return False

    def unload_assets(self) -> bool:
        if super().load_assets():
            del self.gif
            del self.g_i
            return True
        return False

    def render(self, display: pygame.display, target: list[type[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            self.g_i = self.gif.display(target[0], speed=1250//11)
            sound_manager.start_in_first_empty_taunt(self.sound)
        for t in target:
            self.g_i.render(display, (t[0] - 20, t[1] - 190))

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) -> tuple[
        tuple[dict[str, int], list['pokemon_status.Status']],
        list[tuple[dict[str, int], list['pokemon_status.Status']]]]:

        return ({}, []), [({poke.SP_DEFENSE: 2}, [])]