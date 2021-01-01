import random
from typing import NoReturn

import pokemon.abilitys as abilitys
import gif_manger
import sound_manager
import pokemon.battle.battle as battle_
import pygame
import pokemon.player_pokemon as p_poke
import pokemon.status.pokemon_status as pokemon_status

from pokemon.status import status


class BodySlamAbility(abilitys.AbstractAbility):

    def __init__(self):
        super().__init__(id_='body_slam',
                         type="NORMAL",
                         category="PHYSICAL",
                         pp=15,
                         max_pp=24,
                         power=85,
                         accuracy=100,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         target=abilitys.TARGET_ENEMY)

        self.render_during = 1550
        self.need_sound = True
        self.__data: list[bool] = [False]

    def get_rac(self, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':

        x1, y1 = launcher[0] + 40, launcher[1] - 50
        x2, y2 = target[0][0], target[0][1] - 30
        a = (y2 - y1) / (x2 - x1)
        b = y1 - a * x1
        max_delta_x = x2 - x1
        e_size = None
        x = int(min((ps_t / 1400), 1) * max_delta_x + x1)
        y = int((a * x + b) + (0.01 * (x - x1) * (x - x2)))
        l_move = launcher[2], x - launcher[0], y - launcher[1]
        if 1300 < ps_t:
            x = 1
            y = max((1 - (ps_t - 1300 / 250)) * 0.8, 0) + 0.2
            e_size = [(target[i][2], x, y) for i in range(len(target))]
        return battle_.RenderAbilityCallback(move_launcher=l_move, size_edit_target=e_size)

    def unload_assets(self) -> bool:
        if super().load_assets():
            gif_manger.CONTACT.un_load()
            return True
        return False

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[tuple[dict[str, int], list['pokemon_status.Status']],
                  list[tuple[dict[str, int], list['pokemon_status.Status']]]]:
        return ({}, []), [({}, [status.PARALYSIS] if random.random() < 0.1 else []) for _ in range(len(targets))]

    def render(self, display: pygame.display, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)
