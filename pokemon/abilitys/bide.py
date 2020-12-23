from typing import Union, NoReturn

import gif_manger
import pokemon.abilitys as abilitys
import pygame
import pokemon.player_pokemon as p_poke
import pokemon.battle.battle as battle_
import sound_manager

COORDS = [(-10, 70), (10, 70), (20, 50), (-40, 60), (0, 70)]


class BideAbility(abilitys.AbstractAbility):

    glass: Union[pygame.Surface]
    current_vars: dict
    current_vars_2: list

    def __init__(self):
        super().__init__(id_='bide',
                         type="NORMAL",
                         category="PHYSICAL",
                         pp=20,
                         max_pp=32,
                         power=0,
                         accuracy=-1,
                         snatch=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 2000
        self.need_sound = True
        self.render_type = -1

    def load_assets(self) -> bool:
        if super().load_assets():
            self.current_vars = {}
            self.sound_2 = pygame.mixer.Sound('assets/sound/ability/bide_2.mp3')
            return True
        return False

    def unload_assets(self) -> bool:
        if super().load_assets():
            gif_manger.CONTACT.un_load()
            gif_manger.BIDE.un_load()
            del self.glass
            del self.current_vars
            del self.sound_2
            del self.current_vars_2
            del self.bide_gif
            del self.contact_gif
            return True
        return False

    def get_rac(self, target: list[tuple[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':
        if self.render_type == 2:
            l_move = None
            e_move = None
            if ps_t < 500:
                v = int(15 if ps_t > 300 else 15 * ps_t / 280)
                l_move = launcher[2], v, -v if launcher[1] > 300 else v

            if 400 < ps_t < 1400:
                v = ps_t % 180
                v = -4 if v < 60 else 0 if v < 120 else 4
                e_move = [(t[2], v, 0) for t in target]
            return battle_.RenderAbilityCallback(move_launcher=l_move, move_target=e_move)
        else:
            v = ps_t % 180
            v = -2 if v < 60 else 0 if v < 120 else 2
            return battle_.RenderAbilityCallback(move_launcher=(launcher[2], v, 0),
                                                 color_editor_launcher=(launcher[2], 219, 91, 66, 130))

    def render(self, display: pygame.Surface, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            self.current_vars_2 = [False, False, False]
            self.contact_gif = gif_manger.CONTACT.get().display((target[0][0] - 24, target[0][1] - 60), speed=170)
            self.bide_gif = gif_manger.BIDE.get().display((0, 0), speed=10)
        if self.render_type == 0 or self.render_type == 1:
            if not self.current_vars_2[self.render_type]:
                self.current_vars_2[self.render_type] = True
                sound_manager.start_in_first_empty_taunt(self.sound)
            for i in range(len(COORDS)):
                if (2000 / len(COORDS)) * i < ps_t < (2000 / len(COORDS)) * i + 110:
                    co = COORDS[i]
                    self.bide_gif.render(display, (launcher[0] + co[0] - 64, launcher[1] - co[1] - 64))
        else:
            if not self.current_vars_2[self.render_type]:
                self.current_vars_2[self.render_type] = True
                sound_manager.start_in_first_empty_taunt(self.sound_2)
            if 400 < ps_t < 1300:
                self.contact_gif.render(display)

    def get_damage(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) ->\
            tuple[list[tuple[int, float]], bool, int]:
        if launcher.uuid not in self.current_vars:
            self.current_vars[launcher.uuid] = (2, launcher.heal)
            self.render_type = 0
            self.last_damage = [0] * len(targets)
            return [(0, 1)] * len(targets), False, 0
        elif self.current_vars[launcher.uuid][0] == 2:
            self.current_vars[launcher.uuid] = (1, self.current_vars[launcher.uuid][1])
            self.last_damage = [0] * len(targets)
            self.render_type = 1
            return [(0, 1)] * len(targets), False, 0
        else:
            self.render_type = 2
            damage = max(self.current_vars[launcher.uuid][1] - launcher.heal, 0)
            del self.current_vars[launcher.uuid]
            return [(damage, 1)] * len(targets), False, 0

    def get_nb_turn(self) -> int:
        return 3

