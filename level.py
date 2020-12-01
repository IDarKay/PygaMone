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

EMPTY = "EMPTY"
FLOOR = "floor"
LAYER_1 = "layer_1"


class Key(object):

    def __init__(self, key, data):
        self.key = key
        self.ref = structure.parse(data["ref"])
        if not self.ref:
            raise er.LevelParseError("No ref for a layer with key {}".format(key))


class Layers(object):

    def __init__(self, type, data):
        self.type = type
        self.key = data["key"]
        self.pattern = [[c for c in l] for l in data["pattern"]]
        self.size = len(self.pattern), len(self.pattern[0])
        self.random_tab = [[random.random() for i in range(self.size[1])] for y in range(self.size[0])]

    def load_asset(self, cache):
        """

        :type cache: game.Cache
        """
        for key, value in self.key.items():
            if value["ref"] == EMPTY:
                cache.put(key, None)
            else:
                cache.put(key, Key(key, value))

    def get_case(self, x, y):
        return self.pattern[y][x]

    def render(self, x_start, y_start, x_end, y_end, cache, display, collision, to_add):
        """

        :type display: pygame.Surface
        :type cache: game.Cache
        """
        x_start_mod = (x_start // game.CASE_SIZE) - 5
        y_start_mod = (y_start // game.CASE_SIZE) - 5
        x_end_mod = (x_end // game.CASE_SIZE) + 8
        y_end_mod = (y_end // game.CASE_SIZE) + 8

        to_render = {}

        for a in to_add:
            r_y = a[0] // game.CASE_SIZE - y_start
            if r_y not in to_render:
                to_render[r_y] = [[False, a[1]]]
            else:
                to_render[r_y].append([False, a[1]])

        for x in range(x_start_mod, x_end_mod):
            for y in range(y_start_mod, y_end_mod):
                if x < 0 or x >= self.size[1] or y < 0 or y >= self.size[0 ]:
                    continue
                key = cache.get(self.get_case(x, y))
                if key:
                    r_y = y - y_start_mod
                    if r_y not in to_render:
                        to_render[r_y] = [[True, key.ref, x, y]]
                    else:
                        to_render[r_y].append([True, key.ref, x, y])

        od = collections.OrderedDict(sorted(to_render.items()))
        for v in od.values():
            for s in v:
                # print("struct: ", s[0].name,  "x: ", (s[1] - x_start_mod) * game.CASE_SIZE, "y: ", (s[2] - y_start_mod) * game.CASE_SIZE)
                if s[0]:
                    s[1].render(display, s[2] * game.CASE_SIZE - x_start, s[3] * game.CASE_SIZE - y_start, s[2], s[3], self.random_tab, collision)
                else:
                    s[1](display)


class Level(object):

    def __init__(self, path):
        self.path = path
        with open("data/levels/{}.json".format(path), "r", encoding='utf-8') as file:
            data = json.load(file)

        print("pre load lvl {}".format(path))

        if not data:
            raise er.LevelParseError("No data in {}".format(path))

        f = data[FLOOR]
        if not f:
            raise er.LevelParseError("No floor in {}".format(path))
        self.floor = Layers(FLOOR, f)

        l = data[LAYER_1]
        if not l:
            raise er.LevelParseError("No layer_1 in {}".format(path))
        self.layer_1 = Layers(LAYER_1, l)

        if self.layer_1.size != self.floor.size:
            raise er.LevelParseError("Floor and layer haven't same size !! in {}".format(path))

        self.trigger = []
        if "trigger" in data:
            for tr in data["trigger"]:
                if "id" not in tr:
                    raise er.LevelParseError("Trigger with no id in {}".format(path))
                _id = tr["id"]
                if "loc" not in tr:
                    raise er.TriggerParseError("No loc in trigger id {}".format(_id))
                loc = tr["loc"]
                self.trigger.append((_id, loc))

        self.npc = []
        if "npc" in data:
            for np in data["npc"]:
                if "id" not in np:
                    raise er.LevelParseError("Npc with no id in {}".format(path))
                _id = np["id"]
                self.npc.append(npc.load(_id, np))


    def npc_render(self, display, collision):
        for np in self.npc:
            collision.add(np.get_triggers_box())
            np.render(display)

    def load_trigger(self, x_start, y_start, x_end, y_end, cache, collision):
        """
        :type cache: game.Cache
        """
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

    def load_asset(self, cache):
        """
        :type cache: game.Cache
        """
        for tr in self.trigger:
            if not cache.have(tr[0]):
                cache.put(tr[0], triggers.load(tr[0]))