from typing import Optional, List, Dict, Any, Tuple, NoReturn
import game
import hud.hud as hud
import character.character as character
import hud.menu as hud_menu
import hud.menu_calass as menu_calass
import pygame
import collision
import pokemon.battle.battle as battle
import pokemon.player_pokemon as player_pokemon
import utils
import option

MAX_POKE_IN_BOX: int = 26
NB_BOX: int = 10


class PC(object):

    def __init__(self, data: List[Dict[str, Any]]):

        self.__box: List[List[Optional["player_pokemon.PCPlayerPokemon"]]] = []

        for i in range(NB_BOX):
            self.__box.append([None] * MAX_POKE_IN_BOX)

        for p in data:
            po = player_pokemon.PCPlayerPokemon.from_json(p)
            self.__box[po.box][po.case] = po

    def serialisation(self):
        v = []
        for a in self.__box:
            for u in a:
                if u:
                    v.append(u.serialisation())
        return v

    def get_poke(self, box: int, case: int) -> 'player_pokemon.PCPlayerPokemon':
        return self.__box[box][case]

    def add_first_case_empty(self, poke: 'player_pokemon.PlayerPokemon') -> bool:
        for b in range(NB_BOX):
            for c in range(MAX_POKE_IN_BOX):
                if self.get_poke(b, c) is None:
                    self.add_poke(poke, b, c)
                    return True
        return False

    def add_poke(self, poke: 'player_pokemon.PlayerPokemon', box: int, case: int) -> bool:
        if self.get_poke(box, case):
            return False
        self.__box[box][case] = player_pokemon.PCPlayerPokemon.from_none_pc(poke, box, case) if poke else None
        return True

    def remove(self, box: int, case: int) -> Optional['player_pokemon.PlayerPokemon']:
        p = self.get_poke(box, case)
        if p:
            self.__box[box][case] = None
            return p.to_none_pc()
        return None


class SpeedGetter(object):

    def __init__(self, time_millis: int):
        self.prevTimeMillis = time_millis
        self.lastFrameDuration = 0
        self.delta = 0

    def get_delta(self, time_millis: int, speed: float) -> int:
        self.lastFrameDuration = (time_millis - self.prevTimeMillis) / speed
        self.prevTimeMillis = time_millis
        self.delta += self.lastFrameDuration
        i = int(self.delta)
        self.delta -= float(i)
        return i


