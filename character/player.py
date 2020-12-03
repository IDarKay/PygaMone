from utils import get_part_i
import game
from hud.hud import *
import hud.menu as hud_menu
import pygame
import collision


class Player(character.Character):

    def __init__(self, game_i: 'game.Game'):
        """

        :type game_i: game.Game
        """
        super().__init__((100, 100), (34, 50))

        self.image: List[pygame.Surface] = [get_part_i(character.NPC_IMAGE, cord, (34, 50)) for cord in [(0, 25, 17, 50), (17, 25, 34, 50), (0, 0, 17, 25), (17, 0, 34, 25)]]
        self.movement = [0, 0]
        self.speed = 2
        self.direction = 2
        self.current_dialogue = None
        self.freeze_time = 0
        self.is_action_press = False
        self.last_close_dialogue = current_milli_time()
        self.current_menu = None
        self.team = [player_pokemon.PlayerPokemon.from_json(p) for p in game_i.get_save_value("team", [])]
        self.normalize_team()

        # todo: change
        self.pc = [player_pokemon.PlayerPokemon.from_json(p) for p in game_i.get_save_value("pc", [])]

    def get_non_null_team_number(self) -> int:
        i = 0
        while self.team[i]:
            i += 1
        return i

    def normalize_team(self) -> NoReturn:
        if len(self.team) < 6:
            for i in range(len(self.team), 6):
                self.team.append(None)
        elif len(self.team) > 6:
            self.team = self.team[0:6]
            print("WARN to much pokemon in team deleting !")

    def add_pokemon_in_pc(self, pokemon: 'player_pokemon.PlayerPokemon') -> NoReturn:
        # todo: change
        self.pc.append(pokemon)

    def move_pokemon_to_pc(self, team_nb: int) -> NoReturn:
        if 0 <= team_nb < 6 and self.team[team_nb]:
            self.add_pokemon_in_pc(self.team[team_nb])
            # del to sort
            del self.team[team_nb]
            self.normalize_team()

    def switch_pokemon(self, team_nb1: int, team_nb2: int):
        if 0 <= team_nb1 < 6 and 0 <= team_nb2 < 6:
            self.team[team_nb1], self.team[team_nb2] = self.team[team_nb2], self.team[team_nb1]

    def save(self, data: Dict[str, Any]):
        team = []
        for t in self.team:
            if t:
                team.append(t.serialisation())
        data["team"] = team
        data["pc"] = [u.serialisation() for u in self.pc]

    def have_open_menu(self) -> bool:
        return self.current_menu is not None

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

    def open_dialogue(self, dialogue: 'Dialog', check_last_open: int = 0, over: bool = False) -> NoReturn:

        if 0 < check_last_open and check_last_open > current_milli_time() - self.last_close_dialogue and not over:
            return

        if self.current_dialogue and not over:
            raise RuntimeError("try open dialog while other is open")

        self.freeze_time = -2
        self.current_dialogue = dialogue

    def action_press(self) -> NoReturn:
        self.is_action_press = True
        if self.current_dialogue:
            if self.current_dialogue.press_action():
                self.close_dialogue()
        if self.current_menu:
            self.current_menu.on_key_action()

    def escape_press(self) -> NoReturn:
        if self.current_menu:
            self.current_menu.on_key_escape()

    def close_dialogue(self) -> NoReturn:
        self.last_close_dialogue = current_milli_time()
        self.current_dialogue = None
        self.freeze_time = 2

    def action_unpress(self) -> NoReturn:
        self.is_action_press = False

    def get_scroll_start(self) -> Tuple[int, int]:
        return int(self.rect.x-(game.SURFACE_SIZE[0]/2) + 8.5), int(self.rect.y - (game.SURFACE_SIZE[1]/2) + 12.5)

    def get_scroll_end(self) -> Tuple[int, int]:
        return int(self.rect.x + (game.SURFACE_SIZE[0] / 2) + 8.5), int(self.rect.y + (game.SURFACE_SIZE[1] / 2) + 12.5)

    def get_image(self) -> pygame.Surface:
        return self.image[self.direction]

    def move(self, co: 'collision') -> NoReturn:
        """

        :type co: collision.Collision
        """
        move = self.update_direction()
        if move:
            offset_y = (-1 if self.direction == 0 else 1 if self.direction == 2 else 0) * self.speed
            offset_x = (-1 if self.direction == 1 else 1 if self.direction == 3 else 0) * self.speed
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
            return False
        return True

    def on_key_x(self, value: float, up: bool) -> NoReturn:
        if up:
            self.movement[0] -= value
        else:
            self.movement[0] += value
        if self.current_menu:
            self.current_menu.on_key_x(value, not up)

    def on_key_y(self, value: float, up: bool) -> NoReturn:
        if up:
            self.movement[1] -= value
        else:
            self.movement[1] += value
        if self.current_menu:
            self.current_menu.on_key_y(value, not up)
        if self.current_dialogue and not up:
            self.current_dialogue.pres_y(value < 0)
