import math
from typing import NoReturn, Union

import game
import pokemon.abilitys as abilitys
import sound_manager
import pokemon.battle.battle as battle_
import pokemon.player_pokemon as p_poke
import pygame


class CounterAbility(abilitys.AbstractAbility):

    img_y: Union[pygame.Surface]

    def __init__(self):
        super().__init__(id_='counter',
                         type="FIGHTING",
                         category="PHYSICAL",
                         pp=20,
                         max_pp=32,
                         power=0,
                         accuracy=100,
                         contact=True,
                         protect=True,
                         target=abilitys.TARGET_ENEMY,
                         is_priority=-5
                         )
        self.render_during = 1500
        self.need_sound = True

    def get_damage(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[list[tuple[int, float]], bool, int]:

        bat = game.game_instance.player.current_battle
        damage = bat.history.get_damage_on(bat.turn_count, launcher.uuid, lambda move: move.get_move().category == "PHYSICAL") * 2
        return [(damage, 1)] * len(targets), False, 0

    def is_fail(self, poke_: 'p_poke.PlayerPokemon', target: 'p_poke.PlayerPokemon'):
        bat = game.game_instance.player.current_battle
        damage = bat.history.get_damage_on(bat.turn_count, poke_.uuid, lambda move: move.get_move().category == "PHYSICAL") * 2
        return damage == 0 or super().is_fail(poke_, target)

    def get_rac(self, target: list[type[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':

        if ps_t < 850:
            v = ps_t % 425
            pi_part = ((math.pi * 2) * v / 750) - (math.pi / 2)
            x = int(math.cos(pi_part) * 10)
            y = int(math.sin(pi_part) * 20) + 20
            return battle_.RenderAbilityCallback(move_launcher=(launcher[2], x, y))
        elif ps_t > 1000:
            v = ps_t % 180
            v = -6 if v < 60 else 0 if v < 120 else 6
            target_m = [(t[2], v, 0) for t in target]
            return battle_.RenderAbilityCallback(move_target=target_m)
        return super().get_rac(target, launcher, ps_t, first_time)

    def load_assets(self) -> bool:
        if super().load_assets():
            self.img_y = pygame.image.load('assets/textures/ability/fist_y.png')
            return True
        return False

    def unload_assets(self) -> bool:
        if super().unload_assets():
            del self.img_y
            return True
        return False

    def render(self, display: pygame.Surface, target: list[type[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:

        if first_time:
            sound_manager.start_in_first_empty_taunt(self.sound)
        if ps_t > 850:
            ps_t -= 850
            size = (1 - min(ps_t / 1000, 1)) * 4 + 1
            sizes = self.img_y.get_size()
            sizes = (int(sizes[0] * size), int(sizes[1] * size))
            im = pygame.transform.scale(self.img_y, sizes)
            for t in target:
                display.blit(im, (t[0] - sizes[0] // 2, t[1] - 40 - sizes[1] // 2))
