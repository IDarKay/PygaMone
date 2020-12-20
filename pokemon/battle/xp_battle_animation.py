from typing import NoReturn, Optional
from abc import abstractmethod, ABC
from pokemon.battle.animation import Animation
import pokemon.battle.battle as battle
import utils
import pygame
import game
import pokemon.player_pokemon as player_pokemon
import pokemon.pokemon as pokemon
import hud.hud as hud
import hud.forget_ability_menu as forget_ability_menu
import pokemon.abilitys_ as abilitys_
import sound_manager
import sounds


class XpA(Animation, ABC):

    def __init__(self, bat: 'battle.Battle'):
        self._bat = bat
        self._init = False
        self.action = False
        self._start = 0


class XpAnimation(XpA):

    def __init__(self, bat: 'battle.Battle', xp_tab: list[int]):
        super().__init__(bat)
        self.__xp_tab = xp_tab

    def tick(self, display: pygame.Surface) -> bool:
        if not self._init:
            self._init = True
            # self.start = utils.current_milli_time()
            game.game_instance.player.open_dialogue(hud.Dialog("battle.xp.team_won_xp",
                                                               speed=25, need_morph_text=True, none_skip=True, style=2))
        draw_xp_pokemon(display, None)
        # draw_pokemon_stats(display, game.game_instance.player.team[0], {st: 5 for st in pokemon.STATS}, )
        if self.action:
            self._bat.TO_SHOW.insert(0,
                lambda: self._bat.start_new_animation(XpAnimationAdd(self._bat, self.__xp_tab, None)))
            game.game_instance.player.close_dialogue()
            return True
        return False

    def on_key_action(self) -> bool:
        self.action = True
        sound_manager.start_in_first_empty_taunt(sounds.PLINK)
        return True


class XpAnimationAdd(XpA):

    def __init__(self, bat: 'battle.Battle', xp_tab: list[int], i: Optional[int],
                 edit: Optional[list[Optional[tuple[int, dict[str, int]]]]] = None,
                 i_: tuple[Optional[int], Optional[int]] = (None, None),
                 attack_edit: Optional[list[Optional[list[str]]]] = None):
        super().__init__(bat)
        self.attack_edit = attack_edit
        self.__xp_tab = xp_tab
        self.__edit: Optional[list[Optional[tuple[int, dict[str, int]]]]] = edit
        self.__i = i
        self.__i_ = i_
        pl = game.game_instance.player
        if not self.__edit:
            self.__edit = []
            for i in range(6):
                if poke := pl.team[i]:
                    stats = poke.stats.copy()
                    level_up, old_lvl, new_lvl = poke.add_xp(xp_tab[i])
                    if level_up:
                        for st in pokemon.STATS:
                            stats[st] = poke.stats[st] - stats[st]
                        self.__edit.append((new_lvl - old_lvl, stats))
                    else:
                        self.__edit.append(None)
            self.__i = self.get_next_i()
        if 0 <= self.__i < 6:
            self.poke = pl.team[self.__i]

    def get_next_i(self, base_i: Optional[int] = None) -> int:
        for i in range(len(self.__edit)):
            if self.__edit[i] and (base_i is None or i > base_i):
                return i
        return -1

    def tick(self, display: pygame.Surface) -> bool:
        if not self._init:
            self._init = True
            if 0 <= self.__i < 6:
                sound_manager.start_in_first_empty_taunt(sounds.LEVEL_UP)
                game.game_instance.player.open_dialogue(
                    hud.Dialog("battle.xp.poke_level_up", need_morph_text=True, none_skip=True, style=2, speed=25,
                               text_var=[self.poke.get_name(True), self.poke.lvl]))
            else:
                self.action = 2
        draw_xp_pokemon(display, [(key, value and value[0] > 0) for key, value in zip(self.__xp_tab, self.__edit)])
        if self.action == 1:
            if self.__i != -1:
                self.action += 1
                self._start = utils.current_milli_time()
            else:
                self.action = 3
        if 0 <= self.__i < 6:
            fusion = 1
            if self.action > 1:
                fusion = 1 - min((utils.current_milli_time() - self._start) / 200, 1)
            draw_pokemon_stats(display, self.poke, self.__edit[self.__i][1], fusion)
        if self.action > 2:
            if self.__i != -1:
                self._bat.TO_SHOW.insert(0, lambda: self._bat.start_new_animation(PokemonWonAttackAnimation(
                    self._bat, self.__xp_tab, self.__i_, self.__edit, self.get_next_i(self.__i), self.attack_edit)))
                # self._bat.TO_SHOW.append(lambda: self._bat.start_new_animation(XpAnimationAdd(
                #     self._bat, self.__xp_tab, self.get_next_i(self.__i), self.__edit)))
            game.game_instance.player.close_dialogue()
            return True

        return False

    def on_key_action(self) -> bool:
        self.action += 1
        sound_manager.start_in_first_empty_taunt(sounds.PLINK)
        return True


