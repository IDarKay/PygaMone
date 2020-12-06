from typing import List, Tuple, NoReturn, Callable, Optional, Union
import pokemon.player_pokemon as player_pokemon
import pokemon.pokemon
import utils
import pygame
import game
import item.items as items
import sound_manager
import pokemon.battle.background as background
import hud.menu as menu
import pokemon.ability as ability
import hud.hud as hud
import sounds
import sound_manager
import random
import copy

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

    def __init__(self, move_target: Optional[List[Tuple[int, int]]] = None,
                 move_launcher: Tuple[int, int] = None,
                 color_editor_target: List[Union[Tuple[int, int, int], Tuple[int, int, int, int]]] = None,
                 color_editor_launcher: Union[Tuple[int, int, int], Tuple[int, int, int, int]] = None
                 ):
        self.move_target = move_target
        self.move_launcher = move_launcher
        self.color_editor_target = color_editor_target
        self.color_editor_launcher = color_editor_launcher


class PlayAbility(object):

    def __init__(self, ab: 'ability.AbstractAbility', bat: 'Battle',
                 launcher: Tuple[int, int], launcher_p: 'player_pokemon.PlayerPokemon', l_enemy: bool,
                 enemy: bool, case: int):

        self.launcher_p: 'player_pokemon.PlayerPokemon' = launcher_p
        self.__ab: 'ability.AbstractAbility' = ab
        self.__targets_p: List['player_pokemon'] = bat.get_target(ab, l_enemy, enemy, case)
        self.__targets: List[Tuple[int, int]] = bat.get_target_pos(ab, l_enemy, enemy, case)
        self.launcher: Tuple[int, int] = launcher
        self.__first_time: bool = True
        self.__start_time: int = 0
        # attack / crit
        self.__bool_matrix: List[bool] = [True] * 6
        # todo call back
        self.__d_status: Tuple[List[Tuple[int, float]], bool, int] = ab.get_damage(self.launcher_p, self.__targets_p)
        print("d_status", self.__d_status)
        self.__max_type_multi = max(self.__d_status[0], key=lambda k: k[1])[1]
        self.__damage_table = []
        for i in range(len(self.__targets_p)):
            poke = self.__targets_p[i]
            end_heal = poke.heal - self.__d_status[0][i][0]
            self.__damage_table.append((poke.heal, max(0, end_heal)))
            poke.heal = end_heal
        print("Dame table", self.__damage_table)

    def fix_heal(self):
        for i in range(len(self.__targets_p)):
            self.__targets_p[i].heal = self.__damage_table[i][0]

    def get_rac(self):
        ps_t = utils.current_milli_time() - self.__start_time
        return self.__ab.get_rac(self.__targets, self.launcher, ps_t, self.__first_time)

    def tick(self, display: pygame.Surface) -> bool:
        if self.__bool_matrix[4]:
            self.__bool_matrix[4] = False
            self.__start_time: int = utils.current_milli_time()

        ps_t = utils.current_milli_time() - self.__start_time
        if ps_t <= 2000:
            if self.__bool_matrix[0]:
                self.__bool_matrix[0] = False
                d = hud.Dialog("battle.use_ability", need_morph_text=True, speed=20, none_skip=True, style=2,
                               text_var=[self.launcher_p.poke.get_name(True), self.__ab.get_name()])
                game.game_instance.player.open_dialogue(d, over=True)
            return False
        elif ps_t - 2000 <= self.__ab.render_during:
            self.__ab.render(display, self.__targets, self.launcher, ps_t - 2000, self.__first_time)
            if self.__first_time:
                self.__first_time = False
            return False
        else:
            # damage*

            ps_t -= (2000 + self.__ab.render_during)
            if ps_t < 1000:
                if self.__bool_matrix[5]:
                    self.__bool_matrix[5] = False
                    if self.__max_type_multi != 0:
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

    def __init__(self, members: list[BattlePlayer], enemy: bool):
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
                if p.heal > 0:
                    return False
        return True

    # def get_all_first(self) -> List[Optional['player_pokemon.PlayerPokemon']]:
    #     back = []
    #     for mem in self.members:
    #         back += mem.get_all_first()
    #     return back


class Animation(object):

    def tick(self, display: pygame.Surface) -> bool:
        pass


