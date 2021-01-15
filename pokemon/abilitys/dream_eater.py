from typing import NoReturn

import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import random
import pygame
import pokemon.player_pokemon as p_poke
from pokemon.status import pokemon_status

SPEED = 500
SPEED_2 = 300


class DreamEaterAbility(abilitys.AbstractAbility):
    yellow_stars: list[tuple[pygame.surface, int]]
    current_vars: list

    def __init__(self):
        super().__init__(id_='dream_eater',
                         type="PSYCHIC",
                         category="SPECIAL",
                         pp=15,
                         max_pp=24,
                         power=100,
                         accuracy=100,
                         protect=True,
                         mirror_move=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 2000
        self.need_sound = True

    def load_assets(self) -> bool:
        if super().load_assets():
            img = pygame.image.load('assets/textures/ability/yellow_stars.png')
            self.yellow_stars = [(pygame.transform.scale(img, (8, 8)), 8),
                                 (pygame.transform.scale(img, (16, 16)), 16),
                                 (img, 32),
                                 (pygame.transform.scale(img, (48, 48)), 48)
                                 ]
            return True
        return False

    def is_fail(self, poke: 'p_poke.PlayerPokemon', target: 'p_poke.PlayerPokemon'):
        return super().is_fail(poke, target) or not target.combat_status.have_status(pokemon_status.status_.SLEEP)

    def unload_assets(self) -> bool:
        if super().unload_assets():
            del self.yellow_stars
            del self.current_vars
            return True
        return False

    def get_rac(self, target: list[type[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        if ps_t > 2000:
            return battle_.RenderAbilityCallback(color_editor_launcher=(launcher[2], 168, 162, 50, 100))
        return battle_.RenderAbilityCallback()

    def render(self, display: pygame.Surface, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            self.current_vars = [
                [random.randint(0, 3) for _ in range(80)],
                [random.randint(-40, 40) for _ in range(80)],
                [(random.randint(-100, 100), random.randint(-50, 30)) for _ in range(15)],
                self.last_launcher.heal,
                min(self.last_launcher.get_max_heal(), self.last_launcher.heal + max(1, self.last_damage[0] // 2))
            ]
            sound_manager.start_in_first_empty_taunt(self.sound)

        if ps_t < 2000:
            x1, x2, y2 = launcher[0] + 40, target[0][0], target[0][1] - 30

            max_delta_x = x2 - x1
            for i in range(80):
                i_60 = int((i / 80) * (2000 - SPEED))
                if i_60 < ps_t < i_60 + SPEED:
                    y1 = launcher[1] - 50 + self.current_vars[1][i]
                    a = (y2 - y1) / (x2 - x1)
                    b = y1 - a * x1
                    size = self.yellow_stars[self.current_vars[0][i]]
                    x = x2 - ((ps_t - i_60) / SPEED) * max_delta_x - size[1] // 2
                    y = a * x + b - size[1] // 2
                    display.blit(size[0], (x, y))
        elif ps_t < 3000:
            for i in range(15):
                i_15 = int((i / 15) * (1000 - SPEED_2))
                if i_15 + 2000 < ps_t < i_15 + SPEED_2 + 1000:
                    x = launcher[0] + 40 + self.current_vars[2][i][0]
                    y = launcher[1] - 50 + self.current_vars[2][i][1] - ((ps_t - 2000 - i_15) / SPEED_2) * 80
                    size = self.yellow_stars[self.current_vars[0][i]]
                    display.blit(size[0], (x, y))
            if 2200 < ps_t < 2900:
                heal = int((self.current_vars[4] - self.current_vars[3]) * ((ps_t - 2200) / 700)) + self.current_vars[3]
                self.last_launcher.heal = heal
            else:
                self.last_launcher.heal = self.current_vars[4]