x = lambda y: (y - 900) / (-100 / 53)


class PokemonWonAttackAnimation(XpA):

    def __init__(self, bat: 'battle.Battle', xp_tab: list[int], i_: tuple[Optional[int], Optional[int]],
                 edit: list[Optional[tuple[int, dict[str, int]]]], xp_i: int,
                 attack_edit: Optional[list[Optional[list[str]]]] = None):
        super().__init__(bat)
        self.xp_i = xp_i
        self.__xp_tab = xp_tab
        self.__edit: Optional[list[Optional[tuple[int, dict[str, int]]]]] = edit
        self.__poke_i, self.attack_i = i_
        self.__attack_edit: Optional[list[Optional[list[str]]]] = attack_edit
        self.__poke = None
        pl = game.game_instance.player
        if self.__attack_edit is None:
            self.__attack_edit = []
            for i in range(len(self.__edit)):
                el = self.__edit[i]
                if (poke := pl.team[i]) and el and el[0] > 0:
                    c_l = []
                    for lvl in range(poke.lvl - el[0] + 1, poke.lvl + 1):
                        for e in poke.poke.get_possible_ability_at_lvl(lvl):
                            c_l.append(e)
                    self._bat.evolution_table[i] = poke.can_evolve()
                    self.__attack_edit.append(c_l if len(c_l) > 0 else None)
                else:
                    self.__attack_edit.append(None)
            self.__poke_i, self.attack_i = self.get_next_i((None, None))
        if 0 <= self.__poke_i < 6:
            self.__poke = pl.team[self.__poke_i]
            self.__c_ability = self.__attack_edit[self.__poke_i][self.attack_i]
            print(len(self.__poke.ability))
            self.__type = 0 if len(self.__poke.ability) < 4 else 1
            print("type", self.__type)
        self.__answer = None
        self.__menu_answer = None
        self.__old_ab = None

    def get_next_i(self, i_: tuple[Optional[int], Optional[int]]) -> tuple[int, int]:
        if i_[1] == -1:
            return -1, -1
        if i_[0] is not None and i_[1] is None:
            raise ValueError("if i_[0] is not None i_[1] must be not None")
        if i_[0] is not None and (c := self.__attack_edit[i_[0]]) and len(c) - 1 > i_[0]:
            return i_[0], i_[1] + 1
        for i in range(len(self.__attack_edit)):
            if self.__attack_edit[i] and (i_[0] is None or i > i_[0]):
                return i, 0
        return -1, -1

    def tick(self, display: pygame.Surface) -> bool:
        if not self._init:
            self._init = True
            if self.__poke:
                if self.__type == 0:
                    self.__poke.add_ability(0, self.__c_ability)
                    sound_manager.start_in_first_empty_taunt(sounds.LEVEL_UP)
                    game.game_instance.player.open_dialogue(
                        hud.Dialog("battle.xp.learn", need_morph_text=True, none_skip=True, style=2, speed=25,
                                   text_var=[abilitys_.ABILITYS[self.__c_ability].get_name()]))
                else:
                    game.game_instance.player.open_dialogue(
                        hud.Dialog("battle.xp.want_lean", need_morph_text=True, none_skip=True, style=2, speed=25,
                                   text_var=[abilitys_.ABILITYS[self.__c_ability].get_name()]))
            else:
                self.next()
                return True
        draw_xp_pokemon(display, [(key, value and value[0] > 0) for key, value in zip(self.__xp_tab, self.__edit)])
        if self.__type == 0:
            if self.action:
                self.next()
                return True
        else:
            if self.action == 1:
                if self.__type == 0:
                    self.next()
                    return True
                self.action += 1
                ask = game.game_instance.get_message("battle.xp.forget_ability.yes"), \
                         game.game_instance.get_message("battle.xp.forget_ability.no")
                print("open")
                game.game_instance.player.open_dialogue(
                    hud.QuestionDialog("battle.xp.forget_ability.text", self.question_callback,
                                       ask, need_morph_text=True, style=2,
                                       speed=25,
                                       text_var=[abilitys_.ABILITYS[self.__c_ability].get_name()]), over=True,)
            elif self.action == 2 and self.__answer is not None:
                self.action += 1
                if self.__answer == 0:
                    game.game_instance.player.open_menu(forget_ability_menu.ForgetAbility(
                        game.game_instance.player,
                        self.__poke,
                        self.__c_ability, self.menu_callback))
                else:
                    game.game_instance.player.open_dialogue(
                        hud.Dialog("battle.xp.haven_t_lean", need_morph_text=True, none_skip=True, style=2, speed=25,
                                   text_var=[self.__poke.get_name(True), abilitys_.ABILITYS[self.__c_ability].get_name()]))
            elif self.action == 4:
                self.action += 1
                if self.__answer == 0:
                    if self.__menu_answer == -1:
                        game.game_instance.player.open_dialogue(
                            hud.Dialog("battle.xp.haven_t_lean", need_morph_text=True, none_skip=True, style=2,
                                       speed=25,
                                       text_var=[self.__poke.get_name(True),
                                                 abilitys_.ABILITYS[self.__c_ability].get_name()]))
                    else:
                        self.__old_ab = self.__poke.get_ability(self.__menu_answer)
                        self.__poke.add_ability(self.__menu_answer, self.__c_ability)
                        sound_manager.start_in_first_empty_taunt(sounds.LEVEL_UP)
                        game.game_instance.player.open_dialogue(
                            hud.Dialog("battle.xp.learn_2", need_morph_text=True, none_skip=True, style=2,
                                       speed=100))
                else:
                    self.next()
                    return True
            elif self.action == 6:
                self.action += 1
                if self.__menu_answer == -1:
                    self.next()
                    return True
                else:
                    game.game_instance.player.open_dialogue(
                        hud.Dialog("battle.xp.learn_2_end", need_morph_text=True, none_skip=True, style=2, speed=25,
                                   text_var=[self.__poke.get_name(True), self.__old_ab.ability.get_name() if self.__old_ab else '----',
                                             abilitys_.ABILITYS[self.__c_ability].get_name()]))
            elif self.action >= 8:
                self.next()
                return True
        return False

    def menu_callback(self, i):
        self.__menu_answer = i

    def next(self):
        game.game_instance.player.close_dialogue()
        self._bat.TO_SHOW.insert(0, lambda: self._bat.start_new_animation(XpAnimationAdd(
            self._bat, self.__xp_tab, self.xp_i, self.__edit,
            self.get_next_i((self.__poke_i, self.attack_i)), self.__attack_edit)))
        # self._bat.TO_SHOW.append(lambda: self._bat.start_new_animation(PokemonWonAttackAnimation(
        #     self._bat, self.__xp_tab, self.get_next_i((self.__poke_i, self.attack_i)), self.__edit, self self.__attack_edit)))

    def question_callback(self, name, index):
        self.__answer = index

    def on_key_action(self) -> bool:
        print("before", self.action)
        if self.action != 2:
            sound_manager.start_in_first_empty_taunt(sounds.PLINK)
            self.action += 1
            print("after", self.action)
        return True


