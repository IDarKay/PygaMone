import random
from typing import NoReturn

import pokemon.abilitys as abilitys
import pokemon.battle.battle as battle_
import pygame
import pokemon.player_pokemon as p_poke
import pokemon.status.pokemon_status as pokemon_status
import sound_manager

from pokemon.status import status


class ConfusionAbility(abilitys.AbstractAbility):

    def __init__(self):
        super().__init__(id_='confusion',
                         type="PSYCHIC",
                         category="SPECIAL",
                         pp=24,
                         max_pp=40,
                         power=50,
                         accuracy=100,
                         protect=True,
                         mirror_move=True,
                         target=abilitys.TARGET_ENEMY
                         )
        self.render_during = 1500
        self.need_sound = True

    def get_rac(self, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        l_move = None
        l_color = None
        e_move = None
        e_edit = None
        e_color = None
        if 90 <= ps_t <= 580:
            v = ps_t % 180
            v = -4 if v < 60 else 0 if v < 120 else 4
            l_move = launcher[2], v, -v if launcher[1] > 300 else v
            c = (ps_t - 90) // 400
            if c > 1:
                c = 2 - c
            l_color = (255, 255, 255, abs(min(c * 200, 255)))

        if 800 < ps_t < 1470:
            v = ps_t % 180
            v = -4 if v < 60 else 0 if v < 120 else 4
            e_move = [(t[2], v, 0) for t in target]
            ed = (ps_t - 800) / 500
            if ed > 1:
                ed = 2 - ed
            e_edit = [(t[2], 1 - ed * 0.4, 1) for t in target]
            e_color = [(t[2], 255, 255, 255, abs(min(ed * 200, 255))) for t in target]
        return battle_.RenderAbilityCallback(move_launcher=l_move, move_target=e_move, size_edit_target=e_edit,
                                             color_editor_launcher=l_color, color_editor_target=e_color)

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[tuple[dict[str, int], list['pokemon_status.Status']],
                  list[tuple[dict[str, int], list['pokemon_status.Status']]]]:
        return ({}, []), [({}, [status.CONFUSE] if random.random() < 0.1 else []) for _ in range(len(targets))]

    def render(self, display: pygame.display, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)
