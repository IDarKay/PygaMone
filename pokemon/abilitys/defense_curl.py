import math
from typing import NoReturn
import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import pokemon.player_pokemon as p_poke
import pokemon.pokemon as poke
import pokemon.status.pokemon_status as pokemon_status
import pygame


class DefenseCurlAbility(abilitys.AbstractAbility):

    def __init__(self):
        super().__init__(id_='defense_curl',
                         type="NORMAL",
                         category="STATUS",
                         pp=40,
                         max_pp=64,
                         power=0,
                         accuracy=-1,
                         snatch=True,
                         target=abilitys.TARGET_SELF
                         )
        self.render_during = 1100
        self.need_sound = True

    def get_rac(self, target: list[type[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':

        if 50 < ps_t < 950:
            progress = ps_t % 300
            if progress <= 100:
                height = 1 - (progress / 100) * 0.4
            else:
                height = min(((progress - 100) / 180), 1) * 0.4 + 0.6
            return battle_.RenderAbilityCallback(size_edit_launcher=(launcher[2], 1, height))
        return battle_.RenderAbilityCallback()

    def render(self, display: pygame.Surface, target: list[type[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:

        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) -> tuple[
        tuple[dict[str, int], list['pokemon_status.Status']],
        list[tuple[dict[str, int], list['pokemon_status.Status']]]]:

        return ({}, []), [({poke.DEFENSE: 1}, [])]
