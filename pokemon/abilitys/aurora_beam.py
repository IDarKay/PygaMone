from typing import NoReturn

import pokemon.abilitys as abilitys
import pygame_gif
import sound_manager
import pokemon.battle.battle as battle_
import pokemon.player_pokemon as p_poke
import pokemon.pokemon as pokemon
import pokemon.status.pokemon_status as pokemon_status
import random
import pygame

SPEED = 150
COLORS = [
    (3, 223, 252),
    (206, 227, 18),
    (191, 11, 188),
    (66, 98, 143)
]


class AuroraBeamAbility(abilitys.AbstractAbility):
    g_i: 'pygame_gif.GifInstance'
    gif: 'pygame_gif.PygameGif'
    current_vars: list

    def __init__(self):
        super().__init__(id_='aurora_beam',
                         type="ICE",
                         category="SPECIAL",
                         pp=20,
                         max_pp=32,
                         power=65,
                         accuracy=100,
                         protect=True,
                         mirror_move=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 1950
        self.need_sound = True

    def unload_assets(self) -> bool:
        if super().load_assets():
            del self.current_vars
            return True
        return False

    def get_rac(self, target: list[type[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        if 100 < ps_t < 1800:
            v = ps_t % 180
            v = -6 if v < 60 else 0 if v < 120 else 6
            target_m = [(t[2], v, 0) for t in target]
            return battle_.RenderAbilityCallback(move_target=target_m)
        return battle_.RenderAbilityCallback()

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[tuple[dict[str, int], list['pokemon_status.Status']],
                  list[tuple[dict[str, int], list['pokemon_status.Status']]]]:
        return ({}, []), [({pokemon.ATTACK: -1} if random.random() < 0.333333 else {}, []) for _ in range(len(targets))]

    def render(self, display: pygame.display, target: list[type[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            self.current_vars = [random.randint(0, 3) for _ in range(100)]
            sound_manager.start_in_first_empty_taunt(self.sound)

        x1, y1, x2, y2 = launcher[0] + 40, launcher[1] - 50, target[0][0], target[0][1] - 30
        a = (y2 - y1) / (x2 - x1)
        b = y1 - a * x1
        max_delta_x = x2 - x1

        for i in range(100):
            p_i = int((i / 100) * 1950)
            if p_i < ps_t < p_i + SPEED:
                size = (20, 32)
                x = ((ps_t - p_i) / SPEED) * max_delta_x + x1 - size[0] // 2
                y = a * x + b - size[1] // 2
                pygame.draw.ellipse(display, COLORS[self.current_vars[i]], (x, y, size[0], size[1]), 5)