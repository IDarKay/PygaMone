from typing import NoReturn, List, Dict, Callable, Tuple, Optional
import structure
import game_error as er
import json
import game
import collections
import pygame
import random
import triggers
import collision as col
import character.npc as npc
import sound_manager

EMPTY = "EMPTY"
FLOOR = "floor"
LAYER_1 = "layer_1"


# class Key(object):
#
#     def __init__(self, key: str, data: Dict[str, Any]):
#         self.key = key
#         self.ref = data["ref"] if "ref" in data else None
#         if not self.ref:
#             raise er.LevelParseError("No ref for a layer with key {}".format(key))


class Layers(object):

    def __init__(self, level: 'Level', type_: str, data):
        self.level = level
        self.type = type_
        self.key = data["key"]
        self.pattern: List[List[int]] = [[c for c in l] for l in data["pattern"]]
        self.size = len(self.pattern), len(self.pattern[0])
        self.__random_tab: List[List[float]] = [[random.random() for i in range(self.size[1])] for y in range(self.size[0])]
        self.keys = {}

    def load_asset(self) -> NoReturn:
        for key, value in self.key.items():
            if value == EMPTY:
                self.keys[int(key)] = None
            else:
                # k = Key(key, value)
                self.keys[int(key)] = value
        for value in self.keys.values():
            if value and value not in self.level.struct:
                self.level.struct[value] = structure.parse(value)

    def get_case(self, x: int, y: int) -> int:
        return self.pattern[y][x]

    def render(self, x_start: float, y_start: float, x_end: float, y_end: float
               , display: pygame.Surface, collision: 'col.Collision',
               to_add: List[Tuple[int, Callable[[pygame.Surface], NoReturn]]]):

        x_start_mod: int = (x_start // game.CASE_SIZE) - 5
        y_start_mod: int = (y_start // game.CASE_SIZE) - 5
        x_end_mod: int = (x_end // game.CASE_SIZE) + 8
        y_end_mod: int = (y_end // game.CASE_SIZE) + 8

        to_render = {}

        for a in to_add:
            r_y = a[0] // game.CASE_SIZE - y_start
            if r_y not in to_render:
                to_render[r_y] = [[False, a[1]]]
            else:
                to_render[r_y].append([False, a[1]])

        for x in range(x_start_mod, x_end_mod):
            for y in range(y_start_mod, y_end_mod):
                if x < 0 or x >= self.size[1] or y < 0 or y >= self.size[0]:
                    continue
                key = self.keys[self.get_case(x, y)]
                if key:
                    struct = self.level.struct[key]
                    r_y = y - y_start_mod
                    if r_y not in to_render:
                        to_render[r_y] = [[True, struct, x, y]]
                    else:
                        to_render[r_y].append([True, struct, x, y])

        od = collections.OrderedDict(sorted(to_render.items()))
        for v in od.values():
            for s in v:
                if s[0]:
                    s[1].render(display, s[2] * game.CASE_SIZE - x_start, s[3] * game.CASE_SIZE - y_start, s[2], s[3], self.__random_tab, collision)
                else:
                    s[1](display)


class Level(object):

    def __init__(self, path: str):
        self.path = path
        with open("data/levels/{}.json".format(path), "r", encoding='utf-8') as file:
            data = json.load(file)

        print("pre load lvl {}".format(path))

        if not data:
            raise er.LevelParseError("No data in {}".format(path))

        f = data[FLOOR]
        if not f:
            raise er.LevelParseError("No floor in {}".format(path))
        self.floor: Layers = Layers(self, FLOOR, f)

        l = data[LAYER_1]
        if not l:
            raise er.LevelParseError("No layer_1 in {}".format(path))
        self.layer_1: Layers = Layers(self, LAYER_1, l)

        self.name: str = data["name"] if "name" in data else "undefined"

        s = data["sound"] if "sound" in data else None
        self.sound = pygame.mixer.Sound(f'assets/sound/{s}') if s else None

        if self.layer_1.size != self.floor.size:
            raise er.LevelParseError("Floor and layer haven't same size !! in {}".format(path))

        self.trigger: List[Tuple[str, List[int]]] = []
        if "trigger" in data:
            for tr in data["trigger"]:
                if "id" not in tr:
                    raise er.LevelParseError("Trigger with no id in {}".format(path))
                _id = tr["id"]
                if "loc" not in tr:
                    raise er.TriggerParseError("No loc in trigger id {}".format(_id))
                loc = tr["loc"]
                self.trigger.append((_id, loc))

        self.npc: List['npc.NPC'] = []
        if "npc" in data:
            for np in data["npc"]:
                if "id" not in np:
                    raise er.LevelParseError("Npc with no id in {}".format(path))
                _id = np["id"]
                self.npc.append(npc.load(_id, np))

        self.is_poke_center = ("is_poke_center" in data and data["is_poke_center"])
        if self.is_poke_center:
            self.poke_center_heal_coord = data["poke_heal_coord"]

        # wild : {
        #   TALL_GRASS: [poke, proba, min_lvl, max_lvl]
        # }

        self.wild_pokemon: Dict[str, List[List[int]]] = data["wild_pokemon"] if "wild_pokemon" in data else {}
        self.wild_pokemon_rdm: Dict[str, List[List[int]]] = {}
        self.wild_pokemon_rdm_max: Dict[str, int] = {}
        self.can_cycling: bool = data["can_cycling"] if "can_cycling" in data else False

        self.struct = {}

        for key, p_t in self.wild_pokemon.items():
            li = []
            c = 0
            for p in p_t:
                li.append([c, c + p[1], p[0], p[2], p[3]])
                c += p[1]
            self.wild_pokemon_rdm[key] = li
            self.wild_pokemon_rdm_max[key] = c

    def get_random_wild(self, type_: str) -> Optional[tuple[int, int]]:
        if type_ in self.wild_pokemon_rdm:
            rdm_li = self.wild_pokemon_rdm[type_]
            rdm_max = self.wild_pokemon_rdm_max[type_]
            r = random.random() * rdm_max
            for p_li in rdm_li:
                if p_li[0] <= r <= p_li[1]:
                    return p_li[2], random.randint(p_li[3], p_li[4])
            return None
        else:
            return None

    def __del__(self):
        self.struct.clear()

    def get_translate_name(self) -> str:
        return game.get_game_instance().get_message("levels.{}".format(self.name))

    def npc_render(self, display: pygame.Surface, collision: 'col.Collision') -> NoReturn:
        for np in self.npc:
            collision.add(np.get_triggers_box())
            np.render(display)
            np.tick_render(display)

    def load_trigger(self, x_start: float, y_start: float, x_end: float, y_end: float,
                     cache: 'game.Cache', collision: 'col.Collision'):
        x_start_mod = (x_start // game.CASE_SIZE) - 5
        y_start_mod = (y_start // game.CASE_SIZE) - 5
        x_end_mod = (x_end // game.CASE_SIZE) + 8
        y_end_mod = (y_end // game.CASE_SIZE) + 8

        for tr in self.trigger:
            loc = tr[1]
            if x_start_mod <= loc[0] <= x_end_mod and y_start_mod <= loc[1] <= y_end_mod:
                trigger = cache.get(tr[0])
                collision.add(col.SquaredTriggerCollisionBox(loc[0] * game.CASE_SIZE - x_start,
                                                             loc[1] * game.CASE_SIZE - y_start,
                                                             loc[2] * game.CASE_SIZE - x_start,
                                                             loc[3] * game.CASE_SIZE - y_start, trigger))

    def load_sound(self) -> NoReturn:
        if self.sound:
            sound_manager.MUSIC_CHANNEL.play(self.sound, -1)
        else:
            sound_manager.MUSIC_CHANNEL.stop()

    def load_asset(self, cache: 'game.Cache') -> NoReturn:
        """
        :type cache: game.Cache
        """
        for tr in self.trigger:
            if not cache.have(tr[0]):
                cache.put(tr[0], triggers.load(tr[0]))

