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

SURFACE_SIZE = (1060, 600)

# 130 / 40
BASE_SIZE = (390, 120)
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
                base_x = WildAnimation.START_POINT[0] + (battle_.bg.enemy_base_coord[0][0] - WildAnimation.START_POINT[0]) * \
                         min(1.0, (ps_t - 1000) / 1000)
                base_x_2 = WildAnimation.START_POINT[1] - (WildAnimation.START_POINT[1] - battle_.bg.ally_base_coord[0][0]) * \
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
                    launcher: Tuple[int, int], launcher_p: 'player_pokemon.PlayerPokemon', enmy: bool):

        self.launcher_p: 'player_pokemon.PlayerPokemon' = launcher_p
        self.__ab: 'ability.AbstractAbility' = ab
        self.__targets_p: List['player_pokemon'] = bat.get_target(ab, enmy)
        self.__targets: List[Tuple[int, int]] = bat.get_target_pos(ab, enmy)
        self.launcher: Tuple[int, int] = launcher
        self.__first_time: bool = True
        self.__start_time: int = 0
                                        # attack / crit
        self.__bool_matrix: List[bool] = [True] * 6
        self.__d_status: Tuple[List[Tuple[int, int]], bool] = self.launcher_p.get_damage(self.__targets_p, self.__ab)
        print("d_status", self.__d_status)
        self.__max_type_multi = max(self.__d_status[0], key= lambda k: k[1])[1]
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
                        s = sounds.HIT_NOT_VERY_EFFECTIVE if (self.__max_type_multi < 1) else sounds.HIT_NORMAL_DAMAGE if (self.__max_type_multi == 1) else sounds.HIT_SUPER_EFFECTIVE
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


