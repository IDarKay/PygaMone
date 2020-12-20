from typing import Dict, Any, Tuple, NoReturn, Callable, List
import displayer
import game_error as er
import json
import game
import pygame
import collision as co

FLOOR = "floor"
BUILD = "build"
DEFAULT_SIZE = [1, 1]
EMPTY_COLLISION = [0, 0, 0, 0]


class Structure(object):

    def __init__(self, name: str, data: Dict[str, Any]):
        self.name: str = name
        if not data["display"]:
            raise er.StructureParseError("No display for {}".format(name))

        self.display: List['displayer.Displayer'] = [displayer.parse(d, name) for d in data["display"]]
        self.collision: List[int] = data["collision"] if "collision" in data else EMPTY_COLLISION
        if len(self.collision) != 4:
            raise er.StructureParseError("Invalid collision size ({}) in {} need 4 arg".format(len(self.collision), name))

        self.collision_side: Dict[str, 'co.CollisionEvent'] = {}

        if "collision_side" in data:
            for key, value in data["collision_side"].items():
                name = value["id"]
                self.collision_side[key] = co.EVENTS[name](value)

        self.have_collision: bool = self.collision != EMPTY_COLLISION

    def get_display(self, random: List[List[int]], x: int, y: int) -> 'displayer.Displayer':

        if len(self.display) == 1:
            return self.display[0]
        v = int(random[y][x] * len(self.display))
        return self.display[v]

    def render(self, screen: pygame.Surface, x: int, y: int, cx: int, cy: int,
               random: List[List[int]], collision: 'co.Collision') -> NoReturn:
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

    def __del__(self):
        # safe delete
        self.display.clear()

def parse(path: str):

    with open("data/build/{}.json".format(path), "r", encoding='utf-8') as file:
        data = json.load(file)

    if not data:
        raise er.StructureParseError("No data in {}".format(path))

    # same for the moment
    return Structure(path, data)
