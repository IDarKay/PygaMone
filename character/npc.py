from typing import Dict, Any, Tuple, NoReturn, Callable, Optional
import utils
import character as char
import character.player as char_p
import pygame
import game_error as err
import collision
import game
import hud.hud as hud
import sound_manager
import utils
import sounds

class NPC(char.character.Character):

    #    USE DATA:
    #    pos_x => x pos of npc (int) no default
    #    pos_y => y pos of npc (int) no default

    def __init__(self, data: Dict[str, Any], size: Tuple[int, int]):
        pos = NPC.get_args(data, "pos_x"), NPC.get_args(data, "pos_y")
        super().__init__(pos, size)

    def get_triggers_box(self):
        raise RuntimeError("get_triggers ne to be redefine")

    def get_relative_trigger(self, box_size: tuple[int, int],
                             relative: Tuple[int, int]) -> 'collision.NPCTriggerCollisionBox':
        npc_box = self.get_box()

        s_x = npc_box.x1 + relative[0]
        s_y = npc_box.y1 + relative[1]

        return collision.NPCTriggerCollisionBox(s_x, s_y, s_x + box_size[0], s_y + box_size[1], self)

    def trigger(self, pos: Tuple[int, int], face: str) -> NoReturn:
        pass

    def tick_render(self, display: pygame.Surface) -> NoReturn:
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
    RELATIVE = (
        (15, -20),
        (30, -20),
        (15, -10),
        (30, -10),
        (15, 0),
        (30, 0)

    )

    #    USE DATA:
    #    heal_machine => pos of heal machine lis[int, int, int, int] (loc in case) no default
    #    facing => facing of npc 0 = top 1 = left 2 = down 3 = right default (0)a
    #    heal_facing => facing of npc when heal pokemon  0 = top 1 = left 2 = down 3 = right default (0)

    def __init__(self, data: Dict[str, Any]):
        super().__init__(data, (38, 50))
        self.__facing = utils.min_max(0, NPC.get_args(data, "facing", 0, int), 3)
        heal_facing = utils.min_max(0, NPC.get_args(data, "heal_facing", 0, int), 3)
        self.__heal_machine = NPC.get_args(data, "heal_machine", type_check=list)
        self.__heal_machine = self.__heal_machine[0] * game.CASE_SIZE, self.__heal_machine[1] * game.CASE_SIZE

        self.facing_image = utils.get_part_i(char.character.NPC_IMAGE, JoyNPC.IMAGE_LOC[self.__facing], (38, 50))
        self.__heal_facing_image = utils.get_part_i(char.character.NPC_IMAGE, JoyNPC.IMAGE_LOC[heal_facing], (38, 50))
        # 0 nothing, 1 talk
        self.__status = 0
        self.__action: Optional[int] = None
        self.__image_to_show: pygame.Surface = self.facing_image
        self.__player: 'char_p.Player' = game.game_instance.player
        self.__glow = pygame.Surface((16, 16), pygame.SRCALPHA)
        self.__glow.set_alpha(200)
        # pygame.draw.rect(self.__glow, (33, 191, 62), pygame.Rect(0, 0, 16, 16), border_radius=4)
        pygame.draw.circle(self.__glow, (33, 191, 62), (8, 8), 8, 1)
        self.have_start_song = False

    def get_image(self) -> pygame.Surface:
        return self.__image_to_show

    def get_triggers_box(self) -> 'collision.NPCTriggerCollisionBox':
        return self.get_relative_trigger((game.CASE_SIZE, game.CASE_SIZE), JoyNPC.BOX[self.__facing])

    def trigger(self, pos: Tuple[int, int], face: str) -> NoReturn:
        player = game.game_instance.player
        if player.is_action_press and self.__status == 0:
            yes = game.game_instance.get_message("yes")
            no = game.game_instance.get_message("no")
            dialog = hud.QuestionDialog("dialog.poke_center", self.talk_callback, (yes, no), speed_skip=True,
                                        need_morph_text=True)
            player.open_dialogue(dialog, 1000, over=False)

    def talk_callback(self, value, index) -> NoReturn:
        player = game.game_instance.player
        if index == 1:
            player.open_dialogue(hud.Dialog("dialog.poke_center_no", speed_skip=True, need_morph_text=True), over=True)
        else:
            self.have_start_song = False
            self.__action = utils.current_milli_time()
            self.__player.open_dialogue(hud.Dialog("dialog.poke_center_yes", need_morph_text=True, none_skip=True),
                                        over=True)
            self.__player.heal_team()
        return True

    def get_where_pose(self, i: int) -> Tuple[int, int]:
        return self.__heal_machine[0] - game.came_scroll[0] + JoyNPC.RELATIVE[i][0], \
               self.__heal_machine[1] - game.came_scroll[1] + JoyNPC.RELATIVE[i][1]

    def tick_render(self, display: pygame.Surface) -> NoReturn:
        if self.__action:
            dif_t = utils.current_milli_time() - self.__action
            if dif_t > 1000:
                dif_t -= 1000
                self.__image_to_show = self.__heal_facing_image
                nb_poke = self.__player.get_non_null_team_number()
                nb_poke_to_show = dif_t // 1000
                for i in range(min(nb_poke, nb_poke_to_show)):
                    display.blit(self.__player.team[i].poke_ball.small_image, self.get_where_pose(i))
                    if nb_poke_to_show > nb_poke and dif_t % 400 > 200:
                        display.blit(self.__glow, self.get_where_pose(i))
                if nb_poke_to_show > nb_poke:
                    if not self.have_start_song:
                        self.have_start_song = True
                        sound_manager.start_in_first_empty_taunt(pygame.mixer.Sound(sounds.HEAL.path))
                    if dif_t - 1000 * nb_poke > 3000:
                        self.__image_to_show = self.facing_image
                        self.__action = None
                        self.__player.open_dialogue(
                            hud.Dialog("dialog.poke_center_end", speed_skip=True, need_morph_text=True), over=True)


NPC_list: Dict[str, Callable[[Dict[str, Any]], NPC]] = {
    "JOY": JoyNPC
}


def load(_id: str, data: Dict[str, Any]) -> NPC:
    return NPC_list[_id](data)