class Player(character.Character):
    # ["top", "left", "down", "right"]
    I = [

        (230, 375, 249, 401, False),  # 0
        (264, 374, 283, 402, False),  # 1
        (300, 374, 320, 402, False),  # 2
        (232, 438, 252, 466, False),  # 3
        (269, 440, 288, 468, False),  # 4
        (301, 440, 321, 467, False),  # 5
        (29, 543, 48, 570, False),  # 6
        (65, 543, 84, 570, False),  # 7
        (98, 543, 117, 570, False),  # 8
        (344, 519, 362, 546, False),  # 9
        (380, 519, 398, 547, False),  # 10
        (412, 519, 431, 547, False),  # 11

        (125, 375, 144, 401, True),
        (160, 373, 180, 401, True),
        (195, 373, 215, 401, True),
        (130, 440, 150, 468, True),
        (166, 440, 185, 468, True),
        (198, 440, 218, 468, True),
        (169, 508, 190, 536, True),
        (204, 508, 226, 536, True),
        (238, 508, 260, 536, True),
        (443, 518, 470, 546, True),
        (443, 518, 470, 546, True),
        (470, 518, 498, 546, True),

        (20, 375, 38, 401, False),
        (55, 374, 74, 402, False),
        (90, 374, 109, 402, False),
        (22, 439, 41, 466, False),
        (56, 441, 76, 469, False),
        (92, 441, 112, 469, False),
        (29, 508, 47, 536, False),
        (63, 508, 81, 536, False),
        (101, 508, 118, 536, False),
        (344, 551, 362, 578, False),
        (377, 551, 395, 578, False),
        (414, 550, 432, 578, False),

        (125, 375, 144, 401, False),
        (160, 373, 180, 401, False),
        (195, 373, 215, 401, False),
        (130, 440, 150, 468, False),
        (166, 440, 185, 468, False),
        (198, 440, 218, 468, False),
        (169, 508, 190, 536, False),
        (204, 508, 226, 536, False),
        (238, 508, 260, 536, False),
        (443, 518, 470, 546, False),
        (443, 518, 470, 546, False),
        (470, 518, 498, 546, False)

    ]

    def __init__(self, game_i: 'game.Game'):
        """

        :type game_i: game.Game
        """
        super().__init__((100, 100), (36, 52))
        IMAGE = pygame.image.load('assets/textures/character/main.png')
        self.image: List[pygame.Surface] = [
            utils.get_part_i(IMAGE, cord[0:4], (36, 52), flip=(True, False) if cord[4] else (False, False)) for cord in
            Player.I]

        self.movement = [0, 0]
        self.speed = 10
        self.speed_on_running = 6
        self.speed_cycling = 4
        self.speed_getter = SpeedGetter(utils.current_milli_time())
        self.direction = 2
        self.current_dialogue = None
        self.freeze_time = 0
        self.is_action_press = False
        self.last_close_dialogue = utils.current_milli_time()
        self.current_menu: Optional['menu_calass.Menu'] = None
        self.team: list['player_pokemon.PlayerPokemon'] = [player_pokemon.PlayerPokemon.from_json(p) for p
                                                           in game_i.get_save_value("team", [])]
        self.normalize_team()
        self.current_battle: Optional['battle.Battle'] = None
        self.speed_status = [False, False]
        self.is_cycling = False
        self.is_backhoe_loader = False

        self.pc: PC = PC(game_i.get_save_value("pc", []))

    def heal_team(self):
        for poke in self.team:
            if poke:
                poke.heal = poke.get_max_heal()
                for ab in poke.ability:
                    if ab:
                        ab.pp = ab.max_pp
                poke.combat_status.it.clear()

    def get_non_null_team_number(self) -> int:
        return 6 - self.team.count(None)

    def normalize_team(self) -> NoReturn:
        while None in self.team:
            self.team.remove(None)
        while len(self.team) < 6:
            self.team.append(None)
        if len(self.team) > 6:
            self.team = self.team[0:6]
            print("WARN to much pokemon in team deleting !")

    def move_pokemon_to_pc(self, team_nb: int) -> bool:
        if 0 <= team_nb < 6 and self.team[team_nb]:
            if self.pc.add_first_case_empty(self.team[team_nb]):
                # del to sort
                del self.team[team_nb]
                self.normalize_team()
                return True
            return False
        else:
            raise ValueError("invalid team nb")

    def switch_pc_pokemon(self, team_nb: int, pc_box: int, pc_case):
        if 0 <= team_nb < 6:
            p = self.pc.remove(pc_box, pc_case)
            self.pc.add_poke(self.team[team_nb], pc_box, pc_case)
            if p is None:
                del self.team[team_nb]
                self.normalize_team()
            else:
                self.team[team_nb] = p
        else:
            raise ValueError("invalid team nb")

    def switch_pokemon(self, team_nb1: int, team_nb2: int):
        if 0 <= team_nb1 < 6 and 0 <= team_nb2 < 6:
            self.team[team_nb1], self.team[team_nb2] = self.team[team_nb2], self.team[team_nb1]

    def save(self, data: Dict[str, Any]):
        team = []
        for t in self.team:
            if t:
                team.append(t.serialisation())
        data["team"] = team
        data["pc"] = self.pc.serialisation()

    def have_open_menu(self) -> bool:
        return self.current_menu is not None

    def start_battle(self, battle_: 'battle.Battle') -> bool:
        if self.current_dialogue or self.current_menu or self.current_battle:
            return False
        self.freeze_time = -2
        self.current_battle = battle_
        return True

    def open_menu(self, menu: 'hud_menu.Menu') -> bool:
        # check if can open
        if self.current_dialogue:
            return False
        self.freeze_time = -2
        self.current_menu = menu
        return True

    def close_menu(self) -> NoReturn:
        self.freeze_time = 2
        self.current_menu = None

    def open_dialogue(self, dialogue: 'Dialog', check_last_open: int = 0, over: bool = True) -> NoReturn:

        if 0 < check_last_open and check_last_open > utils.current_milli_time() - self.last_close_dialogue and not over:
            return

        if self.current_dialogue and not over:
            return

        self.freeze_time = -2
        self.current_dialogue = dialogue

    def close_dialogue(self) -> NoReturn:
        self.last_close_dialogue = utils.current_milli_time()
        self.current_dialogue = None
        self.freeze_time = 2 if self.current_dialogue is None and self.current_battle is None else -2

    def action_unpress(self) -> NoReturn:
        self.is_action_press = False

    def get_scroll_start(self) -> Tuple[int, int]:
        return int(self.rect.x - (game.SURFACE_SIZE[0] / 2) + 8.5), int(self.rect.y - (game.SURFACE_SIZE[1] / 2) + 12.5)

    # def get_scroll_end(self) -> Tuple[int, int]:
    #     return int(self.rect.x + (game.SURFACE_SIZE[0] / 2) + 8.5), int(self.rect.y + (game.SURFACE_SIZE[1] / 2) + 12.5)

    def get_image(self) -> pygame.Surface:
        if self.freeze_time == 0 and self.speed_status[0]:
            if self.is_cycling:
                if self.is_backhoe_loader:
                    return self.image[
                        self.direction * 12 + ((self.get_half(utils.current_milli_time() % 600, 600)) + 9)]
                return self.image[self.direction * 12 + ((self.get_half(utils.current_milli_time() % 600, 600)) + 6)]
            elif self.speed_status[1]:
                return self.image[self.direction * 12 + ((self.get_half(utils.current_milli_time() % 350, 350)) + 3)]
            else:
                return self.image[self.direction * 12 + (self.get_half(utils.current_milli_time() % 600, 600))]
        else:
            if self.is_cycling:
                if self.is_backhoe_loader:
                    return self.image[self.direction * 12 + 9]
                return self.image[self.direction * 12 + 6]
            return self.image[self.direction * 12]

    def get_half(self, n, a):
        t = a // 2
        return 1 if n < t else 2
        # return 0 if n < t else (1 if n < 2 * t else 2)

    def move(self, co: 'collision') -> NoReturn:
        """

        :type co: collision.Collision
        """
        move = self.update_direction()
        speed = self.speed_cycling if self.is_cycling else (
            self.speed_on_running if self.speed_status[1] else self.speed)
        speed = self.speed_getter.get_delta(utils.current_milli_time(), speed)
        speed = min(10, speed)
        if move:
            offset_y = (-1 if self.direction == 0 else 1 if self.direction == 2 else 0) * speed
            offset_x = (-1 if self.direction == 1 else 1 if self.direction == 3 else 0) * speed
        else:
            offset_x, offset_y = 0, 0
        box = self.get_box()

        col = co.get_collision(box, offset_x, offset_y)
        if self.freeze_time != 0:
            return
        if col and (not game.game_instance.ignore_collision):
            self.set_render_from_scroll(game.came_scroll, col)
        else:
            self.rect.x += offset_x
            self.rect.y += offset_y

    # def get_box(self) -> NoReturn:
    #     s_coord = self.get_render_coord(game.came_scroll)
    #     return game.collision.SquaredCollisionBox(s_coord[0], s_coord[1] + 40, s_coord[0] + self.size[0],
    #                                               s_coord[1] + self.size[1])

    def update_direction(self) -> bool:
        if self.movement[1] < 0:
            self.direction = 0
        elif self.movement[1] > 0:
            self.direction = 2
        elif self.movement[0] > 0:
            self.direction = 3
        elif self.movement[0] < 0:
            self.direction = 1
        else:
            self.speed_status = [False, self.speed_status[1]]
            return False
        self.speed_status = [True, self.speed_status[1]]
        return True

    def on_key_sprint(self, joy: bool, down: bool):
        if option.HOLD_SPRINT or joy:
            self.speed_status[1] = down
        elif down:
            self.speed_status[1] = not self.speed_status[1]

    def cycling_press(self):
        if self.current_dialogue:
            pass
        if self.current_menu:
            self.current_menu.on_key_bike()
        elif self.current_battle:
            pass
        elif game.game_instance.level.can_cycling:
            self.is_cycling = not self.is_cycling
        else:
            self.open_dialogue(hud.Dialog("dialog.cant_bike", speed=20, speed_skip=True, need_morph_text=True, style=2),
                               over=False)

    def backhoe_loader_press(self):
        self.is_backhoe_loader = not self.is_backhoe_loader

    def escape_press(self) -> NoReturn:
        if self.current_menu:
            self.current_menu.on_key_escape()
        elif self.current_battle:
            self.current_battle.on_key_escape()

    def action_press(self) -> NoReturn:
        self.is_action_press = True
        if self.current_dialogue:
            if self.current_dialogue.press_action():
                self.close_dialogue()
        if self.current_menu:
            self.current_menu.on_key_action()
        elif self.current_battle:
            self.current_battle.on_key_action()

    def on_key_x(self, value: float, up: bool, joy: bool = False) -> NoReturn:
        if joy:
            up = value == 0
            self.movement[0] = Player.joy_round(value)
        elif up:
            self.movement[0] -= value
        else:
            self.movement[0] += value
        if self.current_menu:
            self.current_menu.on_key_x(value, not up)
        elif self.current_battle and not up:
            self.current_battle.on_key_x(value < 0)

    def on_key_y(self, value: float, up: bool, joy: bool = False) -> NoReturn:
        if joy:
            up = value == 0
            self.movement[1] = Player.joy_round(value)
        elif up:
            self.movement[1] -= value
        else:
            self.movement[1] += value
        if self.current_menu:
            self.current_menu.on_key_y(value, not up)
        if self.current_dialogue and not up:
            self.current_dialogue.pres_y(value < 0)
        elif self.current_battle and not up:
            self.current_battle.on_key_y(value < 0)

    def get_badge_amount(self) -> int:
        # todo: change
        return 0

    @staticmethod
    def joy_round(v: float) -> float:
        return 0 if v == 0 else -1 if v < 0 else 1

    def menu_press(self):
        if self.current_dialogue:
            pass
        if self.current_menu:
            self.current_menu.on_key_menu()
        elif self.current_battle:
            pass
        elif not self.current_menu:
            self.open_menu(hud_menu.MainMenu(self))
