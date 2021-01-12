from typing import Union, NoReturn, List

from pygame import Surface
from pygame.mixer import Sound
from pygame.surface import SurfaceType

import game
import gif_manger
import pokemon.abilitys as abilitys
import pygame
import pokemon.player_pokemon as p_poke
import pokemon.battle.battle as battle_
import sound_manager
from pygame_gif import GifInstance

COORDS = [(-10, 70), (10, 70), (20, 50), (-40, 60), (0, 70)]


class DigAbility(abilitys.AbstractAbility):
    g_i: list[GifInstance]
    rock: Union[Surface, SurfaceType]
    sound_2: 'Sound'
    current_vars: dict

    def __init__(self):
        super().__init__(id_='dig',
                         type="GROUND",
                         category="PHYSICAL",
                         pp=10,
                         max_pp=16,
                         power=80,
                         accuracy=100,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=abilitys.TARGET_ENEMY,
                         )
        self.render_during = 1500
        self.need_sound = True
        self.render_type = -1

    def load_assets(self) -> bool:
        if super().load_assets():
            self.current_vars = {}
            self.sound_2 = pygame.mixer.Sound('assets/sound/ability/dig_2.mp3')
            self.rock = pygame.image.load('assets/textures/ability/rock.png')
            return True
        return False

    def unload_assets(self) -> bool:
        if super().unload_assets():
            del self.current_vars
            del self.sound_2
            del self.rock
            gif_manger.CONTACT.un_load()
            del self.g_i
            return True
        return False

    def get_rac(self, target: list[tuple[int, int, int]],
                launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> 'battle_.RenderAbilityCallback':

        pos = battle_.unparse_enemy_case(launcher[2])
        laun = game.game_instance.player.current_battle.get_team(pos[0])[pos[1]]
        status = laun.ram_data.get("dig_status", 0)
        if status <= 1:
            h = 192
            down = int(min(ps_t / 1300, 1) * h)
            return battle_.RenderAbilityCallback(move_launcher=(launcher[2], 0, down), cut_launcher=(launcher[2], True))
        else:
            h = 192
            down = 192 - int(min(ps_t / 600, 1) * h)
            return battle_.RenderAbilityCallback(move_launcher=(launcher[2], 0, down), cut_launcher=(launcher[2], True))

    def render(self, display: pygame.Surface, target: list[tuple[int, int, int]],
               launcher: tuple[int, int, int], ps_t: int, first_time: bool) -> NoReturn:
        pos = battle_.unparse_enemy_case(launcher[2])
        laun = game.game_instance.player.current_battle.get_team(pos[0])[pos[1]]
        status = laun.ram_data.get("dig_status", 0)
        if first_time:
            if status <= 1:
                laun.ram_data["invisible"] = True
                sound_manager.start_in_first_empty_taunt(self.sound)
            else:
                laun.ram_data["invisible"] = False
                laun.ram_data["battle_render_bt"] = True
                sound_manager.start_in_first_empty_taunt(self.sound_2)
                gif = gif_manger.CONTACT.get()
                self.g_i = []
                for t in target:
                    self.g_i.append(gif.display((t[0] - 24, t[1] - 60), speed=71))

        if laun.ram_data.get("dig_status", 0) <= 1:
            if ps_t > 1300:
                laun.ram_data["battle_render_bt"] = False
        else:
            if ps_t > 1000:
                for g in self.g_i:
                    g.render(display)

    def get_damage(self, launcher: "p_poke.PlayerPokemon", targets: list['p_poke.PlayerPokemon']) -> \
            tuple[list[tuple[int, float]], bool, int]:

        status = launcher.ram_data.get("dig_status", 0)
        if status != 1:
            launcher.ram_data["dig_status"] = 1
            return [(0, 1)] * len(targets), False, 0
        else:
            launcher.ram_data["dig_status"] = 2
            return super().get_damage(launcher, targets)



    def get_nb_turn(self) -> int:
        return 2
