from typing import Dict, Any, Tuple, NoReturn, Callable, List, Union
import math
import pygame
import triggers
import character.npc as char_npc
import pokemon.battle.wild_start as wild_start

# QUARTER_PI = math.pi / 4

# SOUTH = math.pi
# SOUTH_EAST = (math.pi / 4) * 3
# SOUTH_WEST = (math.pi / 4) * 5
# NORTH_EAST = math.pi / 4
# NORTH_WEST = (math.pi / 4) * 7
# NORTH = 0
# WEST = math.pi / 2 + math.pi
# EAST = math.pi / 2
#
# ROTATION = [
#     NORTH,
#     NORTH_EAST,
#     EAST,
#     SOUTH_EAST,
#     SOUTH,
#     SOUTH_WEST,
#     WEST,
#     NORTH_WEST,
# ]

BLOCK_EVENT = "BLOCK"
JUMP_EVENT = "JUMP"
WILD_POKEMON = "WILD_POKEMON"


class CollisionEvent(object):

    def __init__(self, name: str, data:  Dict[str, Any], block=False):
        self.name = name
        self.block = block

    def need_block(self) -> bool:
        return self.block

    def edit_coord(self, x: float, y: float) -> Tuple[float, float]:
        return x, y


class BlockEvent(CollisionEvent):

    def __init__(self, data: Dict[str, Any]):
        super().__init__(BLOCK_EVENT, data, True)


class WildEvent(CollisionEvent):

    def __init__(self, data: Dict[str, Any]):
        super().__init__(WILD_POKEMON, data, False)
        self.type = data["type"]

    def edit_coord(self, x: float, y: float) -> Tuple[float, float]:
        wild_start.player_in_area(self.type)
        return x, y


class JumpEvent(CollisionEvent):

    def __init__(self, data: Dict[str, Any]):
        super().__init__(JUMP_EVENT, data, False)
        self.x: float = data["x"]
        self.y: float = data["y"]

    def edit_coord(self, x: float, y: float) -> Tuple[float, float]:
        return x + self.x, y + self.y


EVENTS: Dict[str, Callable[[Dict[str, Any]], CollisionEvent]]  = {
    BLOCK_EVENT: BlockEvent,
    JUMP_EVENT: JumpEvent,
    WILD_POKEMON: WildEvent
}


class CollisionBox(object):

    def __init__(self):
        pass

    def is_going_on(self, box: 'CollisionBox', offset_x: float, offset_y: float)  -> Tuple[float, float, bool]:
        pass

    def debug_render(self, display: pygame.Surface) -> NoReturn:
        pass


