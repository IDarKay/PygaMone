import math
import pygame
import triggers

QUARTER_PI = math.pi / 4

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


class CollisionEvent(object):

    def __init__(self, name, data, block=False):
        self.name = name
        self.block = block

    def need_block(self):
        return self.block

    def edit_coord(self, x, y):
        return x, y

class BlockEvent(CollisionEvent):

    def __init__(self, data):
        super().__init__(BLOCK_EVENT, data, True)


class JumpEvent(CollisionEvent):

    def __init__(self, data):
        super().__init__(JUMP_EVENT, data, False)
        self.x = data["x"]
        self.y = data["y"]

    def edit_coord(self, x, y):
        return x + self.x, y + self.y

EVENTS = {
    BLOCK_EVENT: BlockEvent,
    JUMP_EVENT: JumpEvent
}


class CollisionBox(object):

    def __init__(self):
        pass

    def is_going_on(self, x, y, offset_x, offset_y):
        pass


class Vector(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def get_angle(self, other):
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

    def norme(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def scal(self, other):
        """

        :type other: Vector
        """
        if not isinstance(other, Vector):
            raise ValueError("other is not vector")
        return self.x * other.x + self.y * other.y


NORMAL_VECTOR = Vector(0, 1)
NORMAL_VECTOR_2 = Vector(1, 0)


class SquaredCollisionBox(CollisionBox):

    def __init__(self, x1, y1, x2, y2, event=None):
        super().__init__()
        self.event = event
        self.x1, self.x2 = (x1, x2) if x1 < x2 else (x2, x1)
        self.y1, self.y2 = (y1, y2) if y1 < y2 else (y2, y1)
        self.center = (self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2

    def debug_render(self, display):
        """

        :type display: pygame.Surface
        """
        s = pygame.Surface((self.x2 - self.x1, self.y2 - self.y1))
        s.set_alpha(128)
        s.fill((0, 0, 200))
        display.blit(s, (self.x1, self.y1))

    def is_going_on(self, box, offset_x, offset_y):
        """

        :type box: SquaredCollisionBox
        """
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
                    x = self.x1 - x_edit
                    # y = (((self.x1 - side[0]) * (self.center[1] - side[1])) / (self.center[0] - self.x1)) + side[1] - y_edit
                    y = box.y1 + offset_y
                    return self.apply_event("left", x, y)
                elif offset_x < 0:
                    x = self.x2 - x_edit
                    # y = (((self.x2 - side[0]) * (self.center[1] - side[1])) / (self.center[0] - self.x2)) + side[1] - y_edit
                    y = box.y1 + offset_y
                    return self.apply_event("right", x, y)
                elif offset_y > 0:
                    # x = (((self.y1 - side[1]) * (self.center[0] - side[0])) / (self.center[1] - self.y1)) + side[0] - x_edit
                    x = box.x1 + offset_x
                    y = self.y1 - y_edit
                    return self.apply_event("up", x, y)
                elif offset_y < 0:
                    # x = (((self.y2 - side[1]) * (self.center[0] - side[0])) / (self.center[1] - self.y2)) + side[0] - x_edit
                    x = box.x1 + offset_x
                    y = self.y2 - y_edit
                    return self.apply_event("down", x, y)

        return False

    def apply_event(self, face, x, y):
        if face in self.event:
            e = self.event[face]
            if e.need_block():
                return x, y, True
            b = e.edit_coord(x, y)
            return b[0], b[1], True
        return x, y, True


class NPCTriggerCollisionBox(SquaredCollisionBox):

    def __init__(self, x1, y1, x2, y2, npc):
        """

        :type npc: character.npc.NPC
        """
        super().__init__(x1, y1, x2, y2)
        self.npc = npc

    def debug_render(self, display):
        """

        :type display: pygame.Surface
        """
        s = pygame.Surface((self.x2 - self.x1, self.y2 - self.y1))
        s.set_alpha(128)
        s.fill((0, 200, 0))
        display.blit(s, (self.x1, self.y1))

    def apply_event(self, face, x, y):
        self.npc.trigger((x, y), face)

class SquaredTriggerCollisionBox(SquaredCollisionBox):

    def __init__(self, x1, y1, x2, y2, tr):
        """

        :type tr: triggers.Trigger
        """
        super().__init__(x1, y1, x2, y2)
        self.tr = tr

    def debug_render(self, display):
        """

        :type display: pygame.Surface
        """
        s = pygame.Surface((self.x2 - self.x1, self.y2 - self.y1))
        s.set_alpha(128)
        s.fill((200, 0, 0))
        display.blit(s, (self.x1, self.y1))

    def apply_event(self, face, x, y):
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
        self.list = []

    def get_collision(self, box, offset_x, offset_y):

        back = None

        for l in self.list:
            b = l.is_going_on(box, offset_x, offset_y)
            if b and b[2]:
                back = b
        return back

    def debug_render(self, display):
        for l in self.list:
            l.debug_render(display)

    def add(self, box):
        """

        :type box: CollisionBox
        """
        self.list.append(box)

    def clear(self):
        self.list.clear()
