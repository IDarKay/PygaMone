import displayer
import game_error as er
import json
import game
import collision as co

FLOOR = "floor"
BUILD = "build"
DEFAULT_SIZE = [1, 1]
EMPTY_COLLISION = [0, 0, 0, 0]


class Structure(object):

    def __init__(self, name, data):
        """
        :type name: str
        :type size: list
        :type display: list[displayer.Displayer]
        """
        self.name = name
        self.size = data["size"] if data["size"] else DEFAULT_SIZE
        if not data["display"]:
            raise er.StructureParseError("No display for {}".format(name))

        self.display = [displayer.parse(d, name) for d in data["display"]]
        self.collision = data["collision"] if "collision" in data else EMPTY_COLLISION
        if len(self.collision) != 4:
            raise er.StructureParseError("Invalid collision size ({}) in {} need 4 arg".format(len(self.collision), name))

        self.collision_side = {}

        if "collision_side" in data:
            for key, value in data["collision_side"].items():
                name = value["id"]
                self.collision_side[key] = co.EVENTS[name](value)

        self.have_collision = self.collision != EMPTY_COLLISION

    def get_display(self, random, x, y):
        """

        :rtype: displayer.Displayer
        """
        if len(self.display) == 1:
            return self.display[0]
        v = int(random[x][y] * len(self.display))
        return self.display[v]

    def render(self, screen, x, y, cx, cy, random, collision):
        d = self.get_display(random, cx, cy)
        d.display(screen, x, y)
        if self.have_collision:
            collision.add(co.SquaredCollisionBox(
                x + self.collision[0] * game.CASE_SIZE,
                y + self.collision[1] * game.CASE_SIZE,
                x + self.collision[2] * game.CASE_SIZE,
                y + self.collision[3] * game.CASE_SIZE,
                self.collision_side
            ))


    def is_one_case(self):
        return self.size == [1, 1]

    def __del__(self):
        # safe delete
        self.display.clear()

class BuildStructure(Structure):
    def __init__(self, name, data):
        """

        :type collision: tuple
        """
        super().__init__(name, data)
        # self.collision = collision


class FloorStructure(Structure):
    
    def __init__(self, name, data):
        super().__init__(name, data)


def parse(path):

    with open("data/build/{}.json".format(path), "r", encoding='utf-8') as file:
        data = json.load(file)

    if not data:
        raise er.StructureParseError("No data in {}".format(path))

    # same for the moment
    if data["type"] == FLOOR:
        return FloorStructure(path, data)
    elif data["type"] == BUILD:
        return BuildStructure(path, data)
    else:
        raise er.StructureParseError("No type in {}".format(path))