class Vector(object):

    def __init__(self, x: float, y: float):
        self.x: float = x
        self.y: float = y

    def get_angle(self, other: 'Vector'):
        """

       :type other: Vector
       """
        if not isinstance(other, Vector):
            raise ValueError("other is not vector")
        norme_fac = self.norme() * other.norme()
        if norme_fac == 0:
            return 0
        else:
            cos = self.scal(other) / (norme_fac)
        return math.acos(cos)

    def norme(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def scal(self, other: 'Vector') -> float:
        """

        :type other: Vector
        """
        if not isinstance(other, Vector):
            raise ValueError("other is not vector")
        return self.x * other.x + self.y * other.y


NORMAL_VECTOR: 'Vector' = Vector(0, 1)
NORMAL_VECTOR_2: 'Vector' = Vector(1, 0)


class SquaredCollisionBox(CollisionBox):

    def __init__(self, x1: float, y1: float, x2: float, y2: float, event=None):
        super().__init__()
        self.event = event
        self.x1, self.x2 = (x1, x2) if x1 < x2 else (x2, x1)
        self.y1, self.y2 = (y1, y2) if y1 < y2 else (y2, y1)
        self.center = (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2

    def debug_render(self, display: pygame.Surface) -> NoReturn:
        s = pygame.Surface((self.x2 - self.x1, self.y2 - self.y1))
        s.set_alpha(128)
        s.fill((0, 0, 200))
        display.blit(s, (self.x1, self.y1))

    def is_going_on(self, box: 'SquaredCollisionBox', offset_x: float, offset_y: float) -> Union[
        Tuple[float, float, bool], bool]:

        # (box.x1, box.y1)(box.x2, box.y1),
        for side in [((box.x2 + box.x1) / 2, box.y2)]:
            tx = side[0] + offset_x
            ty = side[1] + offset_y
            if self.x1 <= tx <= self.x2 and self.y1 <= ty <= self.y2:
                x_edit = (side[0] - box.x1)
                y_edit = (side[1] - box.y1)

                # vec = Vector(self.center[0] - side[0], self.center[1] - side[1])
                # angle = vec.get_angle(NORMAL_VECTOR)
                # if angle >= QUARTER_PI * 3:
                #     # print("down")
                #     x = (((self.y2 - side[1]) * (self.center[0] - side[0])) / (self.center[1] - self.y2)) + side[0] - x_edit
                #     y = self.y2 - y_edit
                #     return self.apply_event("down", x, y)
                # elif angle <= QUARTER_PI:
                #     # print("up")
                #     x = (((self.y1 - side[1]) * (self.center[0] - side[0])) / (self.center[1] - self.y1)) + side[0] - x_edit
                #     y = self.y1 - y_edit
                #     return self.apply_event("up", x, y)
                # else:
                #     vec = Vector(self.center[0] - side[0], self.center[1] - side[1])
                #     angle = vec.get_angle(NORMAL_VECTOR_2)
                #     if angle <= QUARTER_PI:
                #         x = self.x1 - x_edit
                #         y = (((self.x1 - side[0]) * (self.center[1] - side[1])) / (self.center[0] - self.x1)) + side[1] - y_edit
                #         return self.apply_event("left", x, y)
                #     elif angle >= QUARTER_PI * 3:
                #         x = self.x2 - x_edit
                #         y = (((self.x2 - side[0]) * (self.center[1] - side[1])) / (self.center[0] - self.x2)) + side[1] - y_edit
                #         return self.apply_event("right", x, y)
                if offset_y == offset_x == 0:
                    x = box.x1 + offset_x
                    y = box.y1 + offset_y
                    return self.apply_event("inside", x, y)
                elif offset_x > 0:
                    x = self.x1 - x_edit - 1
                    # y = (((self.x1 - side[0]) * (self.center[1] - side[1])) / (self.center[0] - self.x1)) + side[1] - y_edit
                    y = box.y1 + offset_y
                    return self.apply_event("left", x, y)
                elif offset_x < 0:
                    x = self.x2 - x_edit + 1
                    # y = (((self.x2 - side[0]) * (self.center[1] - side[1])) / (self.center[0] - self.x2)) + side[1] - y_edit
                    y = box.y1 + offset_y
                    return self.apply_event("right", x, y)
                elif offset_y > 0:
                    # x = (((self.y1 - side[1]) * (self.center[0] - side[0])) / (self.center[1] - self.y1)) + side[0] - x_edit
                    x = box.x1 + offset_x
                    y = self.y1 - y_edit - 1
                    return self.apply_event("up", x, y)
                elif offset_y < 0:
                    # x = (((self.y2 - side[1]) * (self.center[0] - side[0])) / (self.center[1] - self.y2)) + side[0] - x_edit
                    x = box.x1 + offset_x
                    y = self.y2 - y_edit + 1
                    return self.apply_event("down", x, y)

        return False

    def apply_event(self, face, x, y) -> Tuple[float, float, bool]:
        if face in self.event or "*" in self.event:
            if face in self.event:
                e = self.event[face]
            else:
                e = self.event["*"]
            if e.need_block():
                return x, y, True

            b = e.edit_coord(x, y)
            return b[0], b[1], (x, y) != b
        return x, y, True


class NPCTriggerCollisionBox(SquaredCollisionBox):

    def __init__(self, x1: float, y1: float, x2: float, y2: float, npc: 'char_npc.NPC'):
        super().__init__(x1, y1, x2, y2)
        self.__npc: 'char_npc.NPC' = npc

    def debug_render(self, display: pygame.Surface) -> NoReturn:
        s = pygame.Surface((self.x2 - self.x1, self.y2 - self.y1))
        s.set_alpha(128)
        s.fill((0, 200, 0))
        display.blit(s, (self.x1, self.y1))

    def apply_event(self, face, x, y) -> Tuple[float, float, bool]:
        self.__npc.trigger((x, y), face)
        return x, y, False


class SquaredTriggerCollisionBox(SquaredCollisionBox):

    def __init__(self, x1: float, y1: float, x2: float, y2: float, tr: 'triggers.Trigger'):

        super().__init__(x1, y1, x2, y2)
        self.tr = tr

    def debug_render(self, display: pygame.Surface) -> NoReturn:

        s = pygame.Surface((self.x2 - self.x1, self.y2 - self.y1))
        s.set_alpha(128)
        s.fill((200, 0, 0))
        display.blit(s, (self.x1, self.y1))

    def apply_event(self, face, x, y) -> Tuple[float, float, bool]:
        e = None
        if face in self.tr.side:
            e = self.tr.side[face]
        elif "*" in self.tr.side:
            e = self.tr.side["*"]
        if e:
            self.tr.trigger(e)
        return x, y, False


class Collision(object):

    def __init__(self):
        self.list: List[CollisionBox] = []

    def get_collision(self, box: CollisionBox, offset_x: float, offset_y: float) -> Tuple[float, float, bool]:

        back = None

        for l in self.list:
            b = l.is_going_on(box, offset_x, offset_y)
            if b and b[2]:
                back = b
        return back

    def debug_render(self, display: pygame.Surface):
        for l in self.list:
            l.debug_render(display)

    def add(self, box: CollisionBox) -> NoReturn:
        self.list.append(box)

    def clear(self) -> NoReturn:
        self.list.clear()
