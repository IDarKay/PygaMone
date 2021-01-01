from typing import NoReturn, Union
import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import pokemon.player_pokemon as p_poke
import pokemon.pokemon as poke
import pokemon.status.pokemon_status as pokemon_status
import random
import pygame

SPEED = 200


class BubbleBeamAbility(abilitys.AbstractAbility):

    ball: Union[pygame.Surface]

    def __init__(self):
        super().__init__(id_='bubble_beam',
                         type="WATER",
                         category="SPECIAL",
                         pp=20,
                         max_pp=32,
                         power=65,
                         accuracy=100,
                         protect=True,
                         mirror_move=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 2300
        self.need_sound = True

    def get_rac(self, target: list[tuple[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        if ps_t > SPEED:
            v = ps_t % 180
            v = -3 if v < 60 else 0 if v < 120 else 3
            target_m = [(t[2], v, 0) for t in target]
            target_c = [(t[2], 57, 145, 227, 130) for t in target]
            return battle_.RenderAbilityCallback(color_editor_target=target_c, move_target=target_m)
        return battle_.RenderAbilityCallback()

    def load_assets(self) -> bool:
        if super().load_assets():
            self.ball = pygame.image.load('assets/textures/ability/bubble.png')
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
            self.current_vars = [random.randint(-40, 40) for _ in range(80)]
            sound_manager.start_in_first_empty_taunt(self.sound)

        for t_i in range(len(target)):

            x1, x2, y2 = launcher[0] + 40, target[t_i][0], target[t_i][1] - 30

            for i in range(80):
                i_60 = int((i / 80) * (2300 - SPEED))
                if i_60 < ps_t < i_60 + SPEED:
                    y1 = launcher[1] - 50
                    a = (y2 - y1) / (x2 - x1)
                    b = y1 - a * x1
                    max_delta_x = x2 - x1
                    size = (self.ball, 32, 32)
                    x = x1 + ((ps_t - i_60) / SPEED) * max_delta_x - size[1] // 2
                    y = a * x + b - size[1] // 2 + self.current_vars[i]
                    display.blit(size[0], (x, y))

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) -> tuple[
        tuple[dict[str, int], list['pokemon_status.Status']],
        list[tuple[dict[str, int], list['pokemon_status.Status']]]]:

        return ({}, []), [(({poke.SPEED: -1} if random.random() < (1/3) else {}), [])]
