from typing import NoReturn, Union

import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import pokemon.player_pokemon as p_poke
import pokemon.pokemon as poke
import pokemon.status.pokemon_status as pokemon_status
import random
import pygame

SPEED_2 = 300


class AcidArmorAbility(abilitys.AbstractAbility):
    ball: Union[pygame.Surface]
    current_vars: list

    def __init__(self):
        super().__init__(id_='acid_armor',
                         type="POISON",
                         category="STATUS",
                         pp=20,
                         max_pp=32,
                         power=0,
                         accuracy=-1,
                         snatch=True,
                         target=abilitys.TARGET_SELF,
                         )
        self.render_during = 2000
        self.need_sound = True

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) -> tuple[
        tuple[dict[str, int], list['pokemon_status.Status']],
        list[tuple[dict[str, int], list['pokemon_status.Status']]]]:

        return ({}, []), [({poke.DEFENSE: 2}, [])]

    def get_rac(self, target: list[type[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        print((1 - (ps_t / 1800)) * 0.5)
        x = max((1 - (ps_t / 1800)) * 0.25, 0) + 0.75
        y = max((1 - (ps_t / 1800)) * 0.5, 0) + 0.5
        return battle_.RenderAbilityCallback(size_edit_launcher=(launcher[2], x, y))

    def render(self, display: pygame.display, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            self.current_vars = [(random.randint(-100, 0), random.randint(0, 30)) for _ in range(15)]
            sound_manager.start_in_first_empty_taunt(self.sound)

        if ps_t > 1000:
            for i in range(15):
                i_15 = int((i / 15) * (1000 - SPEED_2))
                if i_15 + 1000 < ps_t < i_15 + SPEED_2 + 1000:
                    x = launcher[0] + 40 + self.current_vars[i][0]
                    y = launcher[1] - 50 + self.current_vars[i][1] - ((ps_t - 1000 - i_15) / SPEED_2) * 80
                    display.blit(self.ball, (x, y))

    def load_assets(self) -> bool:
        if super().load_assets():
            self.ball = pygame.image.load('assets/textures/ability/purple_ball.png')
            return True
        return False

    def unload_assets(self) -> bool:
        if super().load_assets():
            del self.ball
            del self.current_vars
            return True
        return False