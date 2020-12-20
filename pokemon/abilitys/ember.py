from typing import NoReturn

import pokemon.abilitys as abilitys
import pygame_gif
import sound_manager
import pokemon.battle.battle as battle_
import pokemon.player_pokemon as p_poke
import pokemon.status.pokemon_status as pokemon_status
import pokemon.status.status as status
import random
import pygame


class EmberAbility(abilitys.AbstractAbility):
    g_i: 'pygame_gif.GifInstance'
    gif: 'pygame_gif.PygameGif'

    def __init__(self):
        super().__init__(id_='ember',
                         type="FIRE",
                         category="SPECIAL",
                         pp=25,
                         max_pp=40,
                         power=40,
                         accuracy=100,
                         protect=True,
                         magic_coat=True,
                         mirror_move=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 2000
        self.need_sound = True

    def load_assets(self) -> bool:
        if super().load_assets():
            self.gif = pygame_gif.PygameGif('assets/textures/ability/ember.gif')
            return True
        return False

    def get_rac(self, target: list[type[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        if ps_t < 1800:
            v = ps_t % 180
            v = -6 if v < 60 else 0 if v < 120 else 6
            target_m = [(t[2], v, 0) for t in target]
            target_c = [(t[2], 219, 91, 66, 130) for t in target]
            return battle_.RenderAbilityCallback(color_editor_target=target_c, move_target=target_m)
        return battle_.RenderAbilityCallback()

    def unload_assets(self) -> bool:
        if super().load_assets():
            del self.gif
            del self.g_i
            return True
        return False

    def get_status_edit(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[tuple[dict[str, int], list['pokemon_status.Status']],
                  list[tuple[dict[str, int], list['pokemon_status.Status']]]]:
        return ({}, []), [({}, [status.BURN] if random.random() < 0.1 else []) for i in range(len(targets))]

    def render(self, display: pygame.display, target: list[type[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            self.g_i = self.gif.display(target[0])
            sound_manager.start_in_first_empty_taunt(self.sound)
        for t in target:
            self.g_i.render(display, (t[0] - 40, t[1] - 120))
