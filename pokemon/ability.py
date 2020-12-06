from typing import List, Dict, NoReturn, Any, Tuple
import utils
import pokemon.pokemon_type as p_type
import game_error as err
import game
import pygame
import pygame_gif
from pokemon.battle.battle import RenderAbilityCallback
import sound_manager

PHYSICAL = "PHYSICAL"
SPECIAL = "SPECIAL"
STATUS = "STATUS"

CATEGORYS: List[str] = [PHYSICAL, SPECIAL, STATUS]
ABILITY_SOUND_FOLDER = 'assets/sound/ability/'

class AbstractAbility(object):

    def __init__(self, id_, **data):
        self.id_ = id_
        self.__data = data
        self.type = p_type.TYPES[self.get_args("type", type_check=str)]
        self.category = self.get_args("category")
        if self.category not in CATEGORYS:
            raise err.AbilityParseError("Invalid category for {}".format(id_))
        self.pp = self.get_args("pp", type_check=int)
        self.max_pp = self.get_args("max_pp", type_check=int)
        self.power = self.get_args("power", type_check=int)
        self.accuracy = self.get_args("accuracy", type_check=int)
        self.contact = self.get_args("contact", default=False, type_check=bool)
        self.protect = self.get_args("protect", default=False, type_check=bool)
        self.magic_coat = self.get_args("magic_coat", default=False, type_check=bool)
        self.snatch = self.get_args("snatch", default=False, type_check=bool)
        self.mirror_move = self.get_args("mirror_move", default=False, type_check=bool)
        self.king_rock = self.get_args("king_rock", default=False, type_check=bool)
        self.high_critical = self.get_args("high_critical", default=False, type_check=bool)
        self.target = self.get_args("target")
        self.render_during = 0
        self.load = False
        self.need_sound = False
        del self.__data

    def get_name(self) -> NoReturn:
        return game.get_game_instance().get_message("ability." + self.id_)

    def get_args(self, key: str, default=None, type_check=None) -> Any:
        return self.get_args_2(self.__data, key, self.id_, default, type_check, _type="ability")

    def get_args_2(self, data: Dict[str, Any], key: str, _id: Any, default=None, type_check=None, _type="pokmon") -> Any:
        value = None
        if default is not None:
            value = data[key] if key in data else None if default == "NONE" else default
        else:
            if key not in data:
                raise err.PokemonParseError("No {} value for a {} ({}) !".format(key, _type, _id))
            value = data[key]
        if type_check:
            if value and not isinstance(value, type_check):
                raise err.PokemonParseError(
                    "Invalid var type for {} need be {} for {} ({})".format(key, type_check, _type, _id))
        return value

    def load_assets(self) -> bool:
        if not self.load:
            self.load = True
            if self.need_sound:
                self.sound = pygame.mixer.Sound(ABILITY_SOUND_FOLDER + self.id_ + ".mp3")
            return True
        return False

    def unload_assets(self) -> bool:
        if self.load:
            self.load = False
            if self.need_sound:
                del self.sound
            return False
        return True

    def get_rac(self, target: List[Tuple[int, int]],
               launcher: Tuple[int, int], ps_t: int, first_time: bool) -> RenderAbilityCallback:
        return RenderAbilityCallback()

    def render(self, display: pygame.display, target: List[Tuple[int, int]],
               launcher: Tuple[int, int], ps_t: int, first_time: bool) -> NoReturn:
        pass


class TackleAbility(AbstractAbility):
    def __init__(self):
        super().__init__(id_='tackle',
                         type="NORMAL",
                         category="PHYSICAL",
                         pp=34,
                         max_pp=56,
                         power=40,
                         accuracy=100,
                         contact=True,
                         protect=True,
                         mirror_move=True,
                         king_rock=True,
                         target=[[True, True, False],
                                 [False, False, False]])

        self.render_during = 2000


class EmberAbility(AbstractAbility):

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
                         target=[[True, True, False],
                                [False, True, False]])
        self.render_during = 2000
        self.need_sound = True

    def load_assets(self) -> bool:
        if super().load_assets():
            self.gif = pygame_gif.PygameGif('assets/textures/ability/ember.gif')
            return True
        return False


    def unload_assets(self) -> bool:
        if super().load_assets():
            del self.gif
            del self.g_i
            return True
        return False

    def render(self, display: pygame.display, target: List[Tuple[int, int]],
               launcher: Tuple[int, int], ps_t: int, first_time: bool) -> NoReturn:
        if first_time:
            self.g_i = self.gif.display(target[0])
            sound_manager.start_in_first_empty_taunt(self.sound)
        for t in target:
            self.g_i.render(display, (t[0] - 40, t[1] - 120))


load: bool = False