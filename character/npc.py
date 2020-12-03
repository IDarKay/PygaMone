from typing import Dict, Any, Tuple, NoReturn, Callable
from utils import min_max, get_part_i
import character as char
import pygame
import game_error as err
import collision
import game
import hud.hud as hud


class NPC(char.character.Character):

    #    USE DATA:
    #    pos_x => x pos of npc (int) no default
    #    pos_y => y pos of npc (int) no default

    def __init__(self, data: Dict[str, Any], size: Tuple[int, int]):
        pos = NPC.get_args(data, "pos_x"), NPC.get_args(data, "pos_y")
        super().__init__(pos, size)

    def get_triggers_box(self):
        raise RuntimeError("get_triggers ne to be redefine")

    def get_relative_trigger(self, box_size: Tuple[int, int], relative: Tuple[int, int]) -> 'collision.NPCTriggerCollisionBox':
        npc_box = self.get_box()

        s_x = npc_box.x1 + relative[0]
        s_y = npc_box.y1 + relative[1]

        return collision.NPCTriggerCollisionBox(s_x, s_y, s_x + box_size[0], s_y + box_size[1], self)

    def trigger(self, pos: Tuple[int, int], face: str) -> NoReturn:
        pass

    def tick(self) -> NoReturn:
        # todo:
        pass

    @staticmethod
    def get_args(data, key, default=None, type_check=None):
        value = None
        if default:
            value = data[key] if key in data else default
        else:
            if key not in data:
                raise err.NPCParseError("No {} value for a npc !".format(key))
            value = data[key]
        if type_check:
            if not isinstance(value, type_check):
                raise err.NPCParseError("Invalid var type for {} need be {}".format(key, type_check))
        return value


class JoyNPC(NPC):

    IMAGE_LOC = ((34, 25, 53, 50), (54, 25, 73, 50), (34, 0, 53, 25), (54, 0, 73, 25))
    BOX = ((0, -64), (-64, 0), (0, 64), (64, 0))

    #    USE DATA:
    #    heal_machine => pos of heal machine lis[int, int, int, int] (loc in case) no default
    #    facing => facing of npc 0 = top 1 = left 2 = down 3 = right default (0)a
    #    heal_facing => facing of npc when heal pokemon  0 = top 1 = left 2 = down 3 = right default (0)

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data, (38, 50))
        self.__facing = min_max(0, NPC.get_args(data, "facing", 0, int), 3)
        heal_facing = min_max(0, NPC.get_args(data, "heal_facing", 0, int), 3)
        self.__heal_machine = NPC.get_args(data, "heal_machine", type_check=list)

        self.facing_image = get_part_i(char.character.NPC_IMAGE, JoyNPC.IMAGE_LOC[self.__facing], (38, 50))
        self.__heal_facing_image = get_part_i(char.character.NPC_IMAGE, JoyNPC.IMAGE_LOC[heal_facing], (38, 50))
        # 0 nothing, 1 talk
        self.__status = 0

    def get_image(self) -> pygame.Surface:
        return self.facing_image

    def get_triggers_box(self) -> 'collision.NPCTriggerCollisionBox':
        return self.get_relative_trigger((game.CASE_SIZE, game.CASE_SIZE), JoyNPC.BOX[self.__facing])

    def trigger(self, pos: Tuple[int, int], face: str) -> NoReturn:
        player = game.game_instance.player
        if player.is_action_press and self.__status == 0:
            yes = game.game_instance.get_message("yes")
            no = game.game_instance.get_message("no")
            dialog = hud.QuestionDialog("dialog.poke_center", self.talk_callback, (yes, no), speed_skip=True, need_morph_text=True)
            player.open_dialogue(dialog, 1000)

    def talk_callback(self, value, index) -> NoReturn:
        player = game.game_instance.player
        if index == 1:
            player.open_dialogue(hud.Dialog("dialog.poke_center_no", speed_skip=True, need_morph_text=True), over=True)
        return True


NPC_list: Dict[str, Callable[[Dict[str, Any]], NPC]] = {
    "JOY": JoyNPC
}


def load(_id: str, data: Dict[str, Any]) -> NPC:
    return NPC_list[_id](data)
