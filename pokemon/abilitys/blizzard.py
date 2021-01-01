from typing import NoReturn

import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import pokemon.player_pokemon as p_poke
import pokemon.status.pokemon_status as pokemon_status
import pokemon.status.status as status
import random
import pygame

SPEED = 500


class BlizzardAbility(abilitys.AbstractAbility):
    shard: pygame.Surface

    def __init__(self):
        super().__init__(id_='blizzard',
                         type="ICE",
                         category="SPECIAL",
                         pp=5,
                         max_pp=8,
                         power=110,
                         accuracy=70,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         target=abilitys.TARGET_ENEMY
                         )
        self.render_during = 1500
        self.need_sound = True

    def get_rac(self, target: list[type[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        if SPEED < ps_t:
            v = ps_t % 180
            v = -6 if v < 60 else 0 if v < 120 else 6
            target_m = [(t[2], v, 0) for t in target]
            target_c = [(t[2], 29, 153, 191, 130) for t in target]
            return battle_.RenderAbilityCallback(color_editor_target=target_c, move_target=target_m)
        return battle_.RenderAbilityCallback()

    def load_assets(self) -> bool:
        if super().load_assets():
            self.shard = pygame.image.load('assets/textures/ability/shard.png')
            return True
        return False

    def unload_assets(self) -> bool:
        if super().load_assets():
            del self.shard
            return True
        return False

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[tuple[dict[str, int], list['pokemon_status.Status']],
                  list[tuple[dict[str, int], list['pokemon_status.Status']]]]:
        return ({}, []), [({}, [status.FREEZE] if random.random() < 0.1 else []) for _ in range(len(targets))]

    def render(self, display: pygame.Surface, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            self.current_vars = [random.randint(-40, 40) for _ in range(60)]
            sound_manager.start_in_first_empty_taunt(self.sound)

        if ps_t < 1000:
            x1, x2, y2 = launcher[0] + 40, target[0][0], target[0][1] - 30

            for i in range(60):
                i_60 = int((i / 60) * (1000 - SPEED))
                if i_60 < ps_t < i_60 + SPEED:
                    y1 = launcher[1] - 50 + self.current_vars[i]
                    a = (y2 - y1) / (x2 - x1)
                    b = y1 - a * x1

                    max_delta_x = -b/a - x1

                    size = (self.shard, 32, 32)
                    x = x1 + ((ps_t - i_60) / SPEED) * max_delta_x - size[1] // 2
                    y = a * x + b - size[1] // 2
                    display.blit(size[0], (x, y))