class Battle(object):
    # END_BASE_POINT: Tuple[int, int] = (SURFACE_SIZE[0] - 390, 0)

    def __init__(self, ally: List['player_pokemon.PlayerPokemon'], enemy: List['player_pokemon.PlayerPokemon'],
                 wild: bool, animation: Callable[[], StartAnimation] = WildAnimation,
                 base: Tuple[int, int, int, int] = GRASS_PLATE_BASE, bg: 'background.BackGround' = background.FOREST,
                 sound: str=sounds.BATTLE_DPP_TRAINER
                 ):
        self.sound: 'sounds.Sound' = sound
        self.__ally = ally
        self.__enemy = enemy
        if not (0 < len(self.__ally) < 4) or not (0 < len(self.__enemy) < 4):
            raise ValueError("ally and enemy len need be in [1:3]")
        self.wild = wild
        self.__start_time = utils.current_milli_time()
        self.poke_ball = pygame.transform.scale(items.POKE_BALL.image,
                                                (game.SURFACE_SIZE[1] // 8, game.SURFACE_SIZE[1] // 8))
        self.start_sound: pygame.mixer.Sound = pygame.mixer.Sound('assets/sound/music/pokemon-start-battle.mp3')
        self.animation: StartAnimation = animation()
        self.bool_matrix = [True] * 4
        self.base: Union[Tuple[int, int, int, int], pygame.Surface] = base
        self.bg: 'background.BackGround' = bg
        self.bg_image: Optional[pygame.Surface] = None
        self.selected_y = [0, 3]
        self.menu_action: List[Callable[[], NoReturn]] = [self.action_menu_action, None]
        self.status = 0
        self.turn_count = 0
        self.current_play_ability: Optional[PlayAbility] = None
        self.queue_play_ability: List[PlayAbility] = []

    def load_asset(self):
        self.sound.load()
        sounds.HIT_NORMAL_DAMAGE.load()
        sounds.HIT_NOT_VERY_EFFECTIVE.load()
        sounds.HIT_SUPER_EFFECTIVE.load()
        self.animation.load_asset()
        self.base = utils.get_part_i(pygame.image.load('assets/textures/battle/base_2.png'), self.base, (390, 120))
        self.bg_image = pygame.transform.scale(pygame.image.load(self.bg.bg_path), game.SURFACE_SIZE)
        self.button_text = [game.game_instance.get_message(t) for t in ['attack', 'team', 'bag', 'run_away']]
        self.arrow = utils.get_part_i(menu.MENU_IMAGE, (0, 64, 22, 91), (33, 41))
        for p in self.__ally + self.__enemy:
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
        for p in self.__ally + self.__enemy:
            for a in p.ability:
                if a:
                    a.ability.load_assets()

    def need_render(self):
        return utils.current_milli_time() - self.__start_time <= self.animation.get_during()[0]

    def draw_base(self, display: pygame.Surface, x, enemy: bool, i=0):
        if enemy:
            display.blit(self.base, (x, self.bg.enemy_base_coord[i][1]))
        else:
            display.blit(self.base, (x, self.bg.ally_base_coord[i][1]))

    def draw_bg(self, display: pygame.Surface):
        display.blit(self.bg_image, (0, 0))

    poly_enemy_1 = ((860, 20), (960, 20), (940, 50), (840, 50))
    poly_enemy_2 = ((960, 20), (1060, 20), (1060, 50), (940, 50))
    poly_ally_1 = ((220, 530), (120, 530), (100, 580), (200, 580))
    poly_ally_2 = ((120, 530), (0, 530), (0, 580), (100, 580))
    INFO_enemy = 860,
    INFO_ally = 20,

    def get_poke_pose(self, enemy: bool, i: int, simple: bool = False) -> Tuple[int, int]:
        c = self.bg.enemy_base_coord[i] if enemy else self.bg.ally_base_coord[i]
        poke = self.__enemy[i] if enemy else self.__ally[i]
        displayer = poke.poke.display if enemy else poke.poke.back_display
        if simple:
            return c[0] + (BASE_SIZE[0]) // 2, int(c[1] + (BASE_SIZE[1] * 0.75))
        return c[0] + (BASE_SIZE[0] // 2) - (displayer.image_size[0] // 2), int(c[1] - displayer.image_size[1] + (BASE_SIZE[1] * 0.75))

    GRADIENT = [(0, 229, 29), (25, 205, 27), (50, 181, 26), (75, 157, 25), (100, 133, 24), (125, 109, 23), (150, 85, 22), (175, 61, 21), (200, 37, 20), (225, 14, 19)]

    def bar_color(self, heal, max_heal):
        return Battle.GRADIENT[utils.min_max(0, 9 - int(((heal / max_heal) * 10)), 9)]

    def draw_pokemon(self, display: pygame.Surface, enemy: bool, i):
        p_c = self.get_poke_pose(enemy, i)
        if enemy:
            poke = self.__enemy[i]
            x = Battle.INFO_enemy[i]
            display.blit(poke.poke.display.image, p_c)
            pygame.draw.polygon(display, (246, 250, 253), Battle.poly_enemy_1)
            pygame.draw.polygon(display, (255, 255, 255), Battle.poly_enemy_2)

            utils.draw_progress_bar(display, (x, 40), (170, 5), (100, 100, 100), self.bar_color(poke.heal, poke.get_max_heal()),
                                    poke.heal / poke.get_max_heal())
            lvl = game.FONT_20.render("N.{}".format(poke.lvl), True, (0, 0, 0))
            display.blit(lvl, (x + 170 - lvl.get_rect().size[0], 21))
            n = poke.get_name()
            display.blit(game.FONT_16.render(n[0].upper() + n[1:len(n)], True, (0, 0, 0)), (x, 25))
        else:
            poke = self.__ally[i]
            x = Battle.INFO_ally[i]
            display.blit(poke.poke.back_display.image, p_c)
            pygame.draw.polygon(display, (246, 250, 253), Battle.poly_ally_1)
            pygame.draw.polygon(display, (255, 255, 255), Battle.poly_ally_2)
            utils.draw_progress_bar(display, (x, 551), (170, 5), (100, 100, 100), self.bar_color(poke.heal, poke.get_max_heal()),
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

    def draw_ability(self, display: pygame.Surface) -> NoReturn:
        x = 800
        y = 400
        for i in range(4):
            utils.draw_ability_2(display, (x, y), self.__ally[0].get_ability(i), border=self.selected_y[0] == i)
            if self.selected_y[0] == i:
                display.blit(self.arrow, (x - 50, y + 2))
            y += 50

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
            sound_manager.MUSIC_CHANNEL.play(self.sound.sound, -1)

        # todo: use this
        rac: Optional['RenderAbilityCallback'] = None

        if self.current_play_ability:
            rac = self.current_play_ability.get_rac()

        self.draw_bg(display)
        for i in range(len(self.__enemy)):
            self.draw_base(display, self.bg.enemy_base_coord[i][0], enemy=True, i=i)
            self.draw_pokemon(display, True, i)
        for i in range(len(self.__ally)):
            self.draw_base(display, self.bg.ally_base_coord[i][0], enemy=False, i=i)
            self.draw_pokemon(display, False, i)

        if self.current_play_ability:
            if self.current_play_ability.tick(display):
                while len(self.queue_play_ability) > 0 and self.queue_play_ability[0].launcher_p.heal == 0:
                    del self.queue_play_ability[0]
                if len(self.queue_play_ability) > 0:
                    self.current_play_ability = self.queue_play_ability[0]
                    del self.queue_play_ability[0]
                else:
                    self.current_play_ability = None
                    self.turn_count += 1

        if len(self.queue_play_ability) == 0:
            end_d = self.check_end()
            if end_d[0]:
                if self.bool_matrix[2]:
                    self.bool_matrix[2] = False
                    sound_manager.MUSIC_CHANNEL.stop()
                    d = hud.Dialog("Battle ned, close the game", need_morph_text=True, speed=20, none_skip=True, style=2)
                    game.game_instance.player.open_dialogue(d, over=True)
                return False
        if self.current_play_ability is None:
            if self.status == 0:
                self.draw_button(display)
            elif self.status == 1:
                self.draw_ability(display)

        # end fight here
        return False

                                # end / is enemy_lose
    def check_end(self) -> Tuple[bool, bool]:
        # todo : team
        en_end = True
        for p in self.__enemy:
            if p.heal > 0:
                en_end = False
                break
        al_end = True
        for p in self.__ally:
            if p.heal > 0:
                al_end = False
                break
        return en_end or al_end, en_end


    def action_menu_action(self) -> NoReturn:
        if self.selected_y[0] == 0:
            self.selected_y = [0, 3]
            self.menu_action = [self.ability_action, self.ability_escape]
            self.status = 1

    def ability_action(self) -> NoReturn:
        ab = self.__ally[0].get_ability(self.selected_y[0])
        if ab and ab.pp > 0:
            # return main menu fo next turn
            self.ability_escape()
            ab.pp -= 1
            p = PlayAbility(ab.ability, self, self.get_poke_pose(False, 0, simple=True), self.__ally[0], False)
            all_pa: List[PlayAbility] = [p]
            for i in range(len(self.__enemy)):
                poke = self.__enemy[i]
                ab = poke.ge_rdm_ability()
                print("move", ab)
                if ab:
                    all_pa.append(PlayAbility(ab, self, self.get_poke_pose(True, i, simple=True), poke, True))
            for i in range(1, len(self.__ally)):
                poke = self.__ally[i]
                ab = poke.ge_rdm_ability()
                if ab:
                    all_pa.append(PlayAbility(ab, self, self.get_poke_pose(False, i, simple=True), poke, False))
            sorted(all_pa, key=lambda v: v.launcher_p.stats[pokemon.pokemon.SPEED])

            # reset heal  to max for display
            for pa in all_pa:
                pa.fix_heal()

            if len(all_pa) > 0:
                self.current_play_ability = all_pa[0]
                if len(all_pa) > 1:
                    self.queue_play_ability = all_pa[1:]
        else:
            pass
            # todo: none sound


    def ability_escape(self) -> NoReturn:
        self.selected_y = [0, 3]
        self.menu_action = [self.action_menu_action, None]
        self.status = 0

    def on_key_escape(self) -> NoReturn:
        if self.menu_action[1]:
            self.menu_action[1]()

    def on_key_action(self) -> NoReturn:
        if self.menu_action[0]:
            self.menu_action[0]()

    def on_key_x(self, left: bool) -> NoReturn:
        pass

    def on_key_y(self, up: bool) -> NoReturn:
        if up:
            if self.selected_y[0] > 0:
                self.selected_y[0] -= 1
        else:
            if self.selected_y[0] < self.selected_y[1]:
                self.selected_y[0] += 1

    def get_target_pos(self, ab: 'ability.AbstractAbility', enemy: bool) -> List[Tuple[int, int]]:
        back = []
        for i in range(len(self.__ally if enemy else self.__enemy)):
            if ab.target[0][i]:
                back.append(self.get_poke_pose(not enemy, i, simple=True))
        for i in range(len(self.__enemy if enemy else self.__ally)):
            if ab.target[1][i]:
                back.append(self.get_poke_pose(enemy, i, simple=True))
        return back

    def get_target(self, ab: 'ability.AbstractAbility', enemy: bool) -> List['player_pokemon']:
        back = []
        for i in range(len(self.__ally if enemy else self.__enemy)):
            if ab.target[0][i]:
                back.append((self.__ally if enemy else self.__enemy)[i])
        for i in range(len(self.__enemy if enemy else self.__ally)):
            if ab.target[1][i]:
                back.append((self.__enemy if enemy else self.__ally)[i])
        return back