def draw_pokemon_stats(display: pygame.Surface, poke: 'player_pokemon.PlayerPokemon', up: dict[str, int],
                       fusion: float = 1):
    pygame.draw.rect(display, "#FFFFFF", (583, 150, 350, 214), border_radius=4)
    y = 150
    for st in pokemon.STATS:
        y += 10
        display.blit(game.FONT_24.render(game.get_game_instance().get_message(f'stats.{st}'), True, (0, 0, 0))
                     , (600, y))
        stats_n = poke.get_stats(st, False)
        if fusion != 0:
            stats_n -= up[st]
        display.blit(tx := game.FONT_24.render(str(stats_n), True, (0, 0, 0)), (800 - tx.get_size()[0], y))
        if fusion != 0:
            add_x = 800 + 30 * fusion
            display.blit(game.FONT_24.render(f'+ {up[st]}', True, "#7e0000"), (add_x, y))

        y += 24


def draw_xp_pokemon(display: pygame.Surface, progress: Optional[list[tuple[int, bool]]]) -> NoReturn:
    pygame.draw.polygon(display, (255, 255, 255), ((477, 0), (583, 0), (265, 600), (159, 600)))
    pygame.draw.polygon(display, "#f4f4f4", ((0, 0), (477, 0), (159, 600), (0, 600)))
    y = 10
    h = 70
    c = 5
    for i in range(6):
        pygame.draw.polygon(display, "#e0e0e0", ((0, y), (x(y), y), (x(y + h), y + h), (0, y + h)))
        poke = game.game_instance.player.team[i]
        if poke:
            im = poke.get_front_image(0.7)
            delta_x, delta_y = utils.get_first_color(im)
            display.blit(im, (40 - delta_x // 2, y + 60 - delta_y))
            display.blit(game.FONT_24.render(poke.get_name(True), True, (0, 0, 0)), (80, y + 10))
            display.blit(game.FONT_24.render(f'N. {poke.lvl}', True, (0, 0, 0)), (80, y + h - 5 - game.FONT_SIZE_24[1]))
            if progress and (xp_p := progress[i][0]) > 0:
                display.blit(tx := game.FONT_24.render(f'+ {(xp_p):,}', True, (0, 0, 0)),
                             (230 - tx.get_size()[0], y + h - 5 - game.FONT_SIZE_24[1]))
                if progress[i][1]:
                    display.blit(game.FONT_24.render(game.game_instance.get_message("level_up"), True, (227, 25, 45)),
                                 (240, y + 10))

            xp = poke.current_xp_status()
            utils.draw_progress_bar(display, (80, y + h - 4), (150, 4), "#5a5a5a", "#45c1fd", xp[0] / xp[1])

        y += h + c
