from typing import NoReturn, Union
import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import pokemon.player_pokemon as p_poke
import pokemon.pokemon as poke
import pokemon.status.pokemon_status as pokemon_status
import random
import pygame


class AcidAbility(abilitys.AbstractAbility):

    ball: Union[pygame.Surface]

    def __init__(self):
        super().__init__(id_='acid',
                         type="POISON",
                         category="SPECIAL",
                         pp=30,
                         max_pp=48,
                         power=40,
                         accuracy=100,
                         protect=True,
                         mirror_move=True,
                         target=abilitys.TARGET_ENEMY,
                         range=abilitys.RANGE_TWO
                         )
        self.render_during = 2000
        self.need_sound = True

    def get_rac(self, target: list[type[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        if ps_t > 900:
            v = ps_t % 180
            v = -3 if v < 60 else 0 if v < 120 else 3
            target_m = [(t[2], v, 0) for t in target]
            target_c = [(t[2], 209, 44, 168, 130) for t in target]
            return battle_.RenderAbilityCallback(color_editor_target=target_c, move_target=target_m)
        return battle_.RenderAbilityCallback()

    def load_assets(self) -> bool:
        if super().load_assets():
            self.ball = pygame.image.load('assets/textures/ability/purple_ball.png')
            print(self.ball.get_size())
            return True
        return False

    def unload_assets(self) -> bool:
        if super().load_assets():
            del self.ball
            return True
        return False

    def render(self, display: pygame.Surface, target: list[type[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:

        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)

        # x = ax + b
        x1, y1 = launcher[0] + 40, launcher[1] - 50
        x2, y2 = target[0][0], target[0][1] - 30
        a = (y2 - y1) / (x2 - x1)
        b = y1 - a*x1
        max_delta_x = x2 - x1

        for i in [0, 200, 400]:
            if 1000 + i > ps_t > i:
                x = ((ps_t - i) / 1000) * max_delta_x + x1
                y = a * x + b
                display.blit(self.ball, (x - 16, y - 16))
                # pygame.draw.circle(display, (209, 44, 168), (x, y), 10)

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) -> tuple[
        tuple[dict[str, int], list['pokemon_status.Status']],
        list[tuple[dict[str, int], list['pokemon_status.Status']]]]:

        return ({}, []), [(({poke.DEFENSE: -1} if random.random() < (1/3) else {}) |
                           ({poke.SP_DEFENSE: -1} if random.random() < 0.1 else {}), [])]