class CallBackPokemonAnimation(Animation):

    def __init__(self, mem: BattlePlayer, case: int, team_n: int, enemy: bool):
        self.mem = mem
        self.start_time = utils.current_milli_time()
        self.case = case
        self.team_n = team_n
        self.enemy = enemy
        self.bool_matrix = [True] * 1

    def tick(self, display: pygame.Surface) -> bool:
        ps_t = utils.current_milli_time() - self.start_time

        if self.mem.bot:
            if self.bool_matrix[0]:
                self.bool_matrix[0] = False
                d = hud.Dialog("battle.call_back_pokemon.bot", speed=20, none_skip=True, style=2, need_morph_text=True,
                               text_var=[self.mem.disp.name, self.mem.get_pks()[self.team_n].get_name(True)])
                game.game_instance.player.open_dialogue(d, over=True)
            if ps_t >= 1500:
                game.game_instance.player.close_dialogue()
                return True
            return False
        else:
            if self.bool_matrix[0]:
                self.bool_matrix[0] = False
                d = hud.Dialog("battle.call_back_pokemon.self", speed=20, none_skip=True, style=2, need_morph_text=True,
                               text_var=[self.mem.get_pks()[self.team_n].get_name(True)])
                game.game_instance.player.open_dialogue(d, over=True)
            if ps_t >= 1500:
                game.game_instance.player.close_dialogue()
                return True
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

        self.nb_not_bot: Tuple[int] = self.__ally_team.get_none_bot().case_number
        self.selected_not_bot: int = min(self.nb_not_bot)
        self.player_queue = []

        self.base_size = BASE_SIZES[max(self.nb_ally, self.nb_enemy) - 1]
        self.wild = wild
        self.__start_time = utils.current_milli_time()
        self.poke_ball = pygame.transform.scale(items.POKE_BALL.image,
                                                (game.SURFACE_SIZE[1] // 8, game.SURFACE_SIZE[1] // 8))
        self.start_sound: pygame.mixer.Sound = pygame.mixer.Sound('assets/sound/music/pokemon-start-battle.mp3')
        self.animation: StartAnimation = animation()
        self.bool_matrix = [True] * 5
        self.base: Union[Tuple[int, int, int, int], pygame.Surface] = base
        self.bg: 'background.BackGround' = bg
        self.bg_image: Optional[pygame.Surface] = None
        self.selected_y = [0, 3]
        self.selected_x = [0, 3]
        self.menu_action: List[Callable[[], NoReturn]] = [self.action_menu_action, None]
        self.status = 0
        self.turn_count = 0
        self.current_play_ability: Optional[PlayAbility] = None
        self.queue_play_ability: List[PlayAbility] = []
        self.current_animation: Optional[Animation] = None
        self.current_animation_callback: Optional[Callable[[], NoReturn]] = None
        self.current_ab: Optional['player_pokemon.PokemonAbility'] = None

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
        self.arrow = utils.get_part_i(menu.MENU_IMAGE, (0, 64, 22, 91), (33, 41))
        for m in self.__ally_team.members + self.__enemy_team.members:
            for p in m.get_pks():
                if p:
                    p.reset_combat_stats()
                    for a in p.ability:
                        if a:
                            a.ability.load_assets()

    # todo call this
    def unload_assets(self):
        # other assets is auto del with dell battle
        self.sound.un_load()
        sounds.HIT_NORMAL_DAMAGE.un_load()
        sounds.HIT_NOT_VERY_EFFECTIVE.un_load()
        sounds.HIT_SUPER_EFFECTIVE.un_load()
        game.POKE_CACHE.clear()
        for m in self.__ally_team.members + self.__enemy_team.members:
            for p in m.get_pks():
                if p:
                    p.reset_combat_stats()
                    for a in p.ability:
                        if a:
                            a.ability.unload_assets()

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

    def get_poke_pose(self, enemy: bool, i: int, simple: bool = False) -> Tuple[int, int]:
        c = self.bg.enemy_base_coord[self.nb_enemy - 1][i] if enemy else self.bg.ally_base_coord[self.nb_ally - 1][i]
        poke = self.__enemy[i] if enemy else self.__ally[i]
        size = 192, 192
        if simple:
            return c[0] + (self.base_size[0]) // 2, int(c[1] + (self.base_size[1] * 0.75))
        return c[0] + (self.base_size[0] // 2) - (size[0] // 2), int(
            c[1] + (self.base_size[1] * 0.75) - ((poke.front_image_y if enemy else poke.back_image_y) * 2))

    GRADIENT = [(0, 229, 29), (25, 205, 27), (50, 181, 26), (75, 157, 25), (100, 133, 24), (125, 109, 23),
                (150, 85, 22), (175, 61, 21), (200, 37, 20), (225, 14, 19)]

    def bar_color(self, heal, max_heal):
        return Battle.GRADIENT[utils.min_max(0, 9 - int(((heal / max_heal) * 10)), 9)]

    def draw_pokemon(self, display: pygame.Surface, enemy: bool, i):
        p_c = self.get_poke_pose(enemy, i)
        if enemy:
            poke = self.__enemy[i]
            x = Battle.INFO_enemy[i]
            display.blit(poke.get_front_image(2), p_c)
            pygame.draw.polygon(display, (246, 250, 253), ((x, 20), (x + 100, 20), (x + 80, 50), (x - 20, 50)))
            pygame.draw.polygon(display, (255, 255, 255), ((x + 100, 20), (x + 220, 20), (x + 200, 50), (x + 80, 50)))

            utils.draw_progress_bar(display, (x, 40), (170, 5), (100, 100, 100),
                                    self.bar_color(poke.heal, poke.get_max_heal()),
                                    poke.heal / poke.get_max_heal())
            lvl = game.FONT_20.render("N.{}".format(poke.lvl), True, (0, 0, 0))
            display.blit(lvl, (x + 170 - lvl.get_rect().size[0], 21))
            n = poke.get_name()
            display.blit(game.FONT_16.render(n[0].upper() + n[1:len(n)], True, (0, 0, 0)), (x, 25))
        else:
            poke = self.__ally[i]
            x = Battle.INFO_ally[i]
            display.blit(poke.get_back_image(2), p_c)
            pygame.draw.polygon(display, (246, 250, 253), ((x + 210, 530), (x + 100, 530), (x + 70, 580), (x + 180, 580)))
            pygame.draw.polygon(display, (255, 255, 255), ((x + 100, 530), (x - 20, 530), (x - 50, 580), (x + 70, 580)))
            utils.draw_progress_bar(display, (x, 551), (170, 5), (100, 100, 100),
                                    self.bar_color(poke.heal, poke.get_max_heal()),
                                    poke.heal / poke.get_max_heal())
            xp = poke.current_xp_status()
            utils.draw_progress_bar(display, (x + 90, 559), (80, 5), (100, 100, 100), (54, 133, 166),
                                    xp[0] / xp[1])
            lvl = game.FONT_20.render("N.{}".format(poke.lvl), True, (0, 0, 0))
            display.blit(lvl, (x + 170 - lvl.get_rect().size[0], 531))
            n = poke.get_name()
            display.blit(game.FONT_16.render(n[0].upper() + n[1:len(n)], True, (0, 0, 0)), (x, 537))
            display.blit(game.FONT_20.render("{}/{}".format(poke.heal, poke.get_max_heal()), True, (0, 0, 0)), (x, 559))

    def draw_button(self, display: pygame.Surface) -> NoReturn:
        y = 350
        for i in range(4):
            color = ((0, 0, 0), (255, 255, 255)) if i == self.selected_y[0] else ((255, 255, 255), (0, 0, 0))
            utils.draw_rond_rectangle(display, 800, y, 50, 200, color[0])
            display.blit(game.FONT_24.render(self.button_text[i], True, color[1]), (810, y + 15))

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

    def draw_target_pokemon(self, display: pygame.Surface, poke: 'player_pokemon.PlayerPokemon', color, pose, text_color):
        utils.draw_rond_rectangle(display, pose[0], pose[1], 75, 180, color)
        if poke:
            display.blit(poke.get_front_image(0.8), (pose[0] - 25, pose[1] - 5))
            display.blit(game.FONT_24.render(poke.get_name(True), True, text_color), (pose[0] + 30, pose[1]  + 15))

    TO_SHOW = []

    def next_to_show(self) -> NoReturn:
        if len(Battle.TO_SHOW) > 0:
            self.selected_y = [0, 0]
            self.menu_action = [None, None]
            self.status = -1
            a = Battle.TO_SHOW[0]
            del Battle.TO_SHOW[0]
            a[0](**a[1])
        else:
            self.ability_escape()

    def setup_first_pokemon(self, team: BattleTeam, st: List[Optional['player_pokemon.PlayerPokemon']], enemy: bool):
        for i in range(len(st)):
            me = team.case[i]
            team_n = me.get_first_valid_n(True)
            data = {"case": i, "team_n": team_n, "enemy": enemy, "callback": self.next_to_show}
            Battle.TO_SHOW.append([self.launch_pokemon, data])

    def tick(self, display: pygame.Surface) -> bool:
        ps_t = utils.current_milli_time() - self.__start_time

        if ps_t < self.animation.get_during()[1]:
            if self.bool_matrix[1] and ps_t > self.animation.get_during()[0]:
                self.bool_matrix[1] = False
                self.load_asset()
            self.animation.tick(display, self, ps_t)
            return False

        if self.bool_matrix[3]:
            self.bool_matrix[3] = False
            self.setup_first_pokemon(self.__enemy_team, self.__enemy, True)
            self.setup_first_pokemon(self.__ally_team, self.__ally, False)
            self.next_to_show()

        if self.current_animation:
            if self.current_animation.tick(display):
                self.current_animation = None
                a, self.current_animation_callback = self.current_animation_callback, None
                if a:
                    a()
        else:
            if self.bool_matrix[4]:
                self.bool_matrix[4] = False
                sound_manager.MUSIC_CHANNEL.play(self.sound.sound, -1)

        # todo: use this
        rac: Optional['RenderAbilityCallback'] = None

        if self.current_play_ability:
            rac = self.current_play_ability.get_rac()

        self.draw_bg(display)
        for i in range(self.nb_enemy):
            self.draw_base(display, self.bg.enemy_base_coord[self.nb_enemy - 1][i][0], enemy=True, i=i)
            if self.__enemy[i]:
                self.draw_pokemon(display, True, i)
        for i in range(self.nb_ally):
            self.draw_base(display, self.bg.ally_base_coord[self.nb_ally - 1][i][0], enemy=False, i=i)
            if self.__ally[i]:
                self.draw_pokemon(display, False, i)

        if self.current_play_ability:
            if self.current_play_ability.tick(display):
                while len(self.queue_play_ability) > 0 and self.queue_play_ability[0].launcher_p.heal == 0:
                    del self.queue_play_ability[0]
                if len(self.queue_play_ability) > 0:
                    self.current_play_ability = self.queue_play_ability[0]
                    del self.queue_play_ability[0]
                    return False
                else:
                    self.current_play_ability = None
                    self.turn_count += 1

        if len(self.queue_play_ability) == 0:
            end_d = self.check_end()
            if end_d[0]:
                if self.bool_matrix[2]:
                    self.bool_matrix[2] = False
                    sound_manager.MUSIC_CHANNEL.stop()
                    d = hud.Dialog("Battle ned, close the game", need_morph_text=True, speed=20, none_skip=True,
                                   style=2)
                    game.game_instance.player.open_dialogue(d, over=True)
                return False

        if self.current_play_ability is None and game.game_instance.player.current_dialogue is None:
            if self.status == 0:
                self.draw_button(display)
            elif self.status == 1:
                self.draw_ability(display, self.selected_not_bot)
            elif self.status == 2:
                self.draw_target_select(display)

        # end fight here
        return False

        # end / is enemy_lose

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
            self.menu_action = [self.ability_action, self.ability_escape]
            self.status = 1

    def ability_action(self) -> NoReturn:
        ab = self.__ally[self.selected_not_bot].get_ability(self.selected_y[0])
        if ab and ab.pp > 0:
            if ab.ability.target != ability.TARGET_BOTH and len(self.__ally if ab.ability.target == ability.TARGET_ALLY else self.__enemy) == 1:
                self.do_attack(ab, ab.ability.target == ability.TARGET_ENEMY, 0)
            else:
                self.selected_y = [0, -1] if ab.ability.target == ability.TARGET_ENEMY else\
                                    [1, -1] if ab.ability.target == ability.TARGET_ALLY else [0, 2]
                self.selected_x = [0, max(self.nb_ally, self.nb_enemy)]
                self.current_ab = ab
                self.menu_action = [
                    lambda : self.do_attack(self.current_ab, self.selected_y[0] == 0, self.selected_x[1] - 1 - self.selected_x[0]),
                    self.target_menu_escape
                ]
                self.status = 2
        else:
            sound_manager.start_in_first_empty_taunt(sounds.BLOCK.get())

    def do_attack(self, ab: 'player_pokemon.PokemonAbility', enemy: bool, case: int):

        # don't show menu next turn
        self.ability_escape()
        ab.pp -= 1
        p = PlayAbility(ab.ability, self, self.get_poke_pose(False, self.selected_not_bot, simple=True), self.__ally[self.selected_not_bot], False, enemy, case)
        self.player_queue.append(p)

        if len(self.player_queue) == len(self.nb_not_bot):
            all_pa: List[PlayAbility] = self.player_queue
            for i in range(self.nb_enemy):
                poke = self.__enemy[i]
                ab_ = poke.ge_rdm_ability()
                enemy_ = random.randint(0, 1) == 1 if ab_.target == ability.TARGET_BOTH else ab_.target == ability.TARGET_ENEMY
                case_ = random.randint(0, self.nb_ally - 1) if enemy_ else random.randint(0, self.nb_enemy - 1)
                if ab_:
                    all_pa.append(PlayAbility(ab_, self, self.get_poke_pose(True, i, simple=True), poke, True, enemy_, case_))
            for i in range(self.nb_ally):
                if self.__ally_team.case[i].bot:
                    poke = self.__ally[i]
                    ab_ = poke.ge_rdm_ability()
                    enemy_ = random.randint(0, 1) == 1 if ab_.target == ability.TARGET_BOTH else ab_.target == ability.TARGET_ENEMY
                    case_ = random.randint(0, self.nb_enemy - 1) if enemy_ else random.randint(0, self.nb_ally - 1)
                    if ab_:
                        all_pa.append(PlayAbility(ab_, self, self.get_poke_pose(False, i, simple=True), poke, False, enemy_, case_))
            sorted(all_pa, key=lambda v: v.launcher_p.stats[pokemon.pokemon.SPEED])

            # reset heal  to max for display
            for pa in all_pa:
                pa.fix_heal()

            if len(all_pa) > 0:
                self.current_play_ability = all_pa[0]
                if len(all_pa) > 1:
                    self.queue_play_ability = all_pa[1:]
            self.player_queue.clear()
        else:
            self.selected_not_bot += 1

    def launch_pokemon(self, case: int, team_n: int, enemy: bool,
                       callback: Callable[[], NoReturn]) -> NoReturn:
        member = (self.__enemy_team if enemy else self.__ally_team).case[case]
        storage = self.__enemy if enemy else self.__ally
        poke = member.get_pks()[team_n]
        poke.set_use(True)
        storage[case] = poke
        self.current_animation = LaunchPokemonAnimation(member, case, team_n, enemy)
        self.current_animation_callback = callback

    def callback_pokemon(self, case: int, team_n: int, enemy: bool,
                         callback: Callable[[], NoReturn]) -> NoReturn:
        member = (self.__enemy_team if enemy else self.__ally_team).case[case]
        storage = self.__enemy if enemy else self.__ally
        poke = member.get_pks()[team_n]
        poke.set_use(False)
        storage[case] = None
        self.current_animation = CallBackPokemonAnimation(member, case, team_n, enemy)
        self.current_animation_callback = callback

    def ability_escape(self) -> NoReturn:
        self.selected_y = [0, 3]
        self.selected_x = [0, -1]
        self.menu_action = [self.action_menu_action, None]
        self.status = 0

    def on_key_escape(self) -> NoReturn:
        if self.menu_action[1]:
            self.menu_action[1]()

    def on_key_action(self) -> NoReturn:
        if self.menu_action[0]:
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

    def get_target_pos(self, ab: 'ability.AbstractAbility', l_enemy: bool, enemy: bool, case: int) -> List[Tuple[int, int]]:
        tar = ab.get_target(case, self.nb_enemy, self.nb_ally , enemy)
        back = []
        for i in range(self.nb_ally if l_enemy else self.nb_enemy):
            if tar[0][i]:
                back.append(self.get_poke_pose(not l_enemy, i, simple=True))
        for i in range(self.nb_enemy if l_enemy else self.nb_ally):
            if tar[1][i]:
                back.append(self.get_poke_pose(l_enemy, i, simple=True))
        return back

    def get_target(self, ab: 'ability.AbstractAbility', l_enemy: bool, enemy: bool, case: int) -> List['player_pokemon']:
        tar = ab.get_target(case, self.nb_enemy, self.nb_ally , enemy)
        back = []
        for i in range(self.nb_ally if l_enemy else self.nb_enemy):
            if tar[0][i]:
                back.append((self.__ally if l_enemy else self.__enemy)[i])
        for i in range(self.nb_enemy if l_enemy else self.nb_ally):
            if tar[1][i]:
                back.append((self.__enemy if l_enemy else self.__ally)[i])
        return back
