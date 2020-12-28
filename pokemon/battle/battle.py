from typing import List, Tuple, NoReturn, Callable, Optional, Union, Any

from pygame import Surface

from hud import bag
from pokemon.battle import evolution_animaiton
from pokemon.battle.animation import Animation
import pokemon.player_pokemon as player_pokemon
import pokemon.pokemon
import utils
import pygame
import game
import item
import pokemon.battle.background as background
import pokemon.abilitys as ability
import hud.hud as hud
import hud.menu as menu__
import sounds
import sound_manager
import random
import character.npc as NPC_
from hud.battle_menu import ChangePokemonMenu
import pokemon.battle.xp_battle_animation as xp_battle_animation

SURFACE_SIZE = (1060, 600)

# 130 / 40
BASE_SIZES = ((390, 120), (390, 120), (325, 100))
GRASS_PLATE_BASE = (353, 80, 483, 120)


class StartAnimation(object):

    def __init__(self):
        pass

    def get_during(self) -> Tuple[int, int]:
        return 0, 0

    def load_asset(self):
        pass

    def tick(self, display: pygame.Surface, battle_: 'Battle', ps_t: int) -> NoReturn:
        pass


class WildAnimation(StartAnimation):
    BALL_SPEED = (400, 900, 1500, 600, 1200, 1300, 500, 950)
    START_POINT: Tuple[int, int] = (0, SURFACE_SIZE[0] - 390)

    def __init__(self):
        super().__init__()
        self.__opening: Optional[pygame.Surface] = None
        self.__opening_w: Optional[Tuple[int, int]] = None

    def load_asset(self):
        self.__opening = pygame.image.load('assets/textures/battle/grass_start.png')
        self.__opening_w = self.__opening.get_rect().size

    def get_during(self) -> Tuple[int, int]:
        return 2000, 4100
        # return 100, 100

    def tick(self, display: pygame.Surface, battle_: 'Battle', ps_t: int) -> NoReturn:
        if battle_.bool_matrix[0]:
            battle_.bool_matrix[0] = False
            sound_manager.MUSIC_CHANNEL.play(battle_.start_sound)
        if ps_t <= 500:
            if ps_t // 100 % 2 == 0:
                s = pygame.Surface(game.SURFACE_SIZE)
                s.fill((200, 200, 200))
                s.set_alpha(100)
                display.blit(s, (0, 0))
        elif ps_t <= 2100:
            ps_t -= 500
            h = game.SURFACE_SIZE[1] // 8
            for i in range(8):
                progress = int(game.SURFACE_SIZE[0] * (min(1.0, ps_t / WildAnimation.BALL_SPEED[i])))
                start = 0 if i % 2 == 0 else game.SURFACE_SIZE[0] - progress
                pygame.draw.rect(display, (0, 0, 0), pygame.Rect(start, h * i, progress, h))
                if i % 2 == 0:
                    display.blit(battle_.poke_ball, (progress - h, h * i))
                else:
                    display.blit(battle_.poke_ball, (game.SURFACE_SIZE[0] - progress, h * i))
        else:
            battle_.draw_bg(display)
            ps_t -= 2100
            y = game.SURFACE_SIZE[1] * 0.7
            if ps_t >= 1000:
                y += (game.SURFACE_SIZE[1] * 0.3 + 200) * min(1.0, (ps_t - 1000) / 1500)
                # BASE
                base_x = WildAnimation.START_POINT[0] + (
                        battle_.bg.enemy_base_coord[battle_.nb_enemy - 1][0][0] - WildAnimation.START_POINT[0]) * \
                         min(1.0, (ps_t - 1000) / 1000)
                base_x_2 = WildAnimation.START_POINT[1] - (
                        WildAnimation.START_POINT[1] - battle_.bg.ally_base_coord[battle_.nb_enemy - 1][0][0]) * \
                           min(1.0, (ps_t - 1000) / 1000)
                battle_.draw_base(display, base_x, enemy=True)
                battle_.draw_base(display, base_x_2, enemy=False)

                # add 0 to ignore div by 0
            x = (self.__opening_w[0] - game.SURFACE_SIZE[0]) * ((ps_t % 2000) / 2000)
            display.blit(self.__opening, (0, y), pygame.Rect(x, 0, x + self.__opening_w[0], self.__opening_w[1]))

            if ps_t < 1000:
                h = game.SURFACE_SIZE[1] // 4 * (1 - ps_t / 1000)
                if h < 0:
                    h = 0
                pygame.draw.rect(display, (0, 0, 0), (0, 0, game.SURFACE_SIZE[0], h + game.SURFACE_SIZE[1] // 3))
                pygame.draw.rect(display, (0, 0, 0),
                                 (0, game.SURFACE_SIZE[1] - h, game.SURFACE_SIZE[0], game.SURFACE_SIZE[1]))


class RenderAbilityCallback(object):

    def __init__(self, move_target: Optional[List[Tuple[int, int, int]]] = None,
                 move_launcher: Tuple[int, int, int] = None,
                 color_editor_target: List[Union[Tuple[int, int, int, int], Tuple[int, int, int, int, int]]] = None,
                 color_editor_launcher: Union[Tuple[int, int, int, int], Tuple[int, int, int, int, int]] = None,
                 size_edit_launcher: tuple[int, float, float] = None,
                 size_edit_target: List[tuple[int, float, float]] = None
                 ):
        self.move_target = move_target
        self.move_launcher = move_launcher
        self.color_editor_target = color_editor_target
        self.color_editor_launcher = color_editor_launcher
        self.size_edit_launcher = size_edit_launcher
        self.size_edit_target = size_edit_target

    def get_resize(self, enemy: bool, case) -> Optional[tuple[int, float, float]]:
        v = parse_enemy_case(enemy, case)
        if self.size_edit_launcher and self.size_edit_launcher[0] == v:
            return self.size_edit_launcher
        if self.size_edit_target:
            for mv in self.size_edit_target:
                if mv[0] == v:
                    return mv
        return None

    def get_all(self, enemy: bool, case) \
            -> tuple[tuple[int, int, int], Union[tuple[int, int, int, int], tuple[int, int, int, int, int]]]:
        return self.get_move(enemy, case), self.get_color(enemy, case)

    def get_color(self, enemy: bool, case) -> Optional[
        Union[tuple[int, int, int, int], tuple[int, int, int, int, int]]]:
        v = parse_enemy_case(enemy, case)
        if self.color_editor_launcher and self.color_editor_launcher[0] == v:
            return self.color_editor_launcher
        if self.color_editor_target:
            for c in self.color_editor_target:
                if c[0] == v:
                    return c
        return None

    def get_move(self, enemy: bool, case) -> tuple[int, int, int]:
        v = parse_enemy_case(enemy, case)
        if self.move_launcher and self.move_launcher[0] == v:
            return self.move_launcher
        if self.move_target:
            for mv in self.move_target:
                if mv[0] == v:
                    return mv
        return v, 0, 0


class SimpleDialogue(Animation):

    def __init__(self, msg: str, text_var: list[object] = [], during: int = 1500):
        self.during = during
        self.dialog = hud.Dialog(msg, need_morph_text=True, speed=20, none_skip=True, style=2,
                                 text_var=text_var)
        self.init = False

    def tick(self, display: pygame.Surface) -> bool:
        if not self.init:
            self.init = True
            self.start = utils.current_milli_time()
            game.game_instance.player.open_dialogue(self.dialog)
            return False
        if utils.current_milli_time() - self.start >= self.during:
            game.game_instance.player.close_dialogue()
            return True
        return False


class StatusRemoveAnimation(Animation):

    def __init__(self, status, poke: 'player_pokemon.PlayerPokemon', ally: bool):
        self.ally = ally
        self.status = status
        self.poke = poke
        self.init = False

    def tick(self, display: pygame.Surface) -> bool:
        if not self.init:
            self.init = True
            self.poke.combat_status.remove(self.status)
            self.start = utils.current_milli_time()
            text = self.status.get_end_text(self.ally)
            if text:
                d = hud.Dialog(text, need_morph_text=True, speed=20, none_skip=True, style=2,
                               text_var=[self.poke.get_name(True)])
                game.game_instance.player.open_dialogue(d)
            return False
        if utils.current_milli_time() - self.start >= 1500:
            game.game_instance.player.close_dialogue()
            return True
        return False


class StatusDamageAnimation(Animation):

    def __init__(self, si, amount: int, pos: tuple[int, int], ally: bool):
        self.amount = amount
        self.ally = ally
        self.status = si.status
        self.poke = si.poke
        self.animation = self.status.get_animation(si, pos)
        self.init = False

    def tick(self, display: pygame.Surface) -> bool:
        if not self.init:
            self.init = True
            self.start = utils.current_milli_time()
            text = self.status.get_damage_text(self.ally)
            if text:
                if self.amount > 0:
                    self.d_s = self.poke.heal, max(0, self.poke.heal - self.amount)
                    d = hud.Dialog(text, need_morph_text=True, speed=20, none_skip=True,
                                   style=2, text_var=[self.poke.get_name(True)])
                    sound_manager.start_in_first_empty_taunt(sounds.HIT_NORMAL_DAMAGE.get())
                else:
                    d = hud.Dialog(text, need_morph_text=True, speed=20, none_skip=True,
                                   style=2, text_var=[self.poke.get_name(True)])
                game.game_instance.player.open_dialogue(d)

            return False
        if (not self.animation and utils.current_milli_time() - self.start > 1000) \
                or (self.animation and self.animation.tick(display)):
            game.game_instance.player.close_dialogue()
            if self.amount > 0:
                self.poke.heal = self.d_s[1]
            return True
        if self.amount > 0:
            c = self.d_s[0] - int(
                ((self.d_s[0] - self.d_s[1]) * min(1.0, utils.current_milli_time() - self.start / 1000)))
            self.poke.heal = c
        return False


class PlayAbility(Animation):

    def __init__(self, ab: 'ability.AbstractAbility', bat: 'Battle',
                 launcher: Tuple[int, int, int], launcher_p: 'player_pokemon.PlayerPokemon', l_enemy: bool,
                 enemy: bool, case: int):
        self.bat = bat
        self.launcher_p: 'player_pokemon.PlayerPokemon' = launcher_p
        self.__ab: 'ability.AbstractAbility' = ab
        self.__enemy = enemy
        self.__l_enemy = l_enemy
        self.__case = case
        self.__targets: List[Tuple[int, int, int]] = bat.get_target_pos(ab, l_enemy, enemy, case)
        self.launcher: Tuple[int, int, int] = launcher
        self.__first_time: bool = True
        self.__start_time: int = 0
        # attack / crit
        self.__bool_matrix: List[bool] = [True] * 8
        self.status_date = []
        self.statistic_date = []
        self.cancel: bool = False

    def get_compare_value(self) -> int:
        return self.launcher_p.stats[pokemon.pokemon.SPEED]

    def is_priority(self) -> int:
        return self.__ab.is_priority

    def fix_heal(self):
        for i in range(len(self.__targets_p)):
            self.__targets_p[i].heal = self.__damage_table[i][0]

    def get_rac(self):
        ps_t = utils.current_milli_time() - self.__start_time
        return self.__ab.get_rac(self.__targets, self.launcher, ps_t, self.__first_time)

    def init(self):
        self.__start_time: int = utils.current_milli_time()
        self.__targets_p: List['player_pokemon.PlayerPokemon'] = self.bat.get_target(self.__ab, self.__l_enemy,
                                                                                     self.__enemy, self.__case)
        self.__d_status: Tuple[List[Tuple[int, float]], bool, int] = self.__ab.get_damage(self.launcher_p,
                                                                                          self.__targets_p)
        self.__max_type_multi = max(self.__d_status[0], key=lambda k: k[1])[1]
        self.__max_damge = max(self.__d_status[0], key=lambda k: k[0])[0]
        self.__damage_table = []
        for i in range(len(self.__targets_p)):
            poke = self.__targets_p[i]
            end_heal = poke.heal - self.__d_status[0][i][0]
            self.__damage_table.append((poke.heal, max(0, end_heal)))
        self.__effect_status = self.__ab.get_status_edit(self.launcher_p, self.__targets_p)

        if self.__ab.is_fail(self.launcher_p):
            self.cancel = True
            Battle.TO_SHOW.append(lambda: self.bat.start_new_animation(
                SimpleDialogue("battle.miss_attack", text_var=[self.launcher_p.get_name(True)])))
            self.bat.next_to_show()
            return

        # remove impossible element
        self.__effect_status_fix = [], []
        for e in self.__effect_status[0][1]:
            if self.launcher_p.combat_status.can_add(e, self.bat.turn_count):
                self.__effect_status_fix[0].append(e)
        ii = 0
        for e in self.__effect_status[1]:
            for e2 in e[1]:
                if self.__targets_p[ii].combat_status.can_add(e2, self.bat.turn_count):
                    self.__effect_status_fix[1].append((e2, ii))
            ii += 1

        self.__effect_stats_fix = [], []
        for key, value in self.__effect_status[0][0].items():
            if value != 0:
                self.__effect_stats_fix[0].append((key, value))
        ii = 0
        for e in self.__effect_status[1]:
            for key, value in e[0].items():
                if value != 0:
                    self.__effect_stats_fix[1].append((key, value, ii))
            ii += 1
        to_show = False
        for it in self.launcher_p.combat_status.it:
            back = it.status.attack(it, self.bat.turn_count, self.__ab)
            if back[0]:
                to_show = True
                data = {"anim": StatusRemoveAnimation(it.status, self.launcher_p, not self.__enemy)}
                Battle.TO_SHOW.append([self.bat.start_new_animation, data])
            if back[1]:
                self.cancel = True
                to_show = True
                data = {"anim": StatusDamageAnimation(it, int(back[2]),
                                                      self.launcher[0:2],
                                                      True)}
                Battle.TO_SHOW.append([self.bat.start_new_animation, data])
        if to_show:
            self.bat.next_to_show()

    def tick(self, display: pygame.Surface) -> bool:
        self.bat.rac = None
        if self.__bool_matrix[4]:
            self.__bool_matrix[4] = False
            self.init()
            # return for status edit
            return False
        if self.cancel:
            return True

        ps_t = utils.current_milli_time() - self.__start_time
        if ps_t <= 2000:
            if self.__bool_matrix[0]:
                self.__bool_matrix[0] = False
                d = hud.Dialog("battle.use_ability", need_morph_text=True, speed=20, none_skip=True, style=2,
                               text_var=[self.launcher_p.poke.get_name(True), self.__ab.get_name()])
                game.game_instance.player.open_dialogue(d, over=True)
            return False
        elif ps_t - 2000 <= self.__ab.get_render_during():
            self.bat.rac = self.__ab.get_rac(self.__targets, self.launcher, ps_t - 2000, self.__first_time)
            self.__ab.render(display, self.__targets, self.launcher, ps_t - 2000, self.__first_time)
            if self.__first_time:
                self.__first_time = False
            return False
        else:
            # damage*

            ps_t -= (2000 + self.__ab.get_render_during())
            if ps_t < 1000 and self.__ab.category != ability.STATUS:
                if self.__bool_matrix[5]:
                    self.__bool_matrix[5] = False
                    if self.__max_type_multi != 0 and self.__max_damge != 0:
                        s = sounds.HIT_NOT_VERY_EFFECTIVE if (
                                self.__max_type_multi < 1) else sounds.HIT_NORMAL_DAMAGE if (
                                self.__max_type_multi == 1) else sounds.HIT_SUPER_EFFECTIVE
                        sound_manager.start_in_first_empty_taunt(s.sound)
                for i in range(len(self.__targets_p)):
                    poke = self.__targets_p[i]
                    d_s = self.__damage_table[i]
                    c = d_s[0] - int((d_s[0] - d_s[1]) * (ps_t / 1000))
                    poke.heal = c
                return False
            ps_t -= 1000
            if self.__bool_matrix[3]:
                self.__bool_matrix[3] = False
                for i in range(len(self.__targets_p)):
                    self.__targets_p[i].heal = self.__damage_table[i][1]

            if self.__d_status[1]:
                ps_t -= 1500
                if ps_t < 0:
                    if self.__bool_matrix[1]:
                        self.__bool_matrix[1] = False
                        d = hud.Dialog("battle.critical", need_morph_text=True, speed=20, none_skip=True, style=2)
                        game.game_instance.player.open_dialogue(d, over=True)
                    return False
            if self.__max_type_multi != 1:
                ps_t -= 1500
                if ps_t < 0:
                    if self.__bool_matrix[2]:
                        self.__bool_matrix[2] = False
                        text = "no_effect" if self.__max_type_multi == 0 else "not_effective" if self.__max_type_multi < 1 else "super_effective"
                        d = hud.Dialog("battle." + text, need_morph_text=True, speed=20, none_skip=True, style=2)
                        game.game_instance.player.open_dialogue(d, over=True)
                    return False
            if self.__d_status[2] > 0:
                ps_t -= 1500
                if ps_t < 0:
                    if self.__bool_matrix[6]:
                        self.__bool_matrix[6] = False
                        sound_manager.start_in_first_empty_taunt(sounds.HIT_NORMAL_DAMAGE.get())
                        self.__recoil_d = self.launcher_p.heal, max(0, self.launcher_p.heal - self.__d_status[2])
                        d = hud.Dialog("battle.recoil", need_morph_text=True, speed=20, none_skip=True, style=2,
                                       text_var=[self.launcher_p.get_name(True)])
                        game.game_instance.player.open_dialogue(d, over=True)
                    if ps_t > -1000:
                        for i in range(len(self.__targets_p)):
                            poke = self.launcher_p
                            d_s = self.__recoil_d
                            c = d_s[0] - int(((d_s[0] - d_s[1]) * ((1000 + ps_t) / 1000)))
                            poke.heal = c
                    return False
                elif self.__bool_matrix[7]:
                    self.__bool_matrix[7] = False
                    self.launcher_p.heal = self.__recoil_d[1]

            launcher = self.__effect_status_fix[0]
            enemy = self.__effect_status_fix[1]
            if len(launcher) > 0 or len(enemy) > 0:
                time_l = len(launcher) * 2000
                time_e = len(enemy) * 2000
                if ps_t < time_l:
                    n = min(ps_t // 2000, len(launcher) - 1)
                    if not len(self.status_date) - 1 > n:
                        self.status_date.append(True)
                        add, si = self.launcher_p.combat_status.try_add(launcher[n], self.bat.turn_count)
                        if add:
                            text = si.status.get_apply_text(self.__enemy)
                            if text:
                                d = hud.Dialog(text, need_morph_text=True, speed=20,
                                               none_skip=True, style=2,
                                               text_var=[self.launcher_p.get_name(True)])
                                game.game_instance.player.open_dialogue(d, over=True)
                    return False
                ps_t -= time_l
                if ps_t < time_e:
                    n = min(ps_t // 2000, len(enemy) - 1)
                    if not len(self.status_date) > n + len(launcher):
                        self.status_date.append(True)
                        poke = self.__targets_p[enemy[n][1]]
                        add, si = poke.combat_status.try_add(enemy[n][0], self.bat.turn_count)
                        if add:
                            text = si.status.get_apply_text(not self.__enemy)
                            if text:
                                d = hud.Dialog(text, need_morph_text=True, speed=20,
                                               none_skip=True, style=2,
                                               text_var=[poke.get_name(True)])
                                game.game_instance.player.open_dialogue(d, over=True)
                    return False
                ps_t -= time_e

            launcher = self.__effect_stats_fix[0]
            enemy = self.__effect_stats_fix[1]
            if len(launcher) > 0 or len(enemy) > 0:
                time_l = len(launcher) * 1500
                time_e = len(enemy) * 1500

                if ps_t < time_l:
                    n = min(ps_t // 1500, len(launcher) - 1)
                    if not len(self.statistic_date) > n:
                        self.statistic_date.append(True)
                        a = launcher[n]
                        m = self.launcher_p.pokemon_stats_modifier.add(a[0], a[1])
                        d = hud.Dialog(m,
                                       need_morph_text=True, speed=20, none_skip=True, style=2,
                                       text_var=[self.launcher_p.get_name(True), pokemon.pokemon.TRANSLATE_STATS[a[0]]])
                        game.game_instance.player.open_dialogue(d, over=True)
                    return False
                ps_t -= time_l
                if ps_t < time_e:
                    n = min(ps_t // 1500, len(enemy) - 1)
                    if not len(self.statistic_date) > n + len(launcher):
                        self.statistic_date.append(True)
                        a = enemy[n]
                        poke = self.__targets_p[a[2]]
                        m = poke.pokemon_stats_modifier.add(a[0], a[1])
                        d = hud.Dialog(m,
                                       need_morph_text=True, speed=20, none_skip=True, style=2,
                                       text_var=[poke.get_name(True), pokemon.pokemon.TRANSLATE_STATS[a[0]]])
                        game.game_instance.player.open_dialogue(d, over=True)
                    return False
                ps_t -= time_e

            # check death
            a = [False, len(self.bat.TO_SHOW) == 0]
            for t in range(len(self.__targets_p)):
                if self.__targets_p[t].heal <= 0:
                    a[0] = True
                    c = unparse_enemy_case(self.__targets[t][2])
                    data = {"case": c[1], "enemy": c[0]}
                    self.bat.TO_SHOW.append([self.bat.death_pokemon, data])
            if a[0] and a[1]:
                self.bat.next_to_show()

        game.game_instance.player.close_dialogue()
        return True


# todo move this class

class BattlePlayerDisplay(object):

    def __init__(self, simple: bool, name: str, images: Union[pygame.Surface, List[pygame.Surface]]):
        '''
        images if simple  NPC with pokeball in hand
            else [
                    NPC charging hand
                    NPC start launch
                    NPC continue launch
                    NPC end launch
                ]

        '''
        self.simple = simple
        self.name = name
        self.images = images


class BattlePlayer(object):

    def __init__(self, bot: bool, pks: list['player_pokemon.PlayerPokemon'], case_number: Tuple[int], /,
                 wild: bool = False, disp: Optional['BattlePlayerDisplay'] = None):
        if not wild and disp is None:
            raise ValueError("not wild but no display")
        if len(pks) > 6 or (bot and len(pks) == 0):
            raise ValueError("Invalid pokemon list size")
        for c in case_number:
            if c < 0 or c > 2:
                raise ValueError("case_number value need be in [0:2]")
        self.wild = wild
        self.disp = disp
        self.bot: bool = bot
        self.pks: list['player_pokemon.PlayerPokemon'] = pks
        self.case_number: Tuple[int] = case_number
        for pk in self.get_pks():
            if pk is not None:
                pk.use = False
        self.one_good = False
        self.max_level = max(self.get_pks(), key=lambda p: p.lvl if p else 0).lvl

    def get_pks_index(self, pk):
        i = 0
        for p in self.get_pks():
            if p == pk:
                return i
            i += 1
        return -1

    def get_pks(self):
        return self.pks if self.bot else game.game_instance.player.team

    def get_first_valid_n(self, pass_use: bool = False) -> Optional[int]:
        a_pks = self.get_pks()
        for i in range(len(a_pks)):
            pk = a_pks[i]
            if pk and (not pk.use) and pk.heal > 0:
                self.one_good = True
                if pass_use:
                    pk.set_use(True)
                return i
        if not self.one_good:
            raise ValueError("No alive pokemon in player team can't do battle !")
        return None

    def get_first_valid(self) -> Optional['player_pokemon.PlayerPokemon']:
        return None if (value := self.get_first_valid_n()) is None else self.get_pks()[value]

    # def get_all_first(self) -> List[Optional[int]]:
    #     return [self.get_first_valid_n() for i in range(len(self.case_number))]


class BattleTeam(object):

    def __init__(self, members: list[BattlePlayer], enemy: bool, team_name: str = None):
        self.team_name = team_name
        self.members = members
        self.enemy = enemy
        self.case: List[Optional[BattlePlayer]] = [None] * 3

        for m in members:
            for c in m.case_number:
                if self.case[c] is not None:
                    raise ValueError(f"double same case in team {enemy}")
                self.case[c] = m

        for i in range(len(self.case)):
            while len(self.case) > i and self.case[i] is None:
                del self.case[i]

        if len(self.case) == 0:
            raise ValueError("invalid amount of case")

        if not enemy and self.get_none_bot() is None:
            raise ValueError("Only bot in ally team")

    def get_nb_none_bot(self):
        v = 0
        for m in self.case:
            if not m.bot:
                v += 1
        return v

    def get_none_bot(self):
        for m in self.case:
            if not m.bot:
                return m
        return None

    def is_all_dead(self):
        for m in self.members:
            for p in m.get_pks():
                if p and p.heal > 0:
                    return False
        return True

    # def get_all_first(self) -> List[Optional['player_pokemon.PlayerPokemon']]:
    #     back = []
    #     for mem in self.members:
    #         back += mem.get_all_first()
    #     return back


class PokemonSwitch(Animation):

    def __init__(self, battle: 'Battle', team: BattleTeam, case: int, poke: 'player_pokemon.PlayerPokemon', enemy: bool,
                 team_n: int):
        self.poke = poke
        self.enemy = enemy
        self.team_n = team_n
        self.case = case
        self.battle = battle
        self.team = team
        self.init = False

    def is_priority(self) -> int:
        return 3

    def tick(self, display: pygame.Surface) -> bool:
        if not self.init:
            self.init = True
            data = {"case": self.case, "poke": self.battle.get_team(self.enemy)[self.case], "enemy": self.enemy,
                    "callback": self.battle.next_to_show}
            Battle.TO_SHOW.append([self.battle.callback_pokemon, data])
            data2 = {"case": self.case, "team_n": self.team_n, "enemy": self.enemy,
                     "callback": self.battle.next_to_show}
            Battle.TO_SHOW.append([self.battle.launch_pokemon, data2])
            self.battle.next_to_show()
            return False
        return True


class RunAway(Animation):

    def __init__(self, battle: 'Battle', success: bool):
        self.success = success
        self.battle = battle

    def is_priority(self) -> int:
        return 4

    def tick(self, display: pygame.Surface) -> bool:
        if self.success:
            Battle.TO_SHOW.append(
                lambda: self.battle.start_new_animation(SimpleDialogue("battle.run_away.success", during=2000)))
            self.battle.next_to_show()
            self.battle.need_run_away = True
        else:
            Battle.TO_SHOW.append(
                lambda: self.battle.start_new_animation(SimpleDialogue("battle.run_away.fail", during=2000)))
            self.battle.next_to_show()
        return True


class DeathPokemonAnimation(Animation):

    def __init__(self, bt: 'Battle', poke_pos: Tuple[int, int, int], poke: 'player_pokemon.PlayerPokemon'):
        self.bt = bt
        self.poke_pos = poke_pos
        self.poke = poke
        self.c = unparse_enemy_case(self.poke_pos[2])
        self.init = False
        self.bool_matrix = [True] * 2

    def tick(self, display: pygame.Surface) -> bool:
        if not self.init:
            self.init = True
            self.start_time = utils.current_milli_time()
        ps_t = utils.current_milli_time() - self.start_time

        if self.bool_matrix[0]:
            self.bool_matrix[0] = False
            d = hud.Dialog("battle.no_life", speed=20, none_skip=True, style=2, need_morph_text=True,
                           text_var=[self.poke.get_name(True)])
            game.game_instance.player.open_dialogue(d, over=True)
        elif ps_t >= 1500 and self.bool_matrix[1]:
            self.bool_matrix[1] = False
            d = hud.Dialog("battle.fainted", speed=20, none_skip=True, style=2, need_morph_text=True,
                           text_var=[self.poke.get_name(True)])
            game.game_instance.player.open_dialogue(d, over=True)
        elif ps_t >= 3000:
            game.game_instance.player.close_dialogue()
            return True
        return False


class DeathPokemonChoiceAnimation(Animation):

    def __init__(self, battle: 'Battle', case: int, ask_before: bool = False):
        self.battle = battle
        self.case = case
        self.ask_before = ask_before
        self.on_ask = False

    def tick(self, display: pygame.Surface) -> bool:
        if self.ask_before == 0:
            game.game_instance.player.open_menu(ChangePokemonMenu(game.game_instance.player, self.choice_call_back))
            return True
        elif self.ask_before == -1:
            return True
        elif not self.on_ask:
            self.on_ask = True
            ask = [
                game.game_instance.get_message("yes"),
                game.game_instance.get_message("no")
            ]

            def callback(x, i):
                self.ask_before = -i

            game.game_instance.player.open_dialogue(
                hud.QuestionDialog("battle.ask_switch_pokemon", callback, ask, speed=25, need_morph_text=True, style=2)
            )

        return False

    def choice_call_back(self, done: bool, n: int) -> NoReturn:
        game.game_instance.player.close_menu()
        data = {"case": self.case, "team_n": n, "enemy": False}
        self.battle.TO_SHOW.append([self.battle.launch_pokemon, data])
        if len(self.battle.TO_SHOW) == 1:
            self.battle.next_to_show()
        # self.battle.launch_pokemon(self.case, n, False)


class CallBackPokemonAnimation(Animation):

    def __init__(self, mem: BattlePlayer, case: int, poke: 'player_pokemon.PlayerPokemon', enemy: bool):
        self.mem = mem
        self.start_time = utils.current_milli_time()
        self.case = case
        self.poke = poke
        self.enemy = enemy
        self.bool_matrix = [True] * 1

    def tick(self, display: pygame.Surface) -> bool:
        ps_t = utils.current_milli_time() - self.start_time

        if self.mem.bot:
            if self.bool_matrix[0]:
                self.bool_matrix[0] = False
                d = hud.Dialog("battle.call_back_pokemon.bot", speed=20, none_skip=True, style=2, need_morph_text=True,
                               text_var=[self.mem.disp.name, self.poke.get_name(True)])
                game.game_instance.player.open_dialogue(d, over=True)
            if ps_t >= 1500:
                game.game_instance.player.close_dialogue()
                return True
            return False
        else:
            if self.bool_matrix[0]:
                self.bool_matrix[0] = False
                d = hud.Dialog("battle.call_back_pokemon.self", speed=20, none_skip=True, style=2, need_morph_text=True,
                               text_var=[self.poke.get_name(True)])
                game.game_instance.player.open_dialogue(d, over=True)
            if ps_t >= 1500:
                game.game_instance.player.close_dialogue()
                return True
            return False

    def is_priority(self) -> bool:
        return False


class LaunchPokemonAnimation(Animation):

    def __init__(self, mem: BattlePlayer, case: int, team_n: int, enemy: bool):
        self.mem = mem
        self.start_time = utils.current_milli_time()
        self.case = case
        self.team_n = team_n
        self.enemy = enemy
        self.bool_matrix = [True] * 1

    def tick(self, display: pygame.Surface) -> bool:
        ps_t = utils.current_milli_time() - self.start_time
        if self.mem.wild:
            if self.bool_matrix[0]:
                self.bool_matrix[0] = False
                d = hud.Dialog("battle.wild_spawn", speed=20, none_skip=True, style=2, need_morph_text=True,
                               text_var=[self.mem.get_pks()[self.team_n].get_name(True)])
                game.game_instance.player.open_dialogue(d, over=True)
            if ps_t >= 1500:
                game.game_instance.player.close_dialogue()
                return True
            return False
        elif self.mem.bot:
            if self.bool_matrix[0]:
                self.bool_matrix[0] = False
                d = hud.Dialog("battle.launch_pokemon.bot", speed=20, none_skip=True, style=2, need_morph_text=True,
                               text_var=[self.mem.disp.name, self.mem.get_pks()[self.team_n].get_name(True)])
                game.game_instance.player.open_dialogue(d, over=True)
            if ps_t >= 1500:
                game.game_instance.player.close_dialogue()
                return True
            return False
        else:
            if self.bool_matrix[0]:
                self.bool_matrix[0] = False
                d = hud.Dialog("battle.launch_pokemon.self", speed=20, none_skip=True, style=2, need_morph_text=True,
                               text_var=[self.mem.get_pks()[self.team_n].get_name(True)])
                game.game_instance.player.open_dialogue(d, over=True)
            if ps_t >= 1500:
                game.game_instance.player.close_dialogue()
                return True
            return False

    def is_priority(self) -> bool:
        return 2


class TryCatchAnimation(Animation):

    def __init__(self, bat: 'Battle', poke_ball: 'item.pokeball.Pokeball'):
        self.poke_ball = poke_ball
        self.bat = bat
        self.target_poke = bat.get_team(True)[0]
        self.launcher = bat.get_poke_pose(False, 0, True)
        self.target = bat.get_poke_pose(True, 0, True)
        self.nb_shake = self.poke_ball.try_catch(self.target_poke)
        self.init = 0
        self.start_time = [0] * 4

    def tick(self, display: Surface) -> bool:
        if not (self.init & 0b1):
            self.init |= 0b1
            self.start_time[0] = utils.current_milli_time()
            sound_manager.start_in_first_empty_taunt(sounds.BALL_THROW)
        ps_t = utils.current_milli_time() - self.start_time[0]
        x2, y2 = self.target[0], self.target[1] - 30
        if ps_t <= 1000:
            x1, y1 = self.launcher[0] + 40, self.launcher[1] - 50
            a = (y2 - y1) / (x2 - x1)
            b = y1 - a * x1
            max_delta_x = x2 - x1

            if ps_t % 1200 < 1000:
                x = min(((ps_t % 1200) / 1000), 1) * max_delta_x + x1
                y = (a * x + b) + (0.002 * (x - x1) * (x - x2))
                display.blit(self.poke_ball.image, (x - 11, y - 11))
        else:
            if ps_t < 1600:
                self.draw_absorb(display)
                display.blit(self.poke_ball.image, (x2 - 11, y2 - 11))
            else:
                current_shake = (ps_t - 1600) // 1000
                if current_shake >= self.nb_shake or current_shake >= 3:
                    if self.nb_shake == 4:
                        v = self.draw_catch(display)
                        return v
                    else:
                        return self.draw_break(display)
                else:
                    self.draw_check(display, current_shake, (ps_t - 1600) % 1000)
        return False

    def draw_catch(self, display: Surface) -> bool:
        if not (self.init & 0b1000):
            self.init |= 0b1000
            self.start_time[3] = utils.current_milli_time()
            game.game_instance.player.open_dialogue(hud.Dialog('battle.catch.success', need_morph_text=True,
                                                               speed_skip=False, speed=1, style=2, none_skip=True,
                                                               text_var=[self.target_poke.get_name(True)]))
            sound_manager.start_in_first_empty_taunt(sounds.CATCH)
        ps_t = utils.current_milli_time() - self.start_time[3]
        x2, y2 = self.target[0], self.target[1] - 30
        display.blit(self.poke_ball.image, (x2 - 11, y2 - 11))
        if ps_t > 2000:
            self.bat.is_catch = True
            self.target_poke.poke_ball = self.poke_ball
            game.game_instance.player.close_dialogue()
            return True
        return False

    def draw_break(self, display: Surface) -> bool:
        if not (self.init & 0b100):
            self.init |= 0b100
            self.start_time[2] = utils.current_milli_time()
            game.game_instance.player.open_dialogue(hud.Dialog(f'battle.catch.fail_{self.nb_shake}',
                                                               need_morph_text=True, speed_skip=False,
                                                               speed=1, style=2, none_skip=True))
            sound_manager.start_in_first_empty_taunt(sounds.BALL_EXIT)
        ps_t = utils.current_milli_time() - self.start_time[2]
        if ps_t < 600:
            self.target_poke.ram_data["battle_render"] = False
            resize = ps_t / 600
            im = utils.color_image(self.target_poke.get_front_image(2).copy(), (19, 143, 209, 200))
            im = pygame.transform.scale(im, (int(im.get_size()[0] * resize), int(im.get_size()[1] * resize)))
            p_c = self.bat.get_poke_pose(True, 0, size_edit=(resize, resize))
            display.blit(im, (p_c[0], p_c[1]))
        if ps_t > 600:
            self.target_poke.ram_data["battle_render"] = True
            return True
        return False

    def draw_check(self, display: Surface, check_n: int, ps_t):
        if not (self.init & (2 ** (4 + check_n))):
            self.init |= (2 ** (4 + check_n))
            game.game_instance.player.open_dialogue(hud.Dialog([f'{check_n + 1}...'], speed_skip=False, speed=1,
                                                                   style=2, none_skip=True))
            sound_manager.start_in_first_empty_taunt(sounds.BALL_SHAKE)
        x2, y2 = self.target[0], self.target[1] - 30
        rotate = 0
        if ps_t <= 150 or ps_t > 600:
            rotate = 0
        elif ps_t <= 300 or 450 < ps_t <= 600:
            rotate = 22.5
        elif ps_t <= 450:
            rotate = 45
        im = self.poke_ball.image
        if rotate != 0:
            if check_n % 2:
                rotate = -rotate
            im = pygame.transform.rotate(im, rotate)
        display.blit(im, (x2 - 11, y2 - 11))

    def draw_absorb(self, display: Surface):
        if not (self.init & 0b10):
            self.init |= 0b10
            self.start_time[1] = utils.current_milli_time()
        ps_t = utils.current_milli_time() - self.start_time[1]
        if ps_t < 600:
            self.target_poke.ram_data["battle_render"] = False
            resize = 1 - ps_t / 600
            im = utils.color_image(self.target_poke.get_front_image(2).copy(), (19, 143, 209, 200))
            im = pygame.transform.scale(im, (int(im.get_size()[0] * resize), int(im.get_size()[1] * resize)))
            p_c = self.bat.get_poke_pose(True, 0, size_edit=(resize, resize))
            display.blit(im, (p_c[0], p_c[1]))

    def is_priority(self) -> int:
        return 10


class CatchSuccess(Animation):

    def __init__(self, poke: 'player_pokemon.PlayerPokemon'):
        self.poke = poke
        self.init = False
        self.start = 0
        self.bg = pygame.image.load('assets/textures/battle/bg/evolution.png')
        self.question_answer = None
        self.need_end = False
        self.player = game.game_instance.player
        game.game_instance.set_pokedex_catch(poke.id_)

    def tick(self, display: Surface) -> bool:
        if not self.init:
            self.init = True
            self.ask()
        if self.need_end:
            return True

        display.blit(self.bg, (0, 0))
        display.blit(im := self.poke.get_front_image(4), (530 - im.get_size()[0] // 2, 300 - im.get_size()[1] // 2))

        if self.question_answer is not None:
            # no
            if self.question_answer == 0:
                self.question_answer = None
                self.player.pc.add_first_case_empty(self.poke)
                self.player.open_dialogue(
                    hud.Dialog('battle.catch.success.ask.send_to_pc.message', text_var=[self.poke.get_name(True)],
                               callback=self.end_callback, speed=1, need_morph_text=True, style=2)
                )
                return False
            elif self.question_answer == 1:
                self.question_answer = None
                print(self.player.get_non_null_team_number())
                if self.player.get_non_null_team_number() < 6:
                    self.player.team[5] = self.poke
                    self.player.normalize_team()
                    self.player.open_dialogue(
                        hud.Dialog('battle.catch.success.ask.include_to_team.message', need_morph_text=True,
                                   text_var=[self.poke.get_name(True)], callback=self.end_callback, style=2, speed=1)
                    )
                else:
                    self.player.open_menu(menu__.TeamMenu(self.player, self.ask, self.switch_pokemon))
        return False

    def switch_pokemon(self, i):
        self.player.close_menu()
        self.player.move_pokemon_to_pc(i)
        self.player.team[5] = self.poke
        self.player.normalize_team()
        self.player.open_dialogue(
            hud.Dialog('battle.catch.success.ask.include_to_team.message', text_var=[self.poke.get_name(True)],
                       callback=self.end_callback, need_morph_text=True, speed=1, style=2)
        )

    def ask(self):
        self.player.close_menu()
        self.question_answer = None
        ask = game.game_instance.get_message("battle.catch.success.ask.send_to_pc"), \
              game.game_instance.get_message("battle.catch.success.ask.include_to_team")
        game.game_instance.player.open_dialogue(
            hud.QuestionDialog('battle.catch.success.ask', self.callback, ask, speed=1, style=2, need_morph_text=True,
                              text_var=[self.poke.get_name(True)]))

    def end_callback(self):
        self.player.close_dialogue()
        self.need_end = True

    def callback(self, value, index):
        self.question_answer = index

class Battle(object):
    # END_BASE_POINT: Tuple[int, int] = (SURFACE_SIZE[0] - 390, 0)

    def __init__(self, ally: BattleTeam, enemy: BattleTeam,
                 wild: bool, animation: Callable[[], StartAnimation] = WildAnimation,
                 base: Tuple[int, int, int, int] = GRASS_PLATE_BASE, bg: 'background.BackGround' = background.FOREST,
                 sound: 'sounds.Sound' = sounds.BATTLE_DPP_TRAINER
                 ):

        self.match_size = len(ally.case), len(enemy.case)
        self.__ally_team = ally
        self.__enemy_team = enemy

        self.sound: 'sounds.Sound' = sound
        self.nb_ally = len(self.__ally_team.case)
        self.nb_enemy = len(self.__enemy_team.case)
        self.__ally: List[Optional['player_pokemon.PlayerPokemon']] = [None] * self.nb_ally
        self.__enemy: List[Optional['player_pokemon.PlayerPokemon']] = [None] * self.nb_enemy
        self.__xp_per_case: List[set[int]] = [set()] * self.nb_enemy

        self.nb_not_bot: Tuple[int] = self.__ally_team.get_none_bot().case_number
        self.selected_not_bot: int = min(self.nb_not_bot)
        self.player_queue = []

        self.base_size = BASE_SIZES[max(self.nb_ally, self.nb_enemy) - 1]
        self.wild = wild
        self.__start_time = utils.current_milli_time()
        self.poke_ball = pygame.transform.scale(item.items.POKE_BALL.image,
                                                (game.SURFACE_SIZE[1] // 8, game.SURFACE_SIZE[1] // 8))
        self.start_sound: pygame.mixer.Sound = pygame.mixer.Sound('assets/sound/music/pokemon-start-battle.mp3')
        self.animation: StartAnimation = animation()
        self.bool_matrix = [True] * 5
        self.base: Union[Tuple[int, int, int, int], pygame.Surface] = base
        self.bg: 'background.BackGround' = bg
        self.bg_image: Optional[pygame.Surface] = None
        self.selected_y = [0, 3]
        self.selected_x = [0, 3]
        self.menu_action: List[Callable[[], NoReturn]] = [None, None]
        self.status = 0
        self.turn_count = 0
        self.current_play_ability: Optional[PlayAbility] = None
        self.queue_play_ability: List[PlayAbility] = []
        self.current_animation: Optional[Animation] = None
        self.current_animation_callback: Optional[Callable[[], NoReturn]] = None
        self.current_ab: Optional['player_pokemon.PokemonAbility'] = None
        self.rac: Optional['RenderAbilityCallback'] = None
        self.run_away_c = 0
        self.need_run_away = False
        self.evolution_table = [None] * 6
        self.multi_turn_ab: dict[str, tuple[ability.AbstractAbility, int, bool, int]] = {}
        self.is_catch: Any = False

    def appear_pokemon(self, enemy: bool, case: int):
        if enemy:
            new_set = set()
            for c_n in self.__ally_team.get_none_bot().case_number:
                if (team_n := self.get_poke_n_from_case(False, c_n)) is not None:
                    new_set.add(team_n)
            self.__xp_per_case[case] = new_set
        elif case in self.__ally_team.get_none_bot().case_number:
            team_n = self.get_poke_n_from_case(False, case)
            if team_n is not None:
                for xp_case in self.__xp_per_case:
                    xp_case.add(team_n)

    def get_poke_n_from_case(self, enemy: bool, case: int) -> Optional[int]:
        team = self.__enemy_team if enemy else self.__ally_team
        poke = (self.__enemy if enemy else self.__ally)[case]
        if poke is None: return None
        pks = team.case[case].get_pks()
        for i in range(len(pks)):
            if pks[i] and pks[i] == poke:
                return i
        return None

    def get_team(self, enemy) -> List[Optional['player_pokemon.PlayerPokemon']]:
        return self.__enemy if enemy else self.__ally

    def get_team_obj(self, enemy) -> BattleTeam:
        return self.__enemy_team if enemy else self.__ally_team

    def load_asset(self):
        self.sound.load()
        sounds.HIT_NORMAL_DAMAGE.load()
        sounds.HIT_NOT_VERY_EFFECTIVE.load()
        sounds.HIT_SUPER_EFFECTIVE.load()
        sounds.BLOCK.load()
        self.animation.load_asset()
        self.base = utils.get_part_i(pygame.image.load('assets/textures/battle/base_2.png'), self.base, self.base_size)
        self.bg_image = pygame.transform.scale(pygame.image.load(self.bg.bg_path), game.SURFACE_SIZE)
        self.button_text = [game.game_instance.get_message(t) for t in ['attack', 'team', 'bag', 'run_away']]
        # self.arrow = utils.get_part_i(menu.MENU_IMAGE, (0, 64, 22, 91), (33, 41))
        self.arrow = utils.ARROW
        for m in self.__ally_team.members + self.__enemy_team.members:
            for p in m.get_pks():
                if p:
                    p.reset_combat_status()
                    for a in p.ability:
                        if a:
                            a.ability.load_assets()

    def unload_assets(self):
        # other assets is auto del with dell battle
        print("battle unload_assets")
        self.sound.un_load()
        sounds.HIT_NORMAL_DAMAGE.un_load()
        sounds.HIT_NOT_VERY_EFFECTIVE.un_load()
        sounds.HIT_SUPER_EFFECTIVE.un_load()
        sounds.BALL_SHAKE.un_load()
        sounds.BALL_EXIT.un_load()
        sounds.BALL_THROW.un_load()
        sounds.CATCH.un_load()
        sounds.EVOLUTION.un_load()
        game.POKE_CACHE.clear()
        sounds.unload_poke_sound()
        for m in self.__ally_team.members + self.__enemy_team.members:
            for p in m.get_pks():
                if p:
                    p.reset_combat_status()
                    for a in p.ability:
                        if a:
                            a.ability.unload_assets()

    def __del__(self):
        self.unload_assets()

    def need_render(self):
        return utils.current_milli_time() - self.__start_time <= self.animation.get_during()[0]

    def draw_base(self, display: pygame.Surface, x, enemy: bool, i=0):
        if enemy:
            display.blit(self.base, (x, self.bg.enemy_base_coord[self.nb_enemy - 1][i][1]))
        else:
            display.blit(self.base, (x, self.bg.ally_base_coord[self.nb_ally - 1][i][1]))

    def draw_bg(self, display: pygame.Surface):
        display.blit(self.bg_image, (0, 0))

    INFO_enemy = 830, 580, 330
    INFO_ally = 60, 310, 560

    def get_poke_pose(self, enemy: bool, i: int, simple: bool = False, size_edit=(1, 1)) -> Tuple[int, int, int]:
        c = self.bg.enemy_base_coord[self.nb_enemy - 1][i] if enemy else self.bg.ally_base_coord[self.nb_ally - 1][i]
        poke = self.__enemy[i] if enemy else self.__ally[i]
        size = 192, 192
        if simple:
            return c[0] + (self.base_size[0]) // 2, int(c[1] + (self.base_size[1] * 0.75)), parse_enemy_case(enemy, i)
        return c[0] + (self.base_size[0] // 2) - ((size[0] * size_edit[0]) // 2), int(
            c[1] + (self.base_size[1] * 0.75) - (
                        (poke.front_image_y if enemy else poke.back_image_y) * 2 * size_edit[1])), \
               parse_enemy_case(enemy, i)

    GRADIENT = [(0, 229, 29), (25, 205, 27), (50, 181, 26), (75, 157, 25), (100, 133, 24), (125, 109, 23),
                (150, 85, 22), (175, 61, 21), (200, 37, 20), (225, 14, 19)]

    def bar_color(self, heal, max_heal):
        return Battle.GRADIENT[utils.min_max(0, 9 - int(((heal / max_heal) * 10)), 9)]

    def draw_pokemon(self, display: pygame.Surface, enemy: bool, i, rac: Optional['RenderAbilityCallback']):
        p_c = self.get_poke_pose(enemy, i)[0: 2]
        if enemy:
            poke = self.__enemy[i]
            if "battle_render" not in poke.ram_data or poke.ram_data["battle_render"]:
                x = Battle.INFO_enemy[i]
                if rac:
                    m = rac.get_move(enemy, i)
                    if c := rac.get_color(enemy, i):
                        display.blit(poke.get_front_image_colored(c[1:], 2), (p_c[0] + m[1], p_c[1] + m[2]))
                    else:
                        display.blit(poke.get_front_image(2), (p_c[0] + m[1], p_c[1] + m[2]))
                else:
                    display.blit(poke.get_front_image(2), p_c)
                pygame.draw.polygon(display, (246, 250, 253), ((x, 20), (x + 100, 20), (x + 80, 60), (x - 20, 60)))
                pygame.draw.polygon(display, (255, 255, 255),
                                    ((x + 100, 20), (x + 220, 20), (x + 200, 60), (x + 80, 60)))

                utils.draw_progress_bar(display, (x, 40), (170, 5), (100, 100, 100),
                                        self.bar_color(poke.heal, poke.get_max_heal()),
                                        poke.heal / poke.get_max_heal())
                lvl = game.FONT_20.render("N.{}".format(poke.lvl), True, (0, 0, 0))
                display.blit(lvl, (x + 170 - lvl.get_rect().size[0], 20))
                n = poke.get_name(True)
                display.blit(game.FONT_16.render(n, True, (0, 0, 0)), (x, 23))

                im = poke.combat_status.get_all_image()
                if len(im) > 0:
                    current = im[min(utils.current_milli_time() % (len(im) * 2000) // 2000, len(im) - 1)]
                    utils.draw_rond_rectangle(display, x + 110, 46, 12, 50, current[1])
                    display.blit(tx := game.FONT_12.render(current[0], True, (255, 255, 255)),
                                 (x + 135 - tx.get_size()[0] // 2, 52 - tx.get_size()[1] // 2))

        else:
            poke = self.__ally[i]
            if "battle_render" not in poke.ram_data or poke.ram_data["battle_render"]:
                x = Battle.INFO_ally[i]
                if rac:
                    m = rac.get_move(enemy, i)

                    if c := rac.get_color(enemy, i):
                        im = poke.get_back_image_colored(c[1:], 2)
                    else:
                        im = poke.get_back_image(2)
                    if rac.get_resize(enemy, i):
                        size = rac.get_resize(enemy, i)
                        im = pygame.transform.scale(im, (int(im.get_size()[0] * size[1]),
                                                         int(im.get_size()[1] * size[2])))
                        p_c = self.get_poke_pose(enemy, i, size_edit=size[1:3])[0: 2]

                    display.blit(im, (p_c[0] + m[1], p_c[1] + m[2]))
                else:
                    display.blit(poke.get_back_image(2), p_c)
                pygame.draw.polygon(display, (246, 250, 253),
                                    ((x + 210, 530), (x + 100, 530), (x + 70, 580), (x + 180, 580)))
                pygame.draw.polygon(display, (255, 255, 255),
                                    ((x + 100, 530), (x - 20, 530), (x - 50, 580), (x + 70, 580)))
                utils.draw_progress_bar(display, (x, 551), (170, 5), (100, 100, 100),
                                        self.bar_color(poke.heal, poke.get_max_heal()),
                                        poke.heal / poke.get_max_heal())
                xp = poke.current_xp_status()
                utils.draw_progress_bar(display, (x + 90, 559), (80, 5), (100, 100, 100), (54, 133, 166),
                                        xp[0] / xp[1])
                lvl = game.FONT_20.render("N.{}".format(poke.lvl), True, (0, 0, 0))
                display.blit(lvl, (x + 170 - lvl.get_rect().size[0], 531))
                n = poke.get_name()
                display.blit(game.FONT_16.render(n, True, (0, 0, 0)), (x, 535))
                display.blit(game.FONT_20.render("{}/{}".format(poke.heal, poke.get_max_heal()), True, (0, 0, 0)),
                             (x, 558))

                im = poke.combat_status.get_all_image()
                if len(im) > 0:
                    current = im[min(utils.current_milli_time() % (len(im) * 2000) // 2000, len(im) - 1)]
                    utils.draw_rond_rectangle(display, x + 110, 566, 12, 50, current[1])
                    display.blit(tx := game.FONT_12.render(current[0], True, (255, 255, 255)),
                                 (x + 135 - tx.get_size()[0] // 2, 572 - tx.get_size()[1] // 2))

    def draw_button(self, display: pygame.Surface) -> NoReturn:
        y = 350
        if not self.wild:
            y += 60
        for i in range(4 if self.wild else 3):
            color = ((0, 0, 0), (255, 255, 255)) if i == self.selected_y[0] else ((255, 255, 255), (0, 0, 0))
            utils.draw_rond_rectangle(display, 800, y, 50, 200, color[0])
            display.blit(tx := game.FONT_24.render(self.button_text[i], True, color[1]),
                         (810, y + 25 - tx.get_size()[1] // 2))

            if i == self.selected_y[0]:
                display.blit(self.arrow, (750, y + 2))
            y += 60

    def draw_ability(self, display: pygame.Surface, u: int) -> NoReturn:
        x = 800
        y = 400
        for i in range(4):
            utils.draw_ability_2(display, (x, y), self.__ally[u].get_ability(i), border=self.selected_y[0] == i)
            if self.selected_y[0] == i:
                display.blit(self.arrow, (x - 50, y + 2))
            y += 50

    TARGET_POSE = ((440,), (290, 590), (180, 440, 700))

    def draw_target_select(self, display: pygame.Surface):
        pygame.draw.polygon(display, (206, 39, 86, 100), ((0, 150), (795, 150), (265, 450), (0, 450)))
        pygame.draw.polygon(display, (172, 27, 64, 100), ((795, 150), (1060, 150), (1060, 450), (265, 450)))
        nb_enemy = self.nb_enemy
        nb_ally = self.nb_ally
        tab = self.current_ab.ability.get_target(self.selected_x[0], nb_enemy, nb_ally, self.selected_y[0] == 0)
        WHITE = (255, 255, 255)
        BLACK = (0, 0, 0)
        GRAY = (100, 100, 100)

        for i in range(nb_enemy):
            self.draw_target_pokemon(display, self.__enemy[self.selected_x[1] - 1 - i],
                                     BLACK if tab[0][i] else WHITE,
                                     (Battle.TARGET_POSE[nb_enemy - 1][i], 200),
                                     WHITE if tab[0][i] else GRAY)
        for i in range(nb_ally):
            self.draw_target_pokemon(display, self.__ally[i],
                                     BLACK if tab[1][i] else WHITE,
                                     (Battle.TARGET_POSE[nb_enemy - 1][i], 325),
                                     WHITE if tab[1][i] else GRAY)

    def draw_target_pokemon(self, display: pygame.Surface, poke: 'player_pokemon.PlayerPokemon', color, pose,
                            text_color):
        utils.draw_rond_rectangle(display, pose[0], pose[1], 75, 180, color)
        if poke:
            display.blit(poke.get_front_image(0.8), (pose[0] - 25, pose[1] - 5))
            display.blit(game.FONT_24.render(poke.get_name(True), True, text_color), (pose[0] + 30, pose[1] + 15))

    TO_SHOW = []

    def next_to_show(self) -> NoReturn:
        if len(Battle.TO_SHOW) > 0:
            if self.current_animation is None:
                self.selected_y = [0, 0]
                self.menu_action = [None, None]
                self.status = -1
                a = Battle.TO_SHOW[0]
                del Battle.TO_SHOW[0]
                if isinstance(a, List) or isinstance(a, tuple):
                    a[0](**a[1])
                elif a:
                    a()
                else:
                    self.ability_escape()
        else:
            self.ability_escape()

    def setup_first_pokemon(self, team: BattleTeam, st: List[Optional['player_pokemon.PlayerPokemon']], enemy: bool):
        for i in range(len(st)):
            me = team.case[i]
            team_n = me.get_first_valid_n(True)
            data = {"case": i, "team_n": team_n, "enemy": enemy, "callback": self.next_to_show}
            Battle.TO_SHOW.append([self.launch_pokemon, data])

    def tick(self, display: pygame.Surface) -> Union[bool, Callable[[], NoReturn]]:
        ps_t = utils.current_milli_time() - self.__start_time

        if self.bool_matrix[1] and ps_t >= self.animation.get_during()[0]:
            self.bool_matrix[1] = False
            self.load_asset()
        if ps_t < self.animation.get_during()[1]:
            self.animation.tick(display, self, ps_t)
            return False

        if self.bool_matrix[3]:
            self.bool_matrix[3] = False
            self.setup_first_pokemon(self.__enemy_team, self.__enemy, True)
            self.setup_first_pokemon(self.__ally_team, self.__ally, False)
            self.next_to_show()

        self.draw_bg(display)
        for i in range(self.nb_enemy):
            self.draw_base(display, self.bg.enemy_base_coord[self.nb_enemy - 1][i][0], enemy=True, i=i)
            if self.__enemy[i]:
                self.draw_pokemon(display, True, i, self.rac)
        for i in range(self.nb_ally):
            self.draw_base(display, self.bg.ally_base_coord[self.nb_ally - 1][i][0], enemy=False, i=i)
            if self.__ally[i]:
                self.draw_pokemon(display, False, i, self.rac)

        if self.current_animation:
            if self.current_animation.tick(display):
                self.current_animation = None
                a, self.current_animation_callback = self.current_animation_callback, None
                if a:
                    a()
            return False
        else:
            if self.bool_matrix[4]:
                self.bool_matrix[4] = False
                sound_manager.MUSIC_CHANNEL.play(self.sound.sound, -1)

        if self.need_run_away:
            return lambda: sound_manager.MUSIC_CHANNEL.stop()

        if self.current_play_ability:
            if self.current_play_ability.tick(display):
                self.current_play_ability = None
                if self.is_catch:
                    self.queue_play_ability.clear()
                    self.turn_count += 1
                    return False
                while len(self.queue_play_ability) > 0 and self.queue_play_ability[0].launcher_p.heal == 0:
                    del self.queue_play_ability[0]
                if len(self.queue_play_ability) > 0:
                    self.current_play_ability = self.queue_play_ability[0]
                    del self.queue_play_ability[0]
                    return False
                else:
                    self.current_play_ability = None
                    self.turn_count += 1
                    self.check_death()
                    for ally in [True, False]:
                        pks = self.__ally if ally else self.__enemy
                        for ap_i in range(len(pks)):
                            ap = pks[ap_i]
                            if ap:
                                for it in ap.combat_status.it:
                                    back = it.status.turn(it, self.turn_count)
                                    if back[0]:
                                        data = {"anim": StatusRemoveAnimation(it.status, ap, True)}
                                        Battle.TO_SHOW.append([self.start_new_animation, data])
                                    else:
                                        data = {"anim": StatusDamageAnimation(it, int(back[1]),
                                                                              self.get_poke_pose(not ally, ap_i, True)[
                                                                              0:2],
                                                                              True)}
                                        Battle.TO_SHOW.append([self.start_new_animation, data])
                    self.next_to_show()
            return False

        if self.is_catch:
            if isinstance(self.is_catch, bool):
                self.catch()
                return False
            else:
                return self.is_catch

        if len(self.queue_play_ability) == 0 and self.current_play_ability is None:
            end_d = self.check_end()
            if end_d[0]:
                if self.bool_matrix[2]:
                    self.bool_matrix[2] = False
                    self.finish_callback = self.end(end_d[1])
                    return False
                else:
                    return self.finish_callback

        if self.current_play_ability is None and game.game_instance.player.current_dialogue is None:
            if self.status == 0:
                self.draw_button(display)
            elif self.status == 1:
                self.draw_ability(display, self.selected_not_bot)
            elif self.status == 2:
                self.draw_target_select(display)

        return False

    BASE_PAYOUT = [8, 16, 24, 36, 48, 64, 80, 100, 120]

    def end(self, victory: bool) -> Optional[Callable[[], NoReturn]]:
        if victory:
            for i in range(6):
                if (new_id := self.evolution_table[i]) is not None:
                    poke = game.game_instance.player.team[i]
                    if poke and poke.heal > 0:
                        Battle.TO_SHOW.append(
                            self.start_new_animation(evolution_animaiton.EvolutionAnimation(self, poke, new_id)))
            if self.wild:
                def over_load():
                    sound_manager.MUSIC_CHANNEL.stop()

                self.next_to_show()
                return over_load
            else:
                self.next_to_show()
                return
        else:
            Battle.TO_SHOW.append(lambda: self.start_new_animation(SimpleDialogue("battle.end.no_pokemon")))
            lost_money = min(
                game.game_instance.get_money(),
                max(
                    game.game_instance.player.team,
                    key=lambda p: p.lvl if p else 0).lvl *
                Battle.BASE_PAYOUT[min(len(Battle.BASE_PAYOUT) - 1, game.game_instance.player.get_badge_amount())])
            game.game_instance.set_money(lost_money)
            if self.wild:
                Battle.TO_SHOW.append(lambda: self.start_new_animation(
                    SimpleDialogue("battle.end.lose_money.wild", text_var=[lost_money])))
            else:
                Battle.TO_SHOW.append(lambda: self.start_new_animation(
                    SimpleDialogue("battle.end.lose_trainer", text_var=[self.__enemy_team.team_name])))
                Battle.TO_SHOW.append(lambda: self.start_new_animation(
                    SimpleDialogue("battle.end.lose_money.trainer", text_var=[lost_money])))
            Battle.TO_SHOW.append(lambda: self.start_new_animation(SimpleDialogue("battle.blacked_out")))
            self.next_to_show()

            level = game.get_game_instance().get_save_value("last_poke_center_level", "poke_center_level_1")
            is_poke_center = True
            level_coord = game.get_game_instance().get_save_value("last_poke_center_level_coord", [80.3, 6.1])

            def over_load():
                sound_manager.MUSIC_CHANNEL.stop()
                game.game_instance.load_level(level, level_coord[0], level_coord[1])
                if is_poke_center:
                    for npc in game.game_instance.level.npc:
                        if isinstance(npc, NPC_.JoyNPC):
                            npc.talk_callback("yes", 0)

            return over_load

    def end_by_catch(self):
        def over_load():
            sound_manager.MUSIC_CHANNEL.stop()
        self.is_catch = over_load

    def catch(self):
        all_xps = [0] * 6
        enemy = self.__enemy[0], 0
        for i in range(6):
            p = game.game_instance.player.team[i]
            if p and p.heal > 0:
                all_xps[i] += self.get_xp_amount(i, *enemy)
        if max(all_xps) > 0:
            self.TO_SHOW.append(lambda: self.start_new_animation(xp_battle_animation.XpAnimation(self, all_xps)))

        self.TO_SHOW.append(lambda: self.start_new_animation(CatchSuccess(self.__enemy[0])))
        self.TO_SHOW.append(self.end_by_catch)
        self.next_to_show()

    def check_death(self) -> NoReturn:
        start = len(self.TO_SHOW)
        ask_switch = 0
        enemy_dead: list[tuple['player_pokemon.PlayerPokemon', int]] = []
        for e in [True, False]:
            for i in range(0, self.nb_enemy if e else self.nb_ally):
                p = (self.__enemy if e else self.__ally)[i]
                if p:
                    if p.heal <= 0:
                        t = self.__enemy_team if e else self.__ally_team
                        m = t.case[i]
                        if e:
                            enemy_dead.append((p, i))
                        first = m.get_first_valid_n()
                        (self.__enemy if e else self.__ally)[i] = None
                        if first is not None:
                            if m.bot:
                                if ask_switch == 0:
                                    ask_switch = 1
                                n = first
                                m.get_pks()[n].use = True
                                data = {"case": i, "team_n": n, "enemy": e}
                                self.TO_SHOW.append([self.launch_pokemon, data])
                            else:
                                ask_switch = -1
                                self.TO_SHOW.append(
                                    [self.start_new_animation, {"anim": DeathPokemonChoiceAnimation(self, i)}])
        if ask_switch == 1 and self.nb_ally == 1:
            self.TO_SHOW.insert(start, [self.start_new_animation, {"anim": DeathPokemonChoiceAnimation(self, 0, True)}])
        if len(enemy_dead) > 0:
            all_xps = [0] * 6
            for enemy in enemy_dead:
                for i in range(6):
                    p = game.game_instance.player.team[i]
                    if p and p.heal > 0:
                        all_xps[i] += self.get_xp_amount(i, *enemy)
            if max(all_xps) > 0:
                self.TO_SHOW.insert(start,
                                    lambda: self.start_new_animation(xp_battle_animation.XpAnimation(self, all_xps)))

        # if to_show and len(self.TO_SHOW) != 0:
        #     self.next_to_show()

    def get_xp_amount(self, team_n: int, enemy_poke: 'player_pokemon.PlayerPokemon', enemy_case) -> int:
        if team_n in self.__xp_per_case[enemy_case]:
            ally_pokemon = game.game_instance.player.team[team_n]
            if ally_pokemon and enemy_poke:
                a = 1 if self.wild else 1.5
                b = enemy_poke.poke.xp_points
                L = enemy_poke.lvl
                Lp = ally_pokemon.lvl
                s = sum(game.game_instance.player.team[t_n].heal > 0 for t_n in self.__xp_per_case[enemy_case])
                return int(((a * b * L) / (5 * s)) * (((2 * L + 10) ** 2.5) / ((L + Lp + 10) ** 2.5) + 1))
        return 0

    def check_end(self) -> Tuple[bool, bool]:
        en_end = self.__enemy_team.is_all_dead()
        al_end = self.__ally_team.is_all_dead()
        return en_end or al_end, en_end

    def target_menu_escape(self):
        self.selected_y = [0, 3]
        self.selected_x = [0, -1]
        self.menu_action = [self.ability_action, self.ability_escape]
        self.status = 1

    def action_menu_action(self) -> NoReturn:
        if self.selected_y[0] == 0:
            self.selected_y = [0, 3]
            self.selected_x = [0, -1]

            poke = self.__ally[self.selected_not_bot]
            if poke.uuid in self.multi_turn_ab:
                tuple_ = self.multi_turn_ab[poke.uuid]
                ab_ = tuple_[0]
                enemy_ = tuple_[2]
                case_ = tuple_[3]
                if tuple_[1] <= 1:
                    del self.multi_turn_ab[poke.uuid]
                else:
                    self.multi_turn_ab[poke.uuid] = (ab_, tuple_[1] - 1, enemy_, case_)
                p = PlayAbility(ab_, self, self.get_poke_pose(False, self.selected_not_bot, simple=True),
                                self.__ally[self.selected_not_bot], False, enemy_, case_)
                self.do_ability_turn(p)
            else:
                self.menu_action = [self.ability_action, self.ability_escape]
                self.status = 1
        elif self.selected_y[0] == 1:
            game.game_instance.player.open_menu(ChangePokemonMenu(game.game_instance.player, self.poke_choice_callback))
        elif self.selected_y[0] == 2:
            if self.wild:
                white_list = (item.item.HEAL, item.item.BERRIES, item.item.POKE_BALLS, item.item.BATTLE_ITEMS)
            else:
                white_list = (item.item.HEAL, item.item.BERRIES, item.item.BATTLE_ITEMS)
            game.game_instance.player.open_menu(bag.Bag(game.game_instance.player,
                                                        white_list_category=white_list,
                                                        condition=bag.CONDITION_BATTLE,
                                                        use_callback=self.bag_callback, close_menu_on_escape=True))
        elif self.selected_y[0] == 3:
            p = self.__enemy[0]
            p2 = self.__ally[self.selected_not_bot]
            B = (p.get_stats(pokemon.pokemon.SPEED, True) / 4) % 255
            if B == 0:
                self.run_away(True)
            else:
                A = p2.get_stats(pokemon.pokemon.SPEED, True)
                F = (A * 32) / B + 30 * self.run_away_c
                if F >= 255 or random.randint(0, 255) <= F:
                    self.run_away(True)
                else:
                    self.run_away_c += 1
                    self.run_away(False)

    def run_away(self, success: bool):
        an = RunAway(self, success)
        self.do_ability_turn(an)

    def bag_callback(self, item_: 'item.item.Item', poke: 'player_pokemon.PlayerPokemon') -> NoReturn:
        game.game_instance.player.close_menu()
        if isinstance(item_, item.pokeball.Pokeball):
            if not self.wild:
                return
            an = TryCatchAnimation(self, item_)
            self.do_ability_turn(an)

        elif item_.category == item.item.HEAL or item.item.BERRIES:
            pass
        elif item_.category == item.item.BATTLE_ITEMS:
            pass

    def poke_choice_callback(self, action: bool, value: int) -> NoReturn:
        game.game_instance.player.close_menu()
        if action:
            an = PokemonSwitch(self, self.__ally_team, self.selected_not_bot, self.__ally[self.selected_not_bot], False,
                               value)
            self.do_ability_turn(an)

    def ability_action(self) -> NoReturn:
        ab = self.__ally[self.selected_not_bot].get_ability(self.selected_y[0])
        if ab and ab.pp > 0:
            self.run_away_c = 0
            if ab.ability.target != ability.TARGET_BOTH and len(
                    self.__ally if ab.ability.target == ability.TARGET_ALLY else self.__enemy) == 1 or ab.ability.target == ability.TARGET_SELF:
                self.do_attack(ab, ab.ability.target == ability.TARGET_ENEMY, self.selected_not_bot)
            else:
                self.selected_y = [0, -1] if ab.ability.target == ability.TARGET_ALLY else \
                    [1, -1] if ab.ability.target == ability.TARGET_SELF else [0, 2]
                self.selected_x = [0, max(self.nb_ally, self.nb_enemy)]
                self.current_ab = ab
                self.menu_action = [
                    lambda: self.do_attack(self.current_ab, self.selected_y[0] == 0,
                                           self.selected_x[1] - 1 - self.selected_x[0]),
                    self.target_menu_escape
                ]
                self.status = 2
        else:
            sound_manager.start_in_first_empty_taunt(sounds.BLOCK.get())

    def do_attack(self, ab: 'player_pokemon.PokemonAbility', enemy: bool, case: int):

        # don't show menu next turn
        self.ability_escape()
        ab.pp -= 1
        poke = self.__ally[self.selected_not_bot]
        if (nb_turn := ab.ability.get_nb_turn()) > 1:
            self.multi_turn_ab[poke.uuid] = (ab.ability, nb_turn - 1, enemy, case)
        p = PlayAbility(ab.ability, self, self.get_poke_pose(False, self.selected_not_bot, simple=True),
                        self.__ally[self.selected_not_bot], False, enemy, case)
        self.do_ability_turn(p)

    def do_ability_turn(self, an: 'Animation'):
        self.player_queue.append(an)

        if len(self.player_queue) == len(self.nb_not_bot):
            self.selected_not_bot = 0
            all_pa: List[PlayAbility] = self.player_queue
            for i in range(self.nb_enemy):
                poke = self.__enemy[i]
                if poke.uuid in self.multi_turn_ab:
                    tuple_ = self.multi_turn_ab[poke.uuid]
                    ab_ = tuple_[0]
                    enemy_ = tuple_[2]
                    case_ = tuple_[3]
                    if tuple_[1] <= 1:
                        del self.multi_turn_ab[poke.uuid]
                    else:
                        self.multi_turn_ab[poke.uuid] = (ab_, tuple_[1] - 1, enemy_, case_)
                else:
                    ab_ = poke.ge_rdm_ability()
                    enemy_ = random.randint(0,
                                            1) == 1 if ab_.target == ability.TARGET_BOTH else ab_.target == ability.TARGET_ENEMY
                    case_ = random.randint(0, self.nb_ally - 1) if enemy_ else random.randint(0, self.nb_enemy - 1)
                    if (nb_turn := ab_.get_nb_turn()) > 1:
                        self.multi_turn_ab[poke.uuid] = (ab_, nb_turn - 1, enemy_, case_)
                if ab_:
                    all_pa.append(
                        PlayAbility(ab_, self, self.get_poke_pose(True, i, simple=True), poke, True, enemy_, case_))
            for i in range(self.nb_ally):
                if self.__ally_team.case[i].bot:

                    if poke.uuid in self.multi_turn_ab:
                        tuple_ = self.multi_turn_ab[poke.uuid]
                        ab_ = tuple_[0]
                        enemy_ = tuple_[2]
                        case_ = tuple_[3]
                        if tuple_[1] <= 1:
                            del self.multi_turn_ab[poke.uuid]
                        else:
                            self.multi_turn_ab[poke.uuid] = (ab_, tuple_[1] - 1, enemy_, case_)
                    else:
                        poke = self.__ally[i]
                        ab_ = poke.ge_rdm_ability()
                        enemy_ = random.randint(0,
                                                1) == 1 if ab_.target == ability.TARGET_BOTH else ab_.target == ability.TARGET_ENEMY
                        case_ = random.randint(0, self.nb_enemy - 1) if enemy_ else random.randint(0, self.nb_ally - 1)
                        if (nb_turn := ab_.get_nb_turn()) > 1:
                            self.multi_turn_ab[poke.uuid] = (ab_, nb_turn - 1, enemy_, case_)
                    if ab_:
                        all_pa.append(
                            PlayAbility(ab_, self, self.get_poke_pose(False, i, simple=True), poke, False, enemy_,
                                        case_))
            sort_ab(all_pa)
            for pa in all_pa:
                if isinstance(all_pa, PlayAbility):
                    pa.fix_heal()

            if len(all_pa) > 0:
                self.current_play_ability = all_pa[0]
                if len(all_pa) > 1:
                    self.queue_play_ability = all_pa[1:]
            self.player_queue.clear()
        else:
            self.selected_not_bot += 1

    def start_new_animation(self, anim: Animation, callback: Callable[[], NoReturn] = None) -> NoReturn:
        self.current_animation = anim
        self.current_animation_callback = callback if callback else self.next_to_show

    def death_pokemon(self, case: int, enemy: bool, callback: Callable[[], NoReturn] = None) -> NoReturn:
        pk = (self.__enemy if enemy else self.__ally)[case]
        # storage = self.__enemy if enemy else self.__ally
        pose = self.get_poke_pose(enemy, case, False)
        pk.ram_data["battle_render"] = False
        # storage[case] = None
        self.current_animation = DeathPokemonAnimation(self, pose, pk)
        self.current_animation_callback = callback if callback else self.next_to_show

    def launch_pokemon(self, case: int, team_n: int, enemy: bool,
                       callback: Callable[[], NoReturn] = None) -> NoReturn:
        member = (self.__enemy_team if enemy else self.__ally_team).case[case]
        storage = self.__enemy if enemy else self.__ally
        poke = member.get_pks()[team_n]
        poke.set_use(True)
        storage[case] = poke
        self.appear_pokemon(enemy, case)
        self.current_animation = LaunchPokemonAnimation(member, case, team_n, enemy)
        self.current_animation_callback = callback if callback else self.next_to_show

    def callback_pokemon(self, case: int, poke: 'player_pokemon.PlayerPokemon', enemy: bool,
                         callback: Callable[[], NoReturn]) -> NoReturn:
        member = (self.__enemy_team if enemy else self.__ally_team).case[case]
        storage = self.__enemy if enemy else self.__ally
        poke.set_use(False)
        storage[case] = None
        self.current_animation = CallBackPokemonAnimation(member, case, poke, enemy)
        self.current_animation_callback = callback

    def ability_escape(self) -> NoReturn:
        self.selected_y = [0, 3 if self.wild else 2]
        self.selected_x = [0, -1]
        self.menu_action = [self.action_menu_action, None]
        self.status = 0

    def on_key_escape(self) -> NoReturn:
        if self.menu_action[1]:
            self.menu_action[1]()

    def on_key_action(self) -> NoReturn:
        if (not self.current_animation or not self.current_animation.on_key_action()) \
                and self.menu_action[0] and not self.current_play_ability:
            self.menu_action[0]()

    def on_key_x(self, left: bool) -> NoReturn:
        if self.selected_x[1] == -1:
            return
        if left:
            if self.selected_x[0] > 0:
                self.selected_x[0] -= 1
        else:
            if self.selected_x[0] < self.selected_x[1]:
                self.selected_x[0] += 1

    def on_key_y(self, up: bool) -> NoReturn:
        if self.selected_y[1] == -1:
            return
        if up:
            if self.selected_y[0] > 0:
                self.selected_y[0] -= 1
        else:
            if self.selected_y[0] < self.selected_y[1]:
                self.selected_y[0] += 1

    def get_target_pos(self, ab: 'ability.AbstractAbility', l_enemy: bool, enemy: bool, case: int) -> List[
        Tuple[int, int, int]]:
        tar = ab.get_target(case, self.nb_enemy, self.nb_ally, enemy)
        back = []
        for i in range(self.nb_ally if l_enemy else self.nb_enemy):
            if tar[0][i]:
                back.append(self.get_poke_pose(not l_enemy, i, simple=True))
        for i in range(self.nb_enemy if l_enemy else self.nb_ally):
            if tar[1][i]:
                back.append(self.get_poke_pose(l_enemy, i, simple=True))
        return back

    def get_target(self, ab: 'ability.AbstractAbility', l_enemy: bool, enemy: bool, case: int) -> List[
        'player_pokemon']:
        tar = ab.get_target(case, self.nb_enemy, self.nb_ally, enemy)
        back = []
        for i in range(self.nb_ally if l_enemy else self.nb_enemy):
            if tar[0][i]:
                back.append((self.__ally if l_enemy else self.__enemy)[i])
        for i in range(self.nb_enemy if l_enemy else self.nb_ally):
            if tar[1][i]:
                back.append((self.__enemy if l_enemy else self.__ally)[i])
        return back


def parse_enemy_case(enemy: bool, case: int) -> int:
    return (enemy << 2) + case


def unparse_enemy_case(value: int) -> tuple[bool, int]:
    return value >> 2 == 1, value & 0b11


# def sub_sor(ab_list: List['Animation'], i):


def sort_ab(ab_list: List['Animation']):
    for i in range(1, len(ab_list)):
        for y in range(i, 1, -1):
            if ab_list[y] > ab_list[y - 1]:
                ab_list[y], ab_list[y - 1] = ab_list[y - 1], ab_list[y]
            else:
                break
