import math
from typing import NoReturn
import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import pokemon.player_pokemon as p_poke
import pokemon.pokemon as poke
import pokemon.status.pokemon_status as pokemon_status
import pygame


class AgilityAbility(abilitys.AbstractAbility):

    def __init__(self):
        super().__init__(id_='agility',
                         type="PSYCHIC",
                         category="STATUS",
                         pp=30,
                         max_pp=48,
                         power=0,
                         accuracy=-1,
                         snatch=True,
                         target=abilitys.TARGET_SELF
                         )
        self.render_during = 1500
        self.need_sound = True

    def get_rac(self, target: list[type[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':

        v = ps_t % 750
        pi_part = ((math.pi * 2) * v / 750) - (math.pi / 2)
        x = int(math.cos(pi_part) * 10)
        y = int(math.sin(pi_part) * 20) + 20

        return battle_.RenderAbilityCallback(move_launcher=(launcher[2], x, y))

    def render(self, display: pygame.Surface, target: list[type[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:

        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) -> tuple[
        tuple[dict[str, int], list['pokemon_status.Status']],
        list[tuple[dict[str, int], list['pokemon_status.Status']]]]:

        return ({}, []), [({poke.SPEED: 2}, [])]